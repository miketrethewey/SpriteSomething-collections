import os

from shutil import rmtree

toNuke = [
#  os.path.join(".",".git"), # leave it as a repo to run git commands later
	os.path.join(".",".github"), # nuke workflows
	os.path.join(".","resources") # nuke py source
]
for nuke in toNuke:
  rmtree(nuke)
