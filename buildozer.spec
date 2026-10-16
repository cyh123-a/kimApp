[app]

# (str) Title of your application
title = 状态栏盯盘

# (str) Package name
package.name = mynewapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.cyh

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,txt,png,jpg,kv

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,requests,plyer,android,jnius

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 23

# (list) Permissions
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE,WAKE_LOCK

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) python-for-android branch to use
p4a.branch = master

# (str) Android logcat filters
android.logcat_filters = *:S,Python:i

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1