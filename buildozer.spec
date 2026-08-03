[app]
title = Escaner Logistica
package.name = escanerlogistica
package.domain = org.logistica
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,opencv,pandas,openpyxl

orientation = portrait
fullscreen = 0
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
