# While building index files, this will build for each sprite of each game of each console

import json
import os

from shutil import copy

with open(os.path.join(".","meta","manifests","consoles.txt"), "r") as consoles:
  for console in consoles:
    console = console.strip()
    paths = { "console": os.path.join(".",console) }
    consoleTemplateFile = open(os.path.join(".","resources","ci","templates","console.html"))
    consoleTemplate = consoleTemplateFile.read()
    consoleTemplateFile.close()
    print(console.upper())
    with open(os.path.join(paths["console"],"index.html"), "w+") as consoleFile:
      thisTemplate = consoleTemplate.replace("<PRETTY_CONSOLE>", console.upper())
      thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
      consoleFile.write(thisTemplate)
    with open(os.path.join(paths["console"],"games.txt")) as games:
      gameTemplateFile = open(os.path.join(".","resources","ci","templates","game.html"))
      gameTemplate = gameTemplateFile.read()
      gameTemplateFile.close()
      for game in games:
        game = game.strip()
        paths["game"] = os.path.join(paths["console"],game)
        gameName = game
        with open(os.path.join(paths["game"],"lang","en.json")) as en_lang:
          en = json.load(en_lang)
          if "game" in en and "name" in en["game"]:
            gameName = en["game"]["name"]
            print(" " + en["game"]["name"] + " [" + game + "]")
        with open(os.path.join(paths["game"],"index.html"), "w+") as gameFile:
          thisTemplate = gameTemplate.replace("<PRETTY_CONSOLE>", console.upper())
          thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
          thisTemplate = thisTemplate.replace("<PRETTY_GAME>", gameName)
          thisTemplate = thisTemplate.replace("<PATH_GAME>", game)
          gameFile.write(thisTemplate)
        with open(os.path.join(paths["game"],"manifests","manifest.json")) as manifest:
          manifest = json.load(manifest)
          templateFile = open(os.path.join(".","resources","ci","templates","sprite.html"))
          template = templateFile.read()
          templateFile.close()
          for key in manifest:
            if "$schema" not in key:
              if "name" in manifest[key] and "folder name" in manifest[key]:
                paths["sprite"] = os.path.join(paths["game"],manifest[key]["folder name"])
                print("  " + manifest[key]["name"] + " [" + manifest[key]["folder name"] + "]")
                copy(
                    os.path.join(".","resources","ci","templates","sprites-redir.html"),
                    os.path.join(paths["sprite"],"sprites.html")
                )
                with open(os.path.join(paths["sprite"],"index.html"), "w+") as spriteFile:
                  thisTemplate = template.replace("<PRETTY_CONSOLE>", console.upper())
                  thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
                  thisTemplate = thisTemplate.replace("<PRETTY_GAME>", gameName)
                  thisTemplate = thisTemplate.replace("<PATH_GAME>", game)
                  thisTemplate = thisTemplate.replace("<PRETTY_SPRITE>", manifest[key]["name"])
                  thisTemplate = thisTemplate.replace("<PATH_SPRITE>", manifest[key]["folder name"])
                  spriteFile.write(thisTemplate)
