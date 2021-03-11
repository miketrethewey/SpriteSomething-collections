import os

from shutil import rmtree

toNuke = [
  os.path.join(".",".git"), # nuke git settings
	os.path.join(".",".github"), # nuke workflows
	os.path.join(".","resources") # nuke py source
]
for nuke in toNuke:
  rmtree(nuke)
