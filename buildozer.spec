[app]
title = 图片抗检测
package.name = image_anti_dedup
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0
requirements = python3,kivy,pillow,android,pyjnius

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.build_tools = 34.0.0
android.accept_sdk_license = True

# 权限（读写外部存储）
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

android.gradle = True
android.use_jdk21 = True

log_level = 2
warn_on_root = 1

# 确保使用正确的 NDK（可选）
# android.ndk = 23.1.7779620
