"""
Image Anti-Deduplication - Stable for HarmonyOS
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
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO

# Android imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass

    # Request all needed permissions at start
    perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
    try:
        from android.permissions import Permission as P
        if hasattr(P, 'READ_MEDIA_IMAGES'):
            perms.append(P.READ_MEDIA_IMAGES)
    except:
        pass
    request_permissions(perms)

    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Activity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    ContentValues = autoclass('android.content.ContentValues')
else:
    from plyer import filechooser

# Settings
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
        layout = BoxLayout(orientation='vertical', padding: 20, spacing: 15)

        # Title
        title = Label(text='Image Anti-Deduplication', font_size='24sp', size_hint=(1, 0.15))
        layout.add_widget(title)

        # Status
        self.status = Label(text='No images selected', font_size='18sp', size_hint=(1, 0.1))
        layout.add_widget(self.status)

        # Select button
        btn_select = Button(text='Select Images (Multi)', font_size='20sp', size_hint=(1, 0.15))
        btn_select.bind(on_press=self.select_images)
        layout.add_widget(btn_select)

        # Process button
        btn_process = Button(text='Start Processing', font_size='20sp', size_hint=(1, 0.15))
        btn_process.bind(on_press=self.start_processing)
        layout.add_widget(btn_process)

        # Progress
        self.progress = ProgressBar(max=100, size_hint=(1, 0.05), value=0)
        layout.add_widget(self.progress)

        # Info
        info_text = (f"Settings: flip_h={self.cfg['flip_h']}, color_jitter={self.cfg['color_jitter']}, "
                     f"angle={self.cfg['max_angle']}°, quality={self.cfg['quality']}%")
        info = Label(text=info_text, font_size='14sp', size_hint=(1, 0.1))
        layout.add_widget(info)

        return layout

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

    def select_images(self, instance):
        if platform == 'android':
            intent = Intent()
            intent.setAction(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
            activity.bind(on_activity_result=self.on_activity_result)
            activity.startActivityForResult(intent, 0x1234)
        else:
            filechooser.open_files(on_selection=self.on_files_selected, multiple=True)

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 0x1234 and resultCode == -1:
            self.selected_uris.clear()
            if intent.getData() is not None:
                self.selected_uris.append(str(intent.getData()))
            else:
                clipData = intent.getClipData()
                if clipData is not None:
                    for i in range(clipData.getItemCount()):
                        uri = clipData.getItemAt(i).getUri()
                        self.selected_uris.append(str(uri))
            self.status.text = f'Selected {len(self.selected_uris)} image(s)'
        activity.unbind(on_activity_result=self.on_activity_result)

    def on_files_selected(self, selection):
        self.selected_uris = selection if selection else []
        self.status.text = f'Selected {len(self.selected_uris)} image(s)'

    def start_processing(self, instance):
        if self.processing:
            return
        if not self.selected_uris:
            self.status.text = 'Please select images first!'
            return
        self.processing = True
        self.progress.value = 0
        Clock.schedule_once(lambda dt: self.process_all(), 0)

    def process_all(self):
        total = len(self.selected_uris)
        success = 0
        for idx, img_src in enumerate(self.selected_uris):
            self.status.text = f'Processing {idx+1}/{total}'
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
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
            self.progress.value = (idx+1)/total * 100
        self.processing = False
        self.status.text = f'Done! Success {success}/{total} saved to gallery'
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
        else:
            with open(f"processed_{random.randint(10000,99999)}.jpg", "wb") as f:
                f.write(image_bytes.getvalue())

if __name__ == '__main__':
    AntiDedupApp().run()
