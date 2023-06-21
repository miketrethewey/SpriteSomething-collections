import json
import os
import shutil

with open(os.path.join(".","meta","manifests","consoles.txt"), "r", encoding="utf-8") as consoleManifest:
    consoleList = consoleManifest.readlines()
    for console in consoleList:
        console = console.strip()
        indexPath = os.path.join(".",console,"index.html")
        if os.path.isfile(indexPath):
            os.remove(
                os.path.join(
                    ".",
                    console,
                    "index.html"
                )
            )
        with open(os.path.join(".",console,"games.txt"), "r", encoding="utf-8") as gameManifest:
            gameList = gameManifest.readlines()
            for game in gameList:
                game = game.strip()
                indexPath = os.path.join(".",console,game,"index.html")
                if os.path.isfile(indexPath):
                    os.remove(
                        os.path.join(
                            ".",
                            console,
                            game,
                            "index.html"
                        )
                    )
                with open(os.path.join(".",console,game,"manifests","manifest.json"), "r", encoding="utf-8") as manifestFile:
                    manifestJSON = json.load(manifestFile)
                    for [spriteID, sprite] in manifestJSON.items():
                        if "$schema" not in spriteID:
                            for dirname in ["thumbs","previews"]:
                                dirPath = os.path.join(
                                    ".",
                                    console,
                                    game,
                                    sprite["folder name"],
                                    "sheets",
                                    dirname
                                )
                                if os.path.isdir(dirPath):
                                    shutil.rmtree(dirPath)
                            spritefiles = [
                                "index.html",
                                "previews.html",
                                "sprites.css",
                                "sprites.csv",
                                "sprites.html",
                                "z3m3.json"
                            ]
                            if os.path.isdir(os.path.join(
                                ".",
                                "resources",
                                "ci",
                                console,
                                game,
                                sprite["folder name"]
                            )) and "sprites.xls" in os.listdir(
                                os.path.join(
                                    ".",
                                    "resources",
                                    "ci",
                                    console,
                                    game,
                                    sprite["folder name"]
                                )
                            ):
                                spritefiles.append("sprites.json")
                            for spritefile in spritefiles:
                                spritePath = os.path.join(
                                    ".",
                                    console,
                                    game,
                                    sprite["folder name"],
                                    spritefile
                                )
                                if os.path.isfile(spritePath):
                                    os.remove(spritePath)
