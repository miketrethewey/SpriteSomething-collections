import os

import common

env = common.prepare_env()

VERSION = ""
with(open(os.path.join(".","meta","manifests","app_version.txt"))) as app_version:
    VERSION = app_version.readline()
    if env["BUILD_NUMBER"] != "":
        VERSION += '.' + env["BUILD_NUMBER"]

print(VERSION)
