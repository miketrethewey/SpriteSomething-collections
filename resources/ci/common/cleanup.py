import os

from shutil import rmtree

toNuke = [
  os.path.join(".",".git"),
	os.path.join(".",".github"),
	os.path.join(".","resources")
]
for nuke in toNuke:
  rmtree(nuke)
