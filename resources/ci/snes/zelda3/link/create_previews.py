# While iterating through sprite files, this will generate the preview images to serve to process_previews.py

import io
import math
import os

from glob import glob
from PIL import Image
from ZSPR import ZSPR

local_resources = os.path.join(".","resources","ci","snes","zelda3","link")
site_resources = os.path.join(".","snes","zelda3","link")

def add_thumb(thumb,png,height,x,y):
    thisThumb = Image.open(thumb).resize((16,height),0)
    png.paste(thisThumb,(x,y))
    return png, x + 16

def get_image_for_sprite(sprite):
    if not sprite.valid:
        return None
    # default dims are 16x24
    height = 24
    width = 16

    def draw_sprite_into_gif(add_palette_color, set_pixel_color_index):

        def drawsprite(spr, pal_as_colors, offset):
            for y, row in enumerate(spr):
                for x, pal_index in enumerate(row):
                    if pal_index:
                        color = pal_as_colors[pal_index - 1]
                        set_pixel_color_index(x + offset[0], y + offset[1], color)

        add_palette_color(16, (40, 40, 40))
        shadow = [
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        ]

        drawsprite(shadow, [16], (2, 17))

        palettes = sprite.decode_palette()
        for i in range(15):
            add_palette_color(i + 1, palettes[0][i])

        body = sprite.decode16(0x4C0)
        drawsprite(body, list(range(1, 16)), (0, 8))
        head = sprite.decode16(0x40)
        drawsprite(head, list(range(1, 16)), (0, 0))

    def make_gif(callback):
        gif_header = b'GIF89a'

        gif_lsd = bytearray(7)
        gif_lsd[0] = width
        gif_lsd[2] = height
        gif_lsd[4] = 0xF4  # 32 color palette follows.  transparant + 15 for sprite + 1 for shadow=17 which rounds up to 32 as nearest power of 2
        gif_lsd[5] = 0  # background color is zero
        gif_lsd[6] = 0  # aspect raio not specified
        gif_gct = bytearray(3 * 32)

        gif_gce = bytearray(8)
        gif_gce[0] = 0x21  # start of extention blocked
        gif_gce[1] = 0xF9  # identifies this as the Graphics Control extension
        gif_gce[2] = 4  # we are suppling only the 4 four bytes
        gif_gce[3] = 0x01  # this gif includes transparency
        gif_gce[4] = gif_gce[5] = 0  # animation frrame delay (unused)
        gif_gce[6] = 0  # transparent color is index 0
        gif_gce[7] = 0  # end of gif_gce
        gif_id = bytearray(10)
        gif_id[0] = 0x2c
        # byte 1,2 are image left. 3,4 are image top both are left as zerosuitsamus
        gif_id[5] = width
        gif_id[7] = height
        gif_id[9] = 0  # no local color table

        gif_img_minimum_code_size = bytes([7])  # we choose 7 bits, so that each pixel is represented by a byte, for conviennce.

        clear = 0x80
        stop = 0x81

        unchunked_image_data = bytearray(height * (width + 1) + 1)
        # we technically need a Clear code once every 125 bytes, but we do it at the start of every row for simplicity
        for row in range(height):
            unchunked_image_data[row * (width + 1)] = clear
        unchunked_image_data[-1] = stop

        def add_palette_color(index, color):
            gif_gct[3 * index] = color[0]
            gif_gct[3 * index + 1] = color[1]
            gif_gct[3 * index + 2] = color[2]

        def set_pixel_color_index(x, y, color):
            unchunked_image_data[y * (width + 1) + x + 1] = color

        callback(add_palette_color, set_pixel_color_index)

        def chunk_image(img):
            for i in range(0, len(img), 255):
                chunk = img[i:i + 255]
                yield bytes([len(chunk)])
                yield chunk

        gif_img = b''.join([gif_img_minimum_code_size] + list(chunk_image(unchunked_image_data)) + [b'\x00'])

        gif = b''.join([gif_header, gif_lsd, gif_gct, gif_gce, gif_id, gif_img, b'\x3b'])

        return gif

    gif_data = make_gif(draw_sprite_into_gif)
    image = Image.open(io.BytesIO(gif_data))

    # blow up by 400%
    zoom = 4
    return image.resize((image.size[0] * zoom, image.size[1] * zoom), 0)

sprites = []

# get ZSPRs
print("Getting ZSPRs")
for file in glob(os.path.join(site_resources,"sheets","*.zspr")):
    if os.path.isfile(file):
        sprites.append(ZSPR(file))
# sort ZSPRs
sprites.sort(key=lambda s: str.lower(s.name or "").strip())
print()
print("Wait a little bit, dude, there's %d sprites." % (len(sprites)))
print()

# make previews for ZSPRs (400% size)
print("Processing previews")
for sprite in sprites:
    image = get_image_for_sprite(sprite)
    if image is None:
        continue
    image.save(os.path.join(site_resources,"sheets","thumbs",sprite.slug + ".png"),"png")

VERSION = ""
with(open(os.path.join(".","meta","manifests","app_version.txt"),"r")) as appversion:
    VERSION = appversion.readline().strip()

with(open(os.path.join(".","commit.txt"),"w")) as commit:
    commit.write("Update Site to v" + VERSION)

# get the thumbnails (400%) we made
thumbs = glob(os.path.join(site_resources,"sheets","thumbs","*.png"))

# get the new ones and make a class image
print("Making class image for: " + VERSION)
zoom = 4
width = 6 * 16 * zoom
height = (math.ceil(len(thumbs) / 6)) * 24 * zoom
png = Image.new("RGBA", (width, height))
png.putalpha(0)
x = 0
y = 0
for thumb in sorted(thumbs, key=lambda s: str.lower(s or "").strip()):
    thisThumb = Image.open(thumb)
    png.paste(thisThumb,(x,y))
    x += 16 * zoom
    if x >= width:
        x = 0
        y += 24 * zoom
png.save(os.path.join(site_resources,"sheets","previews","sprites.class." + VERSION + ".png"),"png")

# make css-able image
print("Making CSS-able image for: " + VERSION)
width = (len(thumbs) + 2) * 16
height = 24
png = Image.new("RGBA", (width, height))
png.putalpha(0)
x = 0
y = 0
i = 1
n = len(thumbs)
maxd = len(str(n))

# Add Random Sprite
png, x = add_thumb(os.path.join(local_resources,"sheets","random.png"), png, height, x, y)

for thumb in sorted(thumbs, key=lambda s: str.lower(s or "").strip()):
    png, x = add_thumb(thumb, png, height, x, y)
    print("Adding to css-able image: %*d/%*d %s" %
      (
        maxd,i,
        maxd,n,
        os.path.basename(thumb)
      )
    )
    i += 1

# Add Custom Sprite
png, x = add_thumb(os.path.join(local_resources,"sheets","custom.png"), png, height, x, y)

png.save(os.path.join(site_resources,"sheets","previews","sprites." + VERSION + ".png"),"png")
