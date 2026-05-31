[app]

# 应用名称（显示在手机桌面）
title = 图片抗检测

# 包名（唯一标识，建议改为你自己的域名）
package.name = image_anti_dedup
package.domain = org.example

# 源代码目录和需要包含的文件扩展名
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

# 版本号
version = 1.0

# 依赖库（必须包含 python3，其他按需添加）
requirements = python3,kivy,pillow

# 屏幕方向
orientation = portrait

# 全屏模式（0=非全屏，1=全屏）
fullscreen = 0

# 图标和启动画面（如果没有图片文件，请务必注释掉）
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# 安卓 API 级别
android.api = 33
android.minapi = 21

# 推荐不指定 NDK 版本，让 Buildozer 自动选择
# 如果必须指定，用 25b 或 23c，不要用 23b
# android.ndk = 25b

# 编译工具版本
android.sdk = 33
android.build_tools = 34.0.0

# 接受 SDK 许可证
android.accept_sdk_license = True

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 使用 Gradle 和 JDK 21
android.gradle = True
android.use_jdk21 = True

# 日志级别（2 输出详细信息，有助于调试）
log_level = 2

# 有警告时不中断构建
warn_on_root = 1
