"""
图片抗检测处理 - 相册选择版
功能：从相册选择图片（支持多选），处理后自动保存回系统相册
"""

import os
import json
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Rectangle
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO

# Android 专用导入
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass, cast
    import android

    # 请求运行时权限
    perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
    # Android 13+ 需要单独的媒体权限
    try:
        from android.permissions import Permission as P
        if hasattr(P, 'READ_MEDIA_IMAGES'):
            perms.append(P.READ_MEDIA_IMAGES)
    except:
        pass
    request_permissions(perms)

    # Java类
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Activity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    Bitmap = autoclass('android.graphics.Bitmap')
    ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
    File = autoclass('java.io.File')
    FileOutputStream = autoclass('java.io.FileOutputStream')
    ContentValues = autoclass('android.content.ContentValues')
    Context = autoclass('android.content.Context')

else:
    # 桌面环境模拟
    from plyer import filechooser

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "flip_h": False,
    "flip_v": False,
    "color_jitter": False,
    "add_border": False,
    "png_recode": False,
    "max_angle": 0.6,
    "quality": 95
}


class AntiDedupApp(App):
    def build(self):
        self.load_settings()
        self.selected_images = []  # 存储选中的图片路径 (Android上为Uri字符串)
        self.processing = False

        # 主布局
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 标题
        title = Label(text='图片抗检测处理', size_hint=(1, 0.08), font_size='20sp')
        root.add_widget(title)

        # 设置区域（滚动）
        scroll = ScrollView(size_hint=(1, 0.5))
        settings_grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        settings_grid.bind(minimum_height=settings_grid.setter('height'))

        self.settings_widgets = {}
        for key in DEFAULT_SETTINGS:
            if key in ['max_angle', 'quality']:
                continue
            label = Label(text=key.replace('_', ' ').capitalize(), halign='left', size_hint_x=0.6)
            btn = Button(text='OFF' if not self.cfg[key] else 'ON', size_hint_x=0.4)
            btn.bind(on_press=lambda btn, k=key: self.toggle_setting(k, btn))
            settings_grid.add_widget(label)
            settings_grid.add_widget(btn)
            self.settings_widgets[key] = btn

        # 角度滑块
        angle_label = Label(text='Max angle (deg)', size_hint_x=0.6)
        from kivy.uix.slider import Slider
        angle_slider = Slider(min=0, max=2, value=self.cfg['max_angle'], step=0.05, size_hint_x=0.4)
        angle_slider.bind(value=self.on_angle_change)
        settings_grid.add_widget(angle_label)
        settings_grid.add_widget(angle_slider)

        # 质量滑块
        quality_label = Label(text='JPEG quality', size_hint_x=0.6)
        quality_slider = Slider(min=50, max=100, value=self.cfg['quality'], step=1, size_hint_x=0.4)
        quality_slider.bind(value=self.on_quality_change)
        settings_grid.add_widget(quality_label)
        settings_grid.add_widget(quality_slider)

        scroll.add_widget(settings_grid)
        root.add_widget(scroll)

        # 图片选择区域
        sel_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        select_btn = Button(text='从相册选择 (多选)')
        select_btn.bind(on_press=self.select_images)
        clear_btn = Button(text='清空列表')
        clear_btn.bind(on_press=self.clear_selection)
        sel_layout.add_widget(select_btn)
        sel_layout.add_widget(clear_btn)
        root.add_widget(sel_layout)

        # 已选图片列表（滚动）
        self.list_container = ScrollView(size_hint=(1, 0.2))
        self.thumb_grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.thumb_grid.bind(minimum_height=self.thumb_grid.setter('height'))
        self.list_container.add_widget(self.thumb_grid)
        root.add_widget(self.list_container)

        # 处理按钮
        process_btn = Button(text='开始处理', size_hint=(1, 0.08))
        process_btn.bind(on_press=self.start_processing)
        root.add_widget(process_btn)

        # 进度条和状态
        self.progress = ProgressBar(max=100, size_hint=(1, 0.05), value=0)
        root.add_widget(self.progress)
        self.status_label = Label(text='等待选择图片...', size_hint=(1, 0.08), halign='center')
        root.add_widget(self.status_label)

        return root

    # ---------- 设置相关 ----------
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    saved = json.load(f)
                self.cfg = {**DEFAULT_SETTINGS, **saved}
            except:
                self.cfg = DEFAULT_SETTINGS.copy()
        else:
            self.cfg = DEFAULT_SETTINGS.copy()
        self.save_settings()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.cfg, f, indent=2)
        except:
            pass

    def toggle_setting(self, key, btn):
        self.cfg[key] = not self.cfg[key]
        btn.text = 'ON' if self.cfg[key] else 'OFF'
        self.save_settings()

    def on_angle_change(self, instance, value):
        self.cfg['max_angle'] = round(value, 2)
        self.save_settings()

    def on_quality_change(self, instance, value):
        self.cfg['quality'] = int(value)
        self.save_settings()

    # ---------- 相册选择（支持多选） ----------
    def select_images(self, instance):
        if platform == 'android':
            # 使用 Intent 启动系统相册，支持多选
            intent = Intent()
            intent.setAction(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
            activity.bind(on_activity_result=self.on_activity_result)
            activity.startActivityForResult(intent, 0x1234)
        else:
            # 桌面环境 fallback
            filechooser.open_files(on_selection=self.on_files_selected, multiple=True)

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 0x1234 and resultCode == -1:  # RESULT_OK
            if intent.getData() is not None:
                # 单张
                uri = intent.getData()
                self.add_image_uri(uri)
            else:
                # 多张
                clipData = intent.getClipData()
                if clipData is not None:
                    for i in range(clipData.getItemCount()):
                        uri = clipData.getItemAt(i).getUri()
                        self.add_image_uri(uri)
        activity.unbind(on_activity_result=self.on_activity_result)

    def add_image_uri(self, uri):
        uri_str = str(uri)
        if uri_str not in self.selected_images:
            self.selected_images.append(uri_str)
            # 显示缩略图（简化：显示文本）
            img_box = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            filename = uri_str.split('/')[-1][:15]
            lbl = Label(text=filename, size_hint_y=0.3, font_size='12sp')
            img_box.add_widget(lbl)
            # 也可以添加删除按钮
            self.thumb_grid.add_widget(img_box)
        self.update_status()

    def clear_selection(self, instance):
        self.selected_images.clear()
        self.thumb_grid.clear_widgets()
        self.update_status()

    def on_files_selected(self, selection):
        if selection:
            for f in selection:
                if f not in self.selected_images:
                    self.selected_images.append(f)
                    self.thumb_grid.add_widget(Label(text=os.path.basename(f), size_hint_y=None, height=40))
            self.update_status()

    def update_status(self):
        self.status_label.text = f"已选择 {len(self.selected_images)} 张图片"

    # ---------- 处理图片 ----------
    def start_processing(self, instance):
        if self.processing:
            return
        if not self.selected_images:
            self.status_label.text = "请先选择图片！"
            return
        self.processing = True
        self.progress.value = 0
        Clock.schedule_once(lambda dt: self.process_all(), 0)

    def process_all(self):
        total = len(self.selected_images)
        success = 0
        for i, img_src in enumerate(self.selected_images):
            self.status_label.text = f"处理中 {i+1}/{total}"
            try:
                if platform == 'android':
                    # 从 Uri 获取输入流并转为 PIL Image
                    uri = Uri.parse(img_src)
                    context = Activity.getApplicationContext()
                    input_stream = context.getContentResolver().openInputStream(uri)
                    pil_img = Image.open(input_stream).convert('RGB')
                    input_stream.close()
                else:
                    pil_img = Image.open(img_src).convert('RGB')

                # 处理图片
                processed = self.process_single_image(pil_img)

                # 保存到系统相册
                self.save_to_gallery(processed, f"processed_{i}_{random.randint(1000,9999)}.jpg")

                success += 1
            except Exception as e:
                print(f"处理失败: {e}")
                self.status_label.text = f"处理失败: {img_src}"
            self.progress.value = (i+1)/total * 100
        self.processing = False
        self.status_label.text = f"处理完成！成功 {success}/{total} 张，已保存到相册。"
        self.progress.value = 0

    def process_single_image(self, img):
        if self.cfg["flip_h"]:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.cfg["flip_v"]:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        if self.cfg["color_jitter"]:
            img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95, 1.05))
            img = ImageEnhance.Contrast(img).enhance(random.uniform(0.95, 1.05))
            img = ImageEnhance.Color(img).enhance(random.uniform(0.95, 1.05))

        angle = random.uniform(-self.cfg["max_angle"], self.cfg["max_angle"])
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255,255,255))

        crop_px = random.randint(1, 3)
        w, h = img.size
        img = img.crop((crop_px, crop_px, w - crop_px, h - crop_px))

        scale = random.uniform(0.995, 1.005)
        new_w, new_h = int(img.width * scale), int(img.height * scale)
        img = img.resize((new_w, new_h), resample=Image.LANCZOS)

        # 添加噪点
        pixels = img.load()
        noise_strength = random.randint(1, 2)
        for i in range(img.width):
            for j in range(img.height):
                r, g, b = pixels[i, j]
                noise = random.randint(-noise_strength, noise_strength)
                r = min(255, max(0, r + noise))
                g = min(255, max(0, g + noise))
                b = min(255, max(0, b + noise))
                pixels[i, j] = (r, g, b)

        if self.cfg["add_border"]:
            border_color = random.choice([(255,255,255), (0,0,0)])
            img = ImageOps.expand(img, border=1, fill=border_color)

        if self.cfg["png_recode"]:
            temp_png = BytesIO()
            img.save(temp_png, format='PNG')
            temp_png.seek(0)
            img = Image.open(temp_png).convert('RGB')

        # 输出为 JPEG 字节流
        out = BytesIO()
        img.save(out, format='JPEG', quality=self.cfg["quality"], optimize=True)
        out.seek(0)
        return out

    def save_to_gallery(self, image_bytes_io, filename):
        """将处理后的图片保存到系统相册"""
        if platform == 'android':
            contentResolver = Activity.getApplicationContext().getContentResolver()
            # 使用 MediaStore 插入
            values = ContentValues()
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
            values.put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            # Android 10+ 使用 RELATIVE_PATH
            if hasattr(MediaStore.MediaColumns, 'RELATIVE_PATH'):
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/图片抗检测")
            else:
                # 老版本保存到默认 Pictures
                pass
            uri = contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            if uri:
                os = contentResolver.openOutputStream(uri)
                os.write(image_bytes_io.getvalue())
                os.close()
        else:
            # 桌面测试保存到当前目录
            with open(filename, 'wb') as f:
                f.write(image_bytes_io.getvalue())


if __name__ == '__main__':
    AntiDedupApp().run()
