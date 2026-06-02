from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    Intent = autoclass('android.content.Intent')
    Activity = autoclass('org.kivy.android.PythonActivity')

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.label = Label(text='No image selected', size_hint=(1, 0.3))
        btn = Button(text='Select Image(s)', size_hint=(1, 0.2))
        btn.bind(on_press=self.select_images)
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    def select_images(self, instance):
        if platform == 'android':
            intent = Intent()
            intent.setAction(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
            activity.bind(on_activity_result=self.on_result)
            activity.startActivityForResult(intent, 123)

    def on_result(self, requestCode, resultCode, intent):
        if resultCode == -1 and intent:
            self.label.text = 'Selected!'
        activity.unbind(on_activity_result=self.on_result)

if __name__ == '__main__':
    TestApp().run()