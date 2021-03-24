# While iterating through sprite files by game, this will make and save thumbnails as necessary

import importlib
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../../'))

def do_previews():
  with(open(os.path.join(".","meta","manifests","consoles.txt"), "r")) as consoles:
    for console in consoles:
      console = console.strip()
      paths = { "console": os.path.join(".",console) }
      with(open(os.path.join(paths["console"],"games.txt"), "r")) as games:
        for game in games:
          game = game.strip()
          paths["game"] = os.path.join(paths["console"],game)
          with(open(os.path.join(paths["game"],"manifests","manifest.json"), "r")) as manifest:
            manifest = json.load(manifest)
            for key in manifest:
              if "$schema" not in key:
                if "name" in manifest[key] and "folder name" in manifest[key]:
                  sprite = manifest[key]["folder name"]
                  paths["sprite"] = os.path.join(paths["game"],sprite)
                  print("Processing: %s/%s/%s" % (console,game,sprite))
                  previews_module = False
                  try:
                    previews_module = importlib.import_module(f"resources.ci.{console}.{game}.{sprite}.sprite_previews")
                  except ModuleNotFoundError:
                    print("No specific previews processing for: %s/%s/%s" % (console,game,sprite))
                  if previews_module:
                    previews_module.create_previews()
                  print()

if __name__ == "__main__":
  do_previews()
