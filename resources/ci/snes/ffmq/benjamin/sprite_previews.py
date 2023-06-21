# While iterating through sprite files, this will generate the preview images to serve to process_previews.py

import io
import math
import os

from resources.ci.common.common import strtr
from glob import glob
from PIL import Image

(console,game,sprite) = ("snes","ffmq","benjamin")
local_resources = os.path.join(".","resources","ci",console,game,sprite)
site_resources = os.path.join(".",console,game,sprite)
online_resources = (f"https://miketrethewey.github.io/SpriteSomething-collections/{console}/{game}/{sprite}")

def add_thumb(thumb,png,height,x,y):
    thisThumb = Image.open(thumb).resize((16,height),0)
    png.paste(thisThumb,(x,y))
    return png, x + 16

def get_image_for_sprite(sprite):
    if "valid" not in sprite or not sprite["valid"]:
        return None

    with Image.open(sprite["fname"]) as image:
        metablock = image.crop((96,48,96+8,48+16))
        metablock = metablock.convert("RGBA")
        r,g,b,a = metablock.getpixel((0,15))
        image = image.crop((0,0,0+16,0+16))
        image = image.convert("RGBA")
        pixdata = image.getdata()
        newpixels = []
        for pixel in pixdata:
            if pixel == (r,g,b,a):
                newpixels.append((0,0,0,0))
            else:
                newpixels.append(pixel)
        image.putdata(newpixels)

        # blow up by 400%
        zoom = 4
        return image.resize((image.size[0] * zoom, image.size[1] * zoom), 0)

def create_previews():
  VERSION = ""
  with(open(os.path.join(".","meta","manifests","app_version.txt"), "r")) as appversion:
      VERSION = appversion.readline().strip()

  with(open(os.path.join(".","commit.txt"), "w")) as commit:
      commit.write("Update Site to v" + VERSION)

  sprites = []

  # get ZSPRs
  maxn = 0
  names = {}
  print("Processing version: " + VERSION)
  print()
  print("Getting BMPs")
  for file in glob(os.path.join(site_resources,"sheets","*.bmp")):
      if os.path.isfile(file):
          sprite = {
            "fname": file,
            "slug": os.path.splitext(os.path.basename(file))[0],
            "valid": True
          }
          sprite["name"] = sprite["slug"][:1].upper() + sprite["slug"][1:]
          sprite["name"] = sprite["name"][:sprite["name"].rfind('.')]
          short_slug = sprite["slug"][:sprite["slug"].rfind('.')]
          names[short_slug] = sprite["name"]
          maxn = max(maxn,len(sprite["name"].replace(" ","")))
          sprites.append(sprite)
  # sort ZSPRs
  sprites.sort(key=lambda s: str.lower(s["name"] or "").strip())
  n = len(sprites)
  maxd = len(str(n))

  print()
  print("Wait a little bit, dude, there's %d sprites." % (n))
  print()

  maxs = 0
  # make previews for ZSPRs (400% size)
  print("Processing previews")
  for sprite in sprites:
      image = get_image_for_sprite(sprite)
      if image is None:
          print(f"ERROR: {sprite['name']}: Thumb not created!")
          continue
      maxs = max(maxs,len(sprite["slug"] + ".png"))
      image.save(os.path.join(site_resources,"sheets","thumbs",sprite["slug"] + ".png"),"png")

  # get the thumbnails (400%) we made
  thumbs = glob(os.path.join(site_resources,"sheets","thumbs","*.png"))

  # get the new ones and make a class image
  print("Making CSS for compiled thumbnail image")
  print("Making preview page for compiled thumbnail image")
  print("Making class image")
  zoom = 4
  width = 6 * 16 * zoom
  height = (math.ceil(len(thumbs) / 6)) * 16 * zoom
  print(f"Class Image: [{width}, {height}]")
  png = Image.new("RGBA", (width, height))
  png.putalpha(0)
  i = n + 1
  x = 0
  y = 0
  css  = '[class*=" icon-custom-"],' + "\n"
  css += '[class^=icon-custom-] {' + "\n"
  css += '  width:            16px;' + "\n"
  css += '  height:           16px;' + "\n"
  css += '  vertical-align:   bottom;' + "\n"
  css += '  background-image: url(' + (online_resources + "/sheets/previews/sprites." + VERSION + ".png") + ');' + "\n"
  css += '}' + "\n"
  mini = ""
  large = ""
  thtml = ""
  for thumb in sorted(thumbs, key=lambda s: str.lower(s or "").strip()):
      thisThumb = Image.open(thumb)
      png.paste(thisThumb,(x,y))
      slug = os.path.basename(thumb).replace(".png","")
      short_slug = slug[:slug.rfind('.')]
      name = names[short_slug]
      selector = strtr(name, {
        ' ': "",
        '(': '-',
        ')': "",
        "'": "",
        '.': "",
        '/': '-'
      })
      percent = (100 / (n / (i - 1)))
      percentString = ("-%.6f%%" % (percent)).rjust(12, ' ')
      num = n - i + 2
      css   += ((".icon-custom-%-*s{background-position:%s 0}/* %*d/%*d */") % (maxn, selector, percentString, maxd, num, maxd, n)) + "\n"
      mini  += ('<div data-id="%*d/%*d" class="sprite sprite-mini icon-custom-%s" title="%s"></div>' % (maxd, num, maxd, n, selector, name)) + "\n"
      large += ('<div data-id="%*d/%*d" class="sprite sprite-preview icon-custom-%s" title="%s"></div>' % (maxd, num, maxd, n, selector, name)) + "\n"
      thtml += ('<div data-id="%*d/%*d" class="sprite" title="%s"><img src="%s/sheets/thumbs/%s" /></div>' % (maxd, num, maxd, n, name, online_resources, os.path.basename(thumb))) + "\n"
      x += 16 * zoom
      if x >= width:
          x = 0
          y += 16 * zoom
      i -= 1
  png.save(os.path.join(site_resources,"sheets","previews","sprites.class." + VERSION + ".png"),"png")
  html = ('<html><head><link rel="stylesheet" href="sprites.css" type="text/css" /><style type="text/css">body{margin:0}.sprite{display:inline-block}.sprite-preview{width:64px;height:96px;background-size:auto 96px;image-rendering:pixelated}</style></head><body><div style="float:right"><a href="sprites.json">JSON</a><br /><a href="sprites.css">CSS</a><br /><a href="sprites.csv">CSV</a></div>' + "\n" + '<h2>Sprite Selector</h2><div class="sprite sprite-mini icon-custom-Random"></div>' + "\n" + '<MINI><br /><h2>Sprite Previews</h2><h3>from Sprite Selector</h3><LARGE><br /><h3>from Individual Images</h3><THUMBS></body></html>').replace("<MINI>",mini).replace("<LARGE>","\n"+large).replace("<THUMBS>","\n"+thtml)

  with(open(os.path.join(site_resources,"previews.html"),"w")) as previews_file:
      previews_file.write(html)

  with(open(os.path.join(site_resources,"sprites.css"),"w")) as css_file:
      css_file.write(css)

  # make css-able image
  print("Making CSS-able image")
  width = (len(thumbs) + 1) * 16
  height = 16
  png = Image.new("RGBA", (width, height))
  png.putalpha(0)
  x = 0
  y = 0
  i = 1
  n = len(thumbs)
  maxd = len(str(n))

  for thumb in sorted(thumbs, key=lambda s: str.lower(s or "").strip()):
      png, x = add_thumb(thumb, png, height, x, y)
      print("Adding %*d/%*d [%-*s]" %
        (
          maxd,i,
          maxd,n,
          maxs,os.path.basename(thumb)
        )
      )
      i += 1

  png.save(os.path.join(site_resources,"sheets","previews","sprites." + VERSION + ".png"),"png")

if __name__ == "__main__":
  create_previews()
