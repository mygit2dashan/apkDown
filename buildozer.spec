[app]
title = Image AntiDedup
package.name = image_anti_dedup
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0
requirements = python3,kivy,pillow,pyjnius,android

orientation = portrait
fullscreen = 0

android.api = 30
android.minapi = 21
android.sdk = 30
android.build_tools = 30.0.3

# 不指定 NDK，让 buildozer 自动下载可用的版本
# android.ndk = 

android.accept_sdk_license = True

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

android.gradle = True
android.use_jdk21 = True
android.allow_backup = True
android.arch = arm64-v8a

log_level = 2
warn_on_root = 1
