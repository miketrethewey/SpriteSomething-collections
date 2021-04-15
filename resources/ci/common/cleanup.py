import json
import os

from shutil import rmtree

CI_SETTINGS = {}
with(open(os.path.join("meta","manifests","ci.json"))) as ci_settings_file:
  CI_SETTINGS = json.load(ci_settings_file)

toNuke = []
for nuke in CI_SETTINGS["common"]["cleanup"]["nuke"]:
  toNuke.append(os.path.join(".",nuke))

for nuke in toNuke:
  rmtree(nuke)
