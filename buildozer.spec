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

android.api = 33
android.minapi = 21
android.build_tools = 34.0.0
android.accept_sdk_license = True

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

log_level = 2
warn_on_root = 1
