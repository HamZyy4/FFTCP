[app]
title = TeeXez TCP Bot
package.name = teexeztcpbot
package.domain = id.teexez
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
source.exclude_dirs = .git,.github,__pycache__
version = 1.0.0
requirements = python3,kivy,requests,pycryptodome,protobuf_decoder
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = True
android.logcat_filters = *:S python:D
p4a.bootstrap = sdl2
[buildozer]
log_level = 2
warn_on_root = 1
