[app]
title = Image AntiDedup
package.name = image_anti_dedup
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0
requirements = python3,kivy,pillow,pyjnius

orientation = portrait
fullscreen = 0

android.api = 30
android.minapi = 21
# 不要指定 android.ndk，让 buildozer 自动下载可用版本（当前推荐 r28c）
android.accept_sdk_license = True

android.python_version = 3.10.20
android.archs = arm64-v8a

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# 添加补丁文件夹（用于替换有问题的 Java 文件）
android.add_src = src

android.gradle = True
android.use_jdk21 = True
android.allow_backup = True

log_level = 2
warn_on_root = 0