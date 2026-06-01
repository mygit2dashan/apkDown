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
android.ndk = 23.1.7779620
android.accept_sdk_license = True

android.python_version = 3.10.20
android.archs = arm64-v8a

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# 添加补丁文件：将修复后的 HIDDeviceManager.java 放入仓库的 src/ 目录
android.add_src = src

android.gradle = True
android.use_jdk21 = True
android.allow_backup = True

log_level = 2
warn_on_root = 0