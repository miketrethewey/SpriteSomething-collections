import json
import os
import re

from PIL import Image

from collections import OrderedDict
from glob import glob
from .check_ffmqr import check_ffmqr

def get_local_metadata():
    scouted = check_ffmqr()

    (console,game,sprite) = ("snes","ffmq","benjamin")
    site_resources = os.path.join(".",console,game,sprite)
    online_resources = (f"https://miketrethewey.github.io/SpriteSomething-collections/{console}/{game}/{sprite}")
    controlbits_manifest = []
    with open(os.path.join(".", console, game, "manifests", "manifest.json"), "r", encoding="utf-8") as sprite_manifest_file:
        sprite_manifest = json.load(sprite_manifest_file)
        controlbits_manifest = sprite_manifest["1"]["controlbits"]

    print("Getting metadata from BMPs")
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

    for file in glob(os.path.join(site_resources,"sheets","*.bmp")):
        if os.path.isfile(file):
            basename = os.path.basename(file)
            matches = re.search(r"([^\.]*)(?:[\.]?)([^\.]*)(?:[\.]?)([^\.]*)(?:[\.]?)([^\.]*)", basename)
            groups = matches.groups()
            groups = list(x for x in groups if x)
            groups = groups[::-1]
            del groups[0]
            ver = 0
            if len(groups) >= 2:
              ver = groups[0]
              del groups[0]
            groups = groups[::-1]
            slug = '.'.join(groups)
            maxs = max(maxs,len(slug))
            maxn = max(maxn,len(slug))
            if slug not in spritesmeta:
                  spritesmeta[slug] = {}
            if slug in scouted:
                for k in ["name"]:
                    if k in scouted[slug]:
                        spritesmeta[slug][k] = scouted[slug][k]
                        if k == "name":
                            maxn = max(maxn,len(scouted[slug][k]))
            spritesmeta[slug]["version"] = int(ver)
            spritesmeta[slug]["file"] = online_resources + "/sheets/" + slug + '.' + str(ver) +  ".bmp"
            spritesmeta[slug]["preview"] = online_resources + "/sheets/thumbs/" + slug + '.' + str(ver) +  ".png"
            spritesmeta[slug]["controlbits"] = []
            with Image.open(os.path.join(
                site_resources,
                "sheets",
                slug + '.' + str(ver) + ".bmp"
            )) as spritesheet:
                w = 8
                h = 16
                bith = 1 + 2
                metablock = spritesheet.crop(
                    (
                        96,48,
                        96+w,48+h
                    )
                )
                modblock = metablock.convert("RGBA")
                modblock = modblock.rotate(180)
                modblock = modblock.crop(
                    (
                        0,0,
                        w,bith
                    )
                )
                controlbits = []
                cbitrow = []
                r,g,b,a = modblock.getpixel((w-1,0))
                pixdata = modblock.getdata()
                newpixels = []
                for [pixID, pixel] in enumerate(pixdata):
                    if pixID > w:
                        cbitID = pixID - w - 1
                        cbitName = ""
                        if len(controlbits_manifest) > cbitID:
                            cbitName = controlbits_manifest[cbitID]["name"]
                        cbitrow.append(
                            {
                                "id": cbitID,
                                "name": cbitName,
                                "state": pixel != (r,g,b,a)
                            }
                        )
                        # if pixel == (r,g,b,a):
                        #     newpixels.append((r,g,b,0))
                        # else:
                        #     newpixels.append(pixel)
                        if (pixID + 1) % w == 0:
                            if pixID > w:
                                controlbits.append(cbitrow)
                            cbitrow = []
                #             print()
                # print(controlbits)
                spritesmeta[slug]["controlbits"] = controlbits

                # modblock.putdata(newpixels)
                # modblock.save(os.path.join(".","modblock.png"))
                # modblock.show()

    return spritesmeta,maxs,maxn
