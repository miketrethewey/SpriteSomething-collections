import io
import logging
import os
import struct

class ZSPR(object):
    default_palette = [255, 127, 126, 35, 183, 17, 158, 54, 165, 20, 255, 1, 120, 16, 157,
                       89, 71, 54, 104, 59, 74, 10, 239, 18, 92, 42, 113, 21, 24, 122,
                       255, 127, 126, 35, 183, 17, 158, 54, 165, 20, 255, 1, 120, 16, 157,
                       89, 128, 105, 145, 118, 184, 38, 127, 67, 92, 42, 153, 17, 24, 122,
                       255, 127, 126, 35, 183, 17, 158, 54, 165, 20, 255, 1, 120, 16, 157,
                       89, 87, 16, 126, 69, 243, 109, 185, 126, 92, 42, 39, 34, 24, 122,
                       255, 127, 126, 35, 218, 17, 158, 54, 165, 20, 255, 1, 120, 16, 151,
                       61, 71, 54, 104, 59, 74, 10, 239, 18, 126, 86, 114, 24, 24, 122]

    default_glove_palette = [246, 82, 118, 3]

    def __init__(self, filename):
        with open(filename, 'rb') as file:
            filedata = bytearray(file.read())
        self.name = os.path.basename(filename)
        self.filename = self.name
        self.slug = self.filename.split(".")
        self.slug.pop()
        self.slug = ".".join(self.slug)
        self.author_name = None
        self.valid = True
        if len(filedata) == 0x7000:
            # sprite file with graphics and without palette data
            self.sprite = filedata[:0x7000]
            self.palette = list(self.default_palette)
            self.glove_palette = list(self.default_glove_palette)
        elif len(filedata) == 0x7078:
            # sprite file with graphics and palette data
            self.sprite = filedata[:0x7000]
            self.palette = filedata[0x7000:]
            self.glove_palette = filedata[0x7036:0x7038] + filedata[0x7054:0x7056]
        elif len(filedata) == 0x707C:
            # sprite file with graphics and palette data including gloves
            self.sprite = filedata[:0x7000]
            self.palette = filedata[0x7000:0x7078]
            self.glove_palette = filedata[0x7078:]
        elif len(filedata) in [0x100000, 0x200000]:
            # full rom with patched sprite, extract it
            self.sprite = filedata[0x80000:0x87000]
            self.palette = filedata[0xDD308:0xDD380]
            self.glove_palette = filedata[0xDEDF5:0xDEDF9]
        elif filedata.startswith(b'ZSPR'):
            result = self.parse_zspr(filedata, 1)
            if result is None:
                self.valid = False
                return
            (sprite, palette, self.name, self.author_name) = result
            if len(sprite) != 0x7000:
                self.valid = False
                return
            self.sprite = sprite
            if len(palette) == 0:
                self.palette = list(self.default_palette)
                self.glove_palette = list(self.default_glove_palette)
            elif len(palette) == 0x78:
                self.palette = palette
                self.glove_palette = list(self.default_glove_palette)
            elif len(palette) == 0x7C:
                self.palette = palette[:0x78]
                self.glove_palette = palette[0x78:]
            else:
                self.valid = False
        else:
            self.valid = False

    @staticmethod
    def default_link_sprite():
        return get_sprite_from_name('Link')

    def decode8(self, pos):
        arr = [[0 for _ in range(8)] for _ in range(8)]
        for y in range(8):
            for x in range(8):
                position = 1<<(7-x)
                val = 0
                if self.sprite[pos+2*y] & position:
                    val += 1
                if self.sprite[pos+2*y+1] & position:
                    val += 2
                if self.sprite[pos+2*y+16] & position:
                    val += 4
                if self.sprite[pos+2*y+17] & position:
                    val += 8
                arr[y][x] = val
        return arr

    def decode16(self, pos):
        arr = [[0 for _ in range(16)] for _ in range(16)]
        top_left = self.decode8(pos)
        top_right = self.decode8(pos+0x20)
        bottom_left = self.decode8(pos+0x200)
        bottom_right = self.decode8(pos+0x220)
        for x in range(8):
            for y in range(8):
                arr[y][x] = top_left[y][x]
                arr[y][x+8] = top_right[y][x]
                arr[y+8][x] = bottom_left[y][x]
                arr[y+8][x+8] = bottom_right[y][x]
        return arr

    def parse_zspr(self, filedata, expected_kind):
        logger = logging.getLogger('')
        headerstr = "<4xBHHIHIHH6x"
        headersize = struct.calcsize(headerstr)
        if len(filedata) < headersize:
            return None
        (version, csum, icsum, sprite_offset, sprite_size, palette_offset, palette_size, kind) = struct.unpack_from(headerstr, filedata)
        if version not in [1]:
            logger.error('Error parsing ZSPR file: Version %g not supported', version)
            return None
        if kind != expected_kind:
            return None

        stream = io.BytesIO(filedata)
        stream.seek(headersize)

        def read_utf16le(stream):
            "Decodes a null-terminated UTF-16_LE string of unknown size from a stream"
            raw = bytearray()
            while True:
                char = stream.read(2)
                if char in [b'', b'\x00\x00']:
                    break
                raw += char
            return raw.decode('utf-16_le')

        sprite_name = read_utf16le(stream)
        author_name = read_utf16le(stream)

        # Ignoring the Author Rom name for the time being.

        real_csum = sum(filedata) % 0x10000
        if real_csum != csum or real_csum ^ 0xFFFF != icsum:
            logger.warning('ZSPR file has incorrect checksum. It may be corrupted.')

        sprite = filedata[sprite_offset:sprite_offset + sprite_size]
        palette = filedata[palette_offset:palette_offset + palette_size]

        if len(sprite) != sprite_size or len(palette) != palette_size:
            logger.error('Error parsing ZSPR file: Unexpected end of file')
            return None

        return (sprite, palette, sprite_name, author_name)

    def decode_palette(self):
        "Returns the palettes as an array of arrays of 15 colors"
        def array_chunk(arr, size):
            return list(zip(*[iter(arr)] * size))
        def make_int16(pair):
            return pair[1]<<8 | pair[0]
        def expand_color(i):
            return ((i & 0x1F) * 8, (i>>5 & 0x1F) * 8, (i>>10 & 0x1F) * 8)
        raw_palette = self.palette
        if raw_palette is None:
            raw_palette = Sprite.default_palette
        # turn palette data into a list of RGB tuples with 8 bit values
        palette_as_colors = [expand_color(make_int16(chnk)) for chnk in array_chunk(raw_palette, 2)]

        # split into palettes of 15 colors
        return array_chunk(palette_as_colors, 15)
