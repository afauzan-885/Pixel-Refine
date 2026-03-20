[app]

# (str) Title of your application
title = Pixel Refine

# (str) Package name
package.name = pixel_refine

# (str) Package domain (needed for android/ios packaging)
package.domain = org.pixelrefine

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to include any file)
#source.exclude_exts = spec

source.exclude_dirs = tests, bin, venv, .git, pixel_refine_desktop, .buildozer

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pillow, tifffile, exifread

# (str) Custom source folders for requirements
# packagename.use_custom = /path/to/custom/package

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 33

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess bandwidth usage or network errors
#android.skip_update = False

android.accept_sdk_license = True

# (str) Android entry point, default is main.py
android.entrypoint = main_mobile.py

# (list) Android application meta-data (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so

# (bool) copy_libs_armeabi_v7a (default False)
#android.copy_libs_armeabi_v7a = True

# (bool) copy_libs_arm64_v8a (default False)
#android.copy_libs_arm64_v8a = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (default False)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1

# (str) Path to build artifact storage, logging and cache
# build_dir = ./.buildozer

# (str) Path to bin directory
# bin_dir = ./bin
