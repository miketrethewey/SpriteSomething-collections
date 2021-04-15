import json
import os

import common

env = common.prepare_env()

CI_SETTINGS = {}
with(open(os.path.join("meta","manifests","ci.json"))) as ci_settings_file:
  CI_SETTINGS = json.load(ci_settings_file)

VERSION = ""
with(open(os.path.join(".",*CI_SETTINGS["common"]["prepare_appversion"]["app_version"]),"r")) as app_version:
    VERSION = app_version.readline().strip()
    if env["BUILD_NUMBER"] != "":
        VERSION += '.' + env["BUILD_NUMBER"]

with(open(os.path.join(".",*CI_SETTINGS["common"]["prepare_appversion"]["app_version"]),"w+")) as app_version:
    app_version.write(VERSION)

print("%s: %s" % (CI_SETTINGS["common"]["common"]["repo"]["repository"] ,VERSION))
