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

# 如果没有 icon.png 和 presplash.png，请保持注释状态
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools = 34.0.0

# 这一行必须存在，且值为 True
android.accept_sdk_license = True

android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.gradle = True
android.use_jdk21 = True

log_level = 2
warn_on_root = 1
