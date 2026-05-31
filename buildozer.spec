[app]

# 应用名称（标题）
title = 图片抗检测

# 包名（唯一标识）
package.name = image_anti_dedup
package.domain = org.example

# 源码目录和包含的文件扩展名
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

# 版本号
version = 1.0

# 所需依赖（Python 包）
requirements = python3,kivy,pillow

# 屏幕方向（portrait = 竖屏，landscape = 横屏）
orientation = portrait

# 是否全屏（0 = 否，1 = 是）
fullscreen = 0

# 图标和启动画面（如果没有图标文件，保持注释状态）
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# Android 配置
android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools = 34.0.0

# 指定稳定的 NDK 版本（关键修复，避免 r28c 兼容性问题）
android.ndk = 23.1.7779620

# 接受 SDK 许可证（必须为 True）
android.accept_sdk_license = True

# 应用权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 使用 Gradle 构建
android.gradle = True

# 使用 JDK 21（较新版本）
android.use_jdk21 = True

# 日志级别（2 = 详细调试信息）
log_level = 2

# 如果以 root 运行发出警告（保持为 1）
warn_on_root = 1
