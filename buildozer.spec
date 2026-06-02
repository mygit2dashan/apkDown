[app]
title = TestApp
package.name = testapp
package.domain = org.test

source.dir = .
source.include_exts = py

version = 1.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 30
android.minapi = 21
android.accept_sdk_license = True

android.archs = arm64-v8a

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

log_level = 2
warn_on_root = 0