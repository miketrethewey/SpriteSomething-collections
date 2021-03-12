import os

import common

env = common.prepare_env()

VERSION = ""
with(open(os.path.join(".","meta","manifests","app_version.txt"),"r")) as app_version:
    VERSION = app_version.readline().strip()
    if env["BUILD_NUMBER"] != "":
        VERSION += '.' + env["BUILD_NUMBER"]

with(open(os.path.join(".","meta","manifests","app_version.txt"),"w+")) as app_version:
    app_version.write(VERSION)

print("SpriteSomething-collections: %s" % (VERSION))
