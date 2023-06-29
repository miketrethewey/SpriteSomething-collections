# control bits:
#  0: Software Bop
#  1: Full Horizontal Flip
import csv
import os
import shutil
import ssl
import tempfile
import urllib.request
import yaml
import zipfile

def check_ffmqr():
    slugs = {
        "ffmqr": {},
        "local": {},
        "not-ffmqr": {},
        "not-local": {}
    }
    (console,game,sprite) = ("snes","ffmq","benjamin")
    local_resources = os.path.join(".","resources","ci",console,game,sprite)
    csv_sheet = []
    print("Getting data from CSV")
    with(open(os.path.join(local_resources,"sprites.csv"),"r",encoding="utf-8")) as csv_file:
        rd = csv.reader(csv_file)
        for row in rd:
          if len(row) > 0:
            csv_sheet.append(row)
    sprites = []
    if(len(csv_sheet) > 0):
        print("Processing metadata from CSV")
        keys = []
        i = 0
        for row in csv_sheet:
            j = 0
            slug = ""
            for cell in row:
                if i == 0:
                    keys.append(cell.lower())
                else:
                    if i > len(sprites):
                        sprites.append({})
                        sprites[i - 1][keys[j]] = cell
                        if keys[j] == "slug":
                            # add from local
                            slug = cell
                            slugs["local"][cell] = {}
                    if slug in slugs["local"] and "name" in keys[j].lower():
                        slugs["local"][slug]["name"] = cell
                j += 1
            i+= 1

    url = "https://github.com/wildham0/FFMQRando/raw/dev/FFMQRLib/sprites/customsprites.zip"
    context = ssl._create_unverified_context()
    req = urllib.request.urlopen(url, context=context)
    archive_data = req.read()
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "sprites.zip"), "wb") as sprite_archive:
            sprite_archive.write(archive_data)
            with zipfile.ZipFile(os.path.join(tempdir, "sprites.zip"), 'r') as thisZip:
                thisZip.extractall(tempdir)
                with open(os.path.join(tempdir, "metadata.yaml"), "r", encoding="utf-8") as metadataYAML:
                    metadata = yaml.safe_load(metadataYAML)
                    for sprite_meta in metadata:
                        if "filename" in sprite_meta:
                            # add from FFMQR
                            slugs["ffmqr"][sprite_meta["filename"]] = sprite_meta
                            if sprite_meta["filename"] not in slugs["local"]:
                                # if we don't have a local copy, note it
                                slugs["not-local"][sprite_meta["filename"]] = sprite_meta
                                shutil.copy(
                                    os.path.join(
                                        tempdir,
                                        "spritesheets",
                                        sprite_meta["filename"] + ".bmp"
                                    ),
                                    os.path.join(
                                        console,
                                        game,
                                        sprite,
                                        "sheets",
                                        "import",
                                        sprite_meta["filename"] + ".1.bmp"
                                    )
                                )

    for slug in slugs["local"]:
        if slug not in ["001.benjamin", "guide"] and slug not in slugs["ffmqr"]:
            slugs["not-ffmqr"][slug] = {}

    for [sprite_domain, sprite_list] in slugs.items():
        if "not-" in sprite_domain:
            slug_keys = list(sprite_list.keys())
            slug_keys.sort()
            if len(slug_keys) > 0:
                print(sprite_domain)
                for slug in slug_keys:
                    if slug in sprite_list:
                        sprite = sprite_list[slug]
                        if "filename" in sprite:
                            print(slug,sprite)
                print()
    return slugs["local"]


if __name__ == "__main__":
    check_ffmqr()
