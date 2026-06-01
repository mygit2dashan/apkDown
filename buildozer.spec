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

android.api = 31                     # 从 30 提升到 31
android.minapi = 21
android.build_tools = 31.0.0
android.accept_sdk_license = True

android.python_version = 3.10.20
android.archs = arm64-v8a

# 添加 BLUETOOTH_CONNECT 权限（解决 SDL2 编译错误）
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, BLUETOOTH_CONNECT

android.gradle = True
android.use_jdk21 = True
android.allow_backup = True

log_level = 2
warn_on_root = 0
