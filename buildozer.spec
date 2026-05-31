[app]
title = 图片抗检测
package.name = image_anti_dedup
package.domain = org.example
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0

# Android 关键配置（解决许可证问题）
android.api = 33
android.minapi = 21
android.ndk = 23b
android.sdk = 33
android.build_tools = 34.0.0
android.accept_sdk_license = True
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.gradle = True
android.use_jdk21 = True
