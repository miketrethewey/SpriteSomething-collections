# While building index files, this will build for each sprite of each game of each console

import json
import os

from shutil import copy

indexTemplateFile = open(os.path.join(".","resources","ci","templates","template.html"))
indexTemplate = indexTemplateFile.read()
indexTemplateFile.close()
print("Index")
with(open(os.path.join("index.html"), "w")) as indexFile:
  thisTemplate = indexTemplate.replace("<PATH_ROOT>", "./")
  thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", "")
  thisTemplate = thisTemplate.replace("<PATH_GAME>", "")
  thisTemplate = thisTemplate.replace("<PATH_SPRITE>", "")
  indexFile.write(thisTemplate)

with(open(os.path.join(".","meta","manifests","consoles.txt"), "r")) as consoles:
  for console in consoles:
    console = console.strip()
    paths = { "console": os.path.join(".",console) }
    consoleTemplateFile = open(os.path.join(".","resources","ci","templates","template.html"))
    consoleTemplate = consoleTemplateFile.read()
    consoleTemplateFile.close()
    print(" " + console.upper() + " [" + console + "]")
    with(open(os.path.join(paths["console"],"index.html"), "w")) as consoleFile:
      thisTemplate = consoleTemplate.replace("<PATH_ROOT>", "../")
      thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
      thisTemplate = thisTemplate.replace("<PATH_GAME>", "")
      thisTemplate = thisTemplate.replace("<PATH_SPRITE>", "")
      consoleFile.write(thisTemplate)
    with(open(os.path.join(paths["console"],"games.txt"), "r")) as games:
      gameTemplateFile = open(os.path.join(".","resources","ci","templates","template.html"))
      gameTemplate = gameTemplateFile.read()
      gameTemplateFile.close()
      for game in games:
        game = game.strip()
        paths["game"] = os.path.join(paths["console"],game)
        gameName = game
        with(open(os.path.join(paths["game"],"lang","en.json"), "r")) as en_lang:
          en = json.load(en_lang)
          if "game" in en and "name" in en["game"]:
            gameName = en["game"]["name"]
            print("  " + en["game"]["name"] + " [" + console + "/" + game + "]")
        with(open(os.path.join(paths["game"],"index.html"), "w")) as gameFile:
          thisTemplate = gameTemplate.replace("<PATH_ROOT>", "../../")
          thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
          thisTemplate = thisTemplate.replace("<PATH_GAME>", game)
          thisTemplate = thisTemplate.replace("<PATH_SPRITE>", "")
          gameFile.write(thisTemplate)
        with(open(os.path.join(paths["game"],"manifests","manifest.json"), "r")) as manifest:
          manifest = json.load(manifest)
          spriteTemplateFile = open(os.path.join(".","resources","ci","templates","template.html"))
          spriteTemplate = spriteTemplateFile.read()
          spriteTemplateFile.close()
          for key in manifest:
            if "$schema" not in key:
              if "name" in manifest[key] and "folder name" in manifest[key]:
                paths["sprite"] = os.path.join(paths["game"],manifest[key]["folder name"])
                print("   " + manifest[key]["name"] + " [" + console + "/" + game + "/" + manifest[key]["folder name"] + "]")
                copy(
                    os.path.join(".","resources","ci","templates","sprites-redir.html"),
                    os.path.join(paths["sprite"],"sprites.html")
                )
                with(open(os.path.join(paths["sprite"],"index.html"), "w")) as spriteFile:
                  thisTemplate = spriteTemplate.replace("<PATH_ROOT>", "../../../")
                  thisTemplate = thisTemplate.replace("<PATH_CONSOLE>", console)
                  thisTemplate = thisTemplate.replace("<PATH_GAME>", game)
                  thisTemplate = thisTemplate.replace("<PATH_SPRITE>", manifest[key]["folder name"])
                  spriteFile.write(thisTemplate)
