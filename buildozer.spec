[app]

# 应用名称
title = 图片抗检测

# 包名（唯一标识）
package.name = image_anti_dedup
package.domain = org.example

# 源代码目录和要包含的文件扩展名
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

# 版本号
version = 1.0

# 依赖库
requirements = python3,kivy,pillow

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# 注意：以下两行被注释掉了，所以不需要提供 icon.png 和 presplash.png
# 不注释的话，构建时会报错“文件不存在”
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# 安卓 API 配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 34.0.0

# 必须接受许可
android.accept_sdk_license = True

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 使用 Gradle 和 JDK 21
android.gradle = True
android.use_jdk21 = True

# 日志级别（2 表示输出调试信息）
log_level = 2

# 警告不影响构建
warn_on_root = 1
