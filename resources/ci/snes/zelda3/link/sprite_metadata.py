import os
import re

from collections import OrderedDict
from glob import glob
from .ZSPR import ZSPR

def get_local_metadata():
    (console,game,sprite) = ("snes","zelda3","link")
    site_resources = os.path.join(".",console,game,sprite)
    online_resources = (f"https://miketrethewey.github.io/SpriteSomething-collections/{console}/{game}/{sprite}")

    print("Getting metadata from ZSPRs")
    spritesmeta = OrderedDict()

    VERSION = ""
    with(open(os.path.join(".","meta","manifests","app_version.txt"), "r")) as appversion:
        VERSION = appversion.readline().strip()

    spritesmeta["meta"] = {
      "class": online_resources + "/sheets/previews/sprites.class." + VERSION + ".png",
      "selector": online_resources + "/sheets/previews/sprites." + VERSION + ".png",
      "version": VERSION
    }

    # get ZSPRs
    maxs,maxn = 0,0

    for file in glob(os.path.join(site_resources,"sheets","*.zspr")):
        if os.path.isfile(file):
            sprite = ZSPR(file)
            basename = os.path.basename(sprite.filename)
            matches = re.search(r"([^\.]*)(?:[\.]?)([^\.]*)(?:[\.]?)([^\.]*)(?:[\.]?)([^\.]*)", basename)
            groups = matches.groups()
            groups = list(x for x in groups if x)
            groups = groups[::-1]
            filext = groups[0]
            del groups[0]
            ver = 0
            if len(groups) >= 2:
              ver = groups[0]
              del groups[0]
            groups = groups[::-1]
            slug = '.'.join(groups)
            maxs = max(maxs,len(slug))
            maxn = max(maxn,len(sprite.name))
            if slug not in spritesmeta:
                  spritesmeta[slug] = {}
            spritesmeta[slug]["name"] = sprite.name
            spritesmeta[slug]["author"] = sprite.author_name
            spritesmeta[slug]["short_slug"] = slug
            spritesmeta[slug]["slug"] = slug + '.' + str(ver)
            spritesmeta[slug]["version"] = int(ver)
            spritesmeta[slug]["file"] = online_resources + "/sheets/" + slug + '.' + str(ver) +  ".zspr"
            spritesmeta[slug]["filename"] = basename
            spritesmeta[slug]["preview"] = online_resources + "/sheets/thumbs/" + slug + '.' + str(ver) +  ".png"

    return spritesmeta,maxs,maxn
