"""
图片抗检测处理 - 中文版
日志输出到 /storage/emulated/0/MT2/antidedup.log
"""

import os
import json
import random
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.text import LabelBase
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO

if platform == 'android':
    LOG_DIR = "/storage/emulated/0/MT2"
    LOG_FILE = os.path.join(LOG_DIR, "antidedup.log")
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except:
        pass
else:
    LOG_FILE = "antidedup.log"

def log_error(msg):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{msg}\n")
    except:
        pass

if platform == 'android':
    try:
        LabelBase.register(name='Chinese', fn_regular='/system/fonts/DroidSansFallback.ttf')
        default_font = 'Chinese'
    except:
        default_font = 'Roboto'
else:
    default_font = 'Roboto'

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass
    perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
    try:
        from android.permissions import Permission as P
        if hasattr(P, 'READ_MEDIA_IMAGES'):
            perms.append(P.READ_MEDIA_IMAGES)
    except:
        pass
    log_error("请求权限: " + str(perms))
    request_permissions(perms)
    log_error("权限已授予")
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Activity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    ContentValues = autoclass('android.content.ContentValues')
else:
    from plyer import filechooser

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "flip_h": False,
    "flip_v": False,
    "color_jitter": True,
    "add_border": False,
    "png_recode": False,
    "max_angle": 0.6,
    "quality": 92
}

class AntiDedupApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_uris = []
        self.processing = False

    def build(self):
        self.load_settings()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        title = Label(text='图片抗检测处理', font_size='28sp', size_hint=(1, 0.15),
                      color=(0.2, 0.6, 0.8, 1), font_name=default_font)
        layout.add_widget(title)
        self.status_label = Label(text='未选择图片', font_size='18sp',
                                  size_hint=(1, 0.1), color=(0.3, 0.3, 0.3, 1),
                                  font_name=default_font)
        layout.add_widget(self.status_label)
        self.select_btn = Button(text='📷 从相册选择 (可多选)', font_size='20sp',
                                 size_hint=(1, 0.15), background_normal='',
                                 background_color=(0.2, 0.6, 0.8, 1), color=(1,1,1,1))
        self.select_btn.bind(on_press=self.select_images)
        layout.add_widget(self.select_btn)
        self.process_btn = Button(text='🚀 开始处理图片', font_size='20sp',
                                  size_hint=(1, 0.15), background_normal='',
                                  background_color=(0.1, 0.7, 0.3, 1), color=(1,1,1,1))
        self.process_btn.bind(on_press=self.start_processing)
        layout.add_widget(self.process_btn)
        self.progress = ProgressBar(max=100, size_hint=(1, 0.05), value=0)
        layout.add_widget(self.progress)
        info_text = (f"设置: 水平翻转={self.cfg['flip_h']}, 色彩抖动={self.cfg['color_jitter']}, "
                     f"最大旋转={self.cfg['max_angle']}°, 画质={self.cfg['quality']}%")
        self.info_label = Label(text=info_text, font_size='14sp', size_hint=(1, 0.1),
                                color=(0.5,0.5,0.5,1), font_name=default_font)
        layout.add_widget(self.info_label)
        log_error("界面构建完成")
        return layout

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                self.cfg = {**DEFAULT_SETTINGS, **saved}
            except Exception as e:
                log_error(f"加载设置失败: {e}")
                self.cfg = DEFAULT_SETTINGS.copy()
        else:
            self.cfg = DEFAULT_SETTINGS.copy()
        self.save_settings()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"保存设置失败: {e}")

    def select_images(self, instance):
        log_error("点击选择图片按钮")
        if platform == 'android':
            try:
                intent = Intent()
                intent.setAction(Intent.ACTION_GET_CONTENT)
                intent.setType("image/*")
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
                activity.bind(on_activity_result=self.on_activity_result)
                activity.startActivityForResult(intent, 0x1234)
                log_error("已启动相册选择")
            except Exception as e:
                log_error(f"启动相册失败: {e}\n{traceback.format_exc()}")
                self.status_label.text = f"打开相册失败: {str(e)}"
        else:
            filechooser.open_files(on_selection=self.on_files_selected, multiple=True)

    def on_activity_result(self, requestCode, resultCode, intent):
        log_error(f"收到返回结果: requestCode={requestCode}, resultCode={resultCode}")
        if requestCode == 0x1234 and resultCode == -1:
            self.selected_uris.clear()
            try:
                if intent.getData() is not None:
                    self.selected_uris.append(str(intent.getData()))
                else:
                    clipData = intent.getClipData()
                    if clipData is not None:
                        for i in range(clipData.getItemCount()):
                            uri = clipData.getItemAt(i).getUri()
                            self.selected_uris.append(str(uri))
                count = len(self.selected_uris)
                self.status_label.text = f'已选择 {count} 张图片'
                log_error(f"选择了 {count} 张图片")
            except Exception as e:
                log_error(f"处理返回结果失败: {e}\n{traceback.format_exc()}")
                self.status_label.text = "读取相册结果失败，请重试"
        else:
            log_error(f"相册选择取消或失败: resultCode={resultCode}")
            self.status_label.text = "未选择图片"
        activity.unbind(on_activity_result=self.on_activity_result)

    def on_files_selected(self, selection):
        self.selected_uris = selection if selection else []
        self.status_label.text = f'已选择 {len(self.selected_uris)} 张图片'

    def start_processing(self, instance):
        log_error("点击开始处理按钮")
        if self.processing:
            return
        if not self.selected_uris:
            self.status_label.text = '请先选择图片！'
            return
        self.processing = True
        self.progress.value = 0
        Clock.schedule_once(lambda dt: self.process_all(), 0)

    def process_all(self):
        total = len(self.selected_uris)
        success = 0
        for idx, img_src in enumerate(self.selected_uris):
            self.status_label.text = f'处理中 {idx+1}/{total}'
            try:
                if platform == 'android':
                    uri = Uri.parse(img_src)
                    context = Activity.getApplicationContext()
                    input_stream = context.getContentResolver().openInputStream(uri)
                    pil_img = Image.open(input_stream).convert('RGB')
                    input_stream.close()
                else:
                    pil_img = Image.open(img_src).convert('RGB')
                processed = self.process_single_image(pil_img)
                self.save_to_gallery(processed)
                success += 1
                log_error(f"处理成功: {img_src}")
            except Exception as e:
                log_error(f"处理失败 {img_src}: {e}\n{traceback.format_exc()}")
            self.progress.value = (idx+1)/total * 100
        self.processing = False
        self.status_label.text = f'完成！成功 {success}/{total} 张，已保存到相册'
        self.progress.value = 0

    def process_single_image(self, img):
        cfg = self.cfg
        if cfg['flip_h']:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if cfg['flip_v']:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if cfg['color_jitter']:
            img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95, 1.05))
            img = ImageEnhance.Contrast(img).enhance(random.uniform(0.95, 1.05))
            img = ImageEnhance.Color(img).enhance(random.uniform(0.95, 1.05))
        angle = random.uniform(-cfg['max_angle'], cfg['max_angle'])
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255,255,255))
        crop = random.randint(1, 3)
        w, h = img.size
        img = img.crop((crop, crop, w-crop, h-crop))
        scale = random.uniform(0.995, 1.005)
        new_size = (int(img.width*scale), int(img.height*scale))
        img = img.resize(new_size, Image.LANCZOS)
        pixels = img.load()
        noise = random.randint(1, 2)
        for i in range(img.width):
            for j in range(img.height):
                r,g,b = pixels[i,j]
                r = min(255, max(0, r + random.randint(-noise, noise)))
                g = min(255, max(0, g + random.randint(-noise, noise)))
                b = min(255, max(0, b + random.randint(-noise, noise)))
                pixels[i,j] = (r,g,b)
        if cfg['add_border']:
            border_color = random.choice([(255,255,255), (0,0,0)])
            img = ImageOps.expand(img, border=1, fill=border_color)
        if cfg['png_recode']:
            temp = BytesIO()
            img.save(temp, format='PNG')
            temp.seek(0)
            img = Image.open(temp).convert('RGB')
        out = BytesIO()
        img.save(out, format='JPEG', quality=cfg['quality'], optimize=True)
        out.seek(0)
        return out

    def save_to_gallery(self, image_bytes):
        if platform == 'android':
            resolver = Activity.getApplicationContext().getContentResolver()
            values = ContentValues()
            filename = f"processed_{random.randint(10000,99999)}.jpg"
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
            values.put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            if hasattr(MediaStore.MediaColumns, 'RELATIVE_PATH'):
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/AntiDedup")
            uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            if uri:
                out = resolver.openOutputStream(uri)
                out.write(image_bytes.getvalue())
                out.close()
                log_error(f"保存到相册: {filename}")
        else:
            with open(f"processed_{random.randint(10000,99999)}.jpg", "wb") as f:
                f.write(image_bytes.getvalue())

if __name__ == '__main__':
    AntiDedupApp().run()