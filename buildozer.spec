
[app]

title = 图片抗检测
package.name = image_anti_dedup
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0
requirements = python3,kivy,pillow

orientation = portrait
fullscreen = 0

# 必须注释掉，因为没有图片文件
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 34.0.0

android.accept_sdk_license = True
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.gradle = True
android.use_jdk21 = True

log_level = 2
warn_on_root = 1
