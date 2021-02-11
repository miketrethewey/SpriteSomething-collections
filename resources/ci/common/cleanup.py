import os

from shutil import rmtree

toNuke = [
  os.path.join(".",".git")
]
for nuke in toNuke:
  rmtree(nuke)
