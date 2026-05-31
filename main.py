import os, random, threading
from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10)
        self.add_widget(Label(text='输出: DCIM/Processed', size_hint_y=None, height=30))
        flip_box = BoxLayout(size_hint_y=None, height=40)
        self.flip_h_btn = ToggleButton(text='水平翻转')
        self.flip_v_btn = ToggleButton(text='垂直翻转')
        flip_box.add_widget(self.flip_h_btn); flip_box.add_widget(self.flip_v_btn)
        self.add_widget(flip_box)
        self.color_btn = ToggleButton(text='色彩微调', size_hint_y=None, height=40)
        self.border_btn = ToggleButton(text='细边框', size_hint_y=None, height=40)
        self.png_btn = ToggleButton(text='PNG转码', size_hint_y=None, height=40)
        self.add_widget(self.color_btn); self.add_widget(self.border_btn); self.add_widget(self.png_btn)
        self.add_widget(Label(text='旋转角度 (°)', size_hint_y=None, height=30))
        self.angle_slider = Slider(min=0, max=2, value=0.6, step=0.1)
        self.angle_label = Label(text='0.6°', size_hint_y=None, height=20)
        self.add_widget(self.angle_slider); self.add_widget(self.angle_label)
        self.angle_slider.bind(value=lambda i,v: setattr(self.angle_label, 'text', f'{v:.1f}°'))
        self.add_widget(Label(text='JPEG画质', size_hint_y=None, height=30))
        self.qual_slider = Slider(min=90, max=100, value=95, step=1)
        self.qual_label = Label(text='95', size_hint_y=None, height=20)
        self.add_widget(self.qual_slider); self.add_widget(self.qual_label)
        self.qual_slider.bind(value=lambda i,v: setattr(self.qual_label, 'text', str(int(v))))
        self.progress = ProgressBar(max=100, size_hint_y=None, height=20)
        self.add_widget(self.progress)
        self.status = Label(text='就绪', size_hint_y=None, height=30)
        self.add_widget(self.status)
        self.btn = Button(text='选择图片并处理', size_hint_y=None, height=50)
        self.btn.bind(on_press=self.open_chooser)
        self.add_widget(self.btn)

    def open_chooser(self, *args):
        content = BoxLayout(orientation='vertical')
        fc = FileChooserListView(filters=['*.jpg','*.jpeg','*.png','*.webp'], multiselect=True)
        content.add_widget(fc)
        btn_box = BoxLayout(size_hint_y=None, height=50)
        btn_box.add_widget(Button(text='开始处理', on_press=lambda x: self.process(fc.selection)))
        btn_box.add_widget(Button(text='取消', on_press=lambda x: self.popup.dismiss()))
        content.add_widget(btn_box)
        self.popup = Popup(title='选择图片', content=content, size_hint=(0.9,0.9))
        self.popup.open()

    def process(self, files):
        if not files: return
        self.popup.dismiss()
        out_dir = '/storage/emulated/0/DCIM/Processed'
        os.makedirs(out_dir, exist_ok=True)
        cfg = {
            'flip_h': self.flip_h_btn.state == 'down',
            'flip_v': self.flip_v_btn.state == 'down',
            'color': self.color_btn.state == 'down',
            'border': self.border_btn.state == 'down',
            'png': self.png_btn.state == 'down',
            'angle': self.angle_slider.value,
            'quality': int(self.qual_slider.value),
        }
        self.btn.disabled = True
        self.status.text = '处理中...'
        self.progress.max = len(files)
        self.progress.value = 0

        def worker():
            for i, f in enumerate(files):
                img = Image.open(f).convert('RGB')
                if cfg['flip_h']: img = img.transpose(Image.FLIP_LEFT_RIGHT)
                if cfg['flip_v']: img = img.transpose(Image.FLIP_TOP_BOTTOM)
                if cfg['color']:
                    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95,1.05))
                    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.95,1.05))
                    img = ImageEnhance.Color(img).enhance(random.uniform(0.95,1.05))
                angle = random.uniform(-cfg['angle'], cfg['angle'])
                img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255,255,255))
                crop = random.randint(1,3)
                w,h = img.size
                img = img.crop((crop, crop, w-crop, h-crop))
                scale = random.uniform(0.995,1.005)
                img = img.resize((int(img.width*scale), int(img.height*scale)), resample=Image.LANCZOS)
                px = img.load()
                ns = random.randint(1,2)
                for x in range(img.width):
                    for y in range(img.height):
                        r,g,b = px[x,y]
                        n = random.randint(-ns, ns)
                        px[x,y] = (min(255,max(0,r+n)), min(255,max(0,g+n)), min(255,max(0,b+n)))
                if cfg['border']:
                    img = ImageOps.expand(img, border=1, fill=random.choice([(255,255,255),(0,0,0)]))
                if cfg['png']:
                    tmp = BytesIO()
                    img.save(tmp, format='PNG')
                    tmp.seek(0)
                    img = Image.open(tmp).convert('RGB')
                out_path = os.path.join(out_dir, os.path.basename(f))
                tmp = BytesIO()
                img.save(tmp, format='JPEG', quality=cfg['quality'], optimize=True)
                tmp.seek(0)
                final = Image.open(tmp)
                final.save(out_path, format='JPEG', quality=cfg['quality'], optimize=True, exif=b'')
                Clock.schedule_once(lambda dt, i=i: (self.progress.setter('value')(self.progress, i+1), setattr(self.status, 'text', f'{i+1}/{len(files)}')))
            Clock.schedule_once(lambda dt: self.finish())
        threading.Thread(target=worker, daemon=True).start()

    def finish(self):
        self.btn.disabled = False
        self.status.text = '完成！保存在 DCIM/Processed'
        self.progress.value = 0

class AntiDedupApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    AntiDedupApp().run()
