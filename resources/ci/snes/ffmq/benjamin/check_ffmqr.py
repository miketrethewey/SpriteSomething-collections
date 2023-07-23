# control bits:
#  0: Software Bop
#  1: Full Horizontal Flip
import csv
import json
import os
import re
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
    spritePath = os.path.join(
        ".",
        console,
        game,
        sprite
    )
    sheetsPath = os.path.join(spritePath, "sheets")
    manifestsPath = os.path.join(spritePath, "manifests")

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
    for filename in os.listdir(sheetsPath):
        match = re.match(r"^([\.\d]*[^\.]*)(?:[\.])(\d+)(?:.bmp)$", filename)
        if match:
            slug = match.group(1)
            if slug in slugs["local"]:
                slugs["local"][slug]["version"] = int(match.group(2))

    get_new_archive = False

    listinguser = "miketrethewey"
    listingrepo = "SpriteSomething-collections"
    listingpath = "snes/ffmq/benjamin"
    listingsha  = "manifests/sha.txt"

    repouser    = "wildham0"
    reporepo    = "FFMQRando"
    repobranch  = "dev"
    repopath    = "FFMQRLib/sprites/customsprites.zip"

    context = ssl._create_unverified_context()

    # check latest sha
    print("Checking latest commit ID to FFMQR/Benjamin archive")
    latestsha   = ""
    localsha    = ""
    url = f"https://api.github.com/repos/{repouser}/{reporepo}/commits?path={repopath}"
    req = urllib.request.urlopen(url, context=context)
    req_data = req.read().decode("utf-8")
    latestShaJSON = None
    try:
        latestShaJSON = json.loads(req_data)
        latestsha = latestShaJSON[0]["sha"]
        print(f"> {latestsha}")
    except Exception as e:
        print(e)

    if latestsha != "":
        # check local sha
        print("Checking saved commit ID for FFMQR/Benjamin archive")
        url = f"http://{listinguser}.github.io/{listingrepo}/{listingpath}/{listingsha}"
        req = None
        try:
            req = urllib.request.urlopen(url, context=context)
        except Exception as e:
            req = None
            if "404" in str(e):
                print("Online saved commit ID not found")
                print("Checking local saved commit ID")
        with open(os.path.join(manifestsPath, "sha.txt"), "r+", encoding="utf-8") as shaFile:
            if req:
                localsha = req.read()
            else:
                localsha = shaFile.read()
            print(f"> {localsha}")
            get_new_archive = latestsha != localsha
            if get_new_archive:
                shaFile.seek(0)
                shaFile.write(latestsha)
                commitsPath = os.path.join(manifestsPath, "commits.txt")
                with open(commitsPath, "w+", encoding="utf-8") as commitsFile:
                    commitsFile.seek(0)
                    commits = []
                    for commit in latestShaJSON:
                        commits.append(
                            {
                                "sha": commit["sha"],
                                "commit": {
                                    "author": commit["commit"]["author"],
                                    "committer": commit["commit"]["committer"],
                                    "message": commit["commit"]["message"]
                                },
                                "html_url": commit["html_url"]
                            }
                        )
                    commitsFile.write(json.dumps(commits, indent=2))

    if get_new_archive:
        # get new sprites archive
        print("Getting new copy of FFMQR/Benjamin archive")
        url = f"https://github.com/{repouser}/{reporepo}/raw/{repobranch}/{repopath}"
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
                                            ".",
                                            console,
                                            game,
                                            sprite,
                                            "sheets",
                                            "import",
                                            sprite_meta["filename"] + ".1.bmp"
                                        )
                                    )
    else:
        print("Skipping new copy of FFMQR/Benjamin archive")

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
                        sprite_data = sprite_list[slug]
                        if "filename" in sprite_data:
                            print(slug,sprite_data)
                print()

    with open(os.path.join(manifestsPath, "slugs.json"), "w+", encoding="utf-8") as slugsFile:
        slugsFile.write(json.dumps(slugs, indent=2))

    # importManifestsPath = os.path.join(
    #     sheetsPath,
    #     "import",
    #     "manifests"
    # )
    # if os.path.exists(importManifestsPath):
    #     shutil.rmtree(importManifestsPath)
    # shutil.copytree(
    #     manifestsPath,
    #     importManifestsPath
    # )
    return slugs["local"]


if __name__ == "__main__":
    check_ffmqr()
