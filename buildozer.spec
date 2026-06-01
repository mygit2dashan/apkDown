[app]
title = Image AntiDedup
package.name = image_anti_dedup
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0
requirements = python3,kivy,pillow,pyjnius
# 注意：移除了错误的 "android" 包，pyjnius 已经提供 Java 交互能力

orientation = portrait
fullscreen = 0

android.api = 30
android.minapi = 21
android.build_tools = 30.0.3
android.accept_sdk_license = True

# 关键：强制使用 Python 3.10（避免不兼容的 3.14）
android.python_version = 3.10.20

# 使用新的 archs 语法（替代废弃的 android.arch）
android.archs = arm64-v8a

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

android.gradle = True
android.use_jdk21 = True
android.allow_backup = True

log_level = 2
warn_on_root = 0
