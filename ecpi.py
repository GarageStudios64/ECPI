from PIL import Image
import sys, math
def getbytes(x):
    y = (x.bit_length() + 7) // 8
    if y == 0:
        return x.to_bytes(1, 'big')
    else:
        return x.to_bytes(y, 'big')
def write_new_ecpi(filename, size, width, height, palette, list):
    """Creates a new Efficient Colour Palette Image file."""
    sys.set_int_max_str_digits(2147483647)
    MAGIC = b'ECPI'
    SIZE = getbytes(size)
    WIDTH = getbytes(width)
    HEIGHT = getbytes(height)
    LIST = ''
    if not filename.endswith(".ecpi"):
        print("Not a valid ECPI file")
    with open(filename, 'wb') as f:
        f.write(MAGIC)
        for inte in SIZE:
            f.write(b'\x01')
            f.write(inte.to_bytes(1, 'big'))
        for inte in WIDTH:
            f.write(b'\x02')
            f.write(inte.to_bytes(1, 'big'))
        for inte in HEIGHT:
            f.write(b'\x03')
            f.write(inte.to_bytes(1, 'big'))
        for key, value in palette.items():
            f.write(b'\x10')
            for inte in getbytes(key):
                f.write(b'\x12')
                f.write(inte.to_bytes(1, 'big'))
            f.write(b'\x13')
            f.write(value[0].to_bytes(1, 'big'))
            f.write(value[1].to_bytes(1, 'big'))
            f.write(value[2].to_bytes(1, 'big'))
            f.write(b'\x11')
        for item in list:
            LIST += format(item, '0' + str(size) + 'b')
        f.write(b'\x20')
        f.write(int(LIST, 2).to_bytes((len(LIST) + 7) // 8, 'big'))
def convert_from_ecpi(filename, filetype):
    """Reads image data from an Effcient Colour Palette Image file."""
    if not filename.endswith(".ecpi"):
        print("Not a valid ECPI file")
    with open(filename, 'rb') as f:
        size = b''
        width = b''
        height = b''
        palette = {}
        list = b''
        fbo = b''
        palmode = False
        tempindex = b''
        temprgb = [b'', b'', b'']
        magic = f.read(4)
        if magic != b'ECPI':
            raise ValueError("Not a valid ECPI file")
        f.seek(0, 2)
        end = f.tell()
        f.seek(4, 0)
        while f.tell() < end:
            datatype = f.read(1)
            if palmode:
                match datatype:
                    case b'\x12':
                        tempindex += f.read(1)
                    case b'\x13':
                        temprgb[0] += f.read(1)
                        temprgb[1] += f.read(1)
                        temprgb[2] += f.read(1)
                    case b'\x11':
                        palette[tempindex] = temprgb
                        tempindex = b''
                        temprgb = [b'', b'', b'']
                        palmode = False
                    case _:
                        print("Not a valid ECPI file")
            else:
                match datatype:
                    case b'\x01':
                        size += f.read(1)
                    case b'\x02':
                        width += f.read(1)
                    case b'\x03':
                        height += f.read(1)
                    case b'\x10':
                        palmode = True
                    case b'\x20':
                        list = f.read()
                    case _:
                        print("Not a valid ECPI file")
    s = int.from_bytes(size, 'big')
    w = int.from_bytes(width, 'big')
    h = int.from_bytes(height, 'big')
    f = (w*h*s)%8
    bits = ''.join(f'{byte:08b}' for byte in list)
    bits = bits[f:]
    l = []
    for i in range(round(len(bits)/s)):
        l.append(int(bits[s*i:(s*i)+s], 2))
    p = {}
    for k, v in palette.items():
        p[int.from_bytes(k, 'big')] = [int.from_bytes(v[0], 'big'), int.from_bytes(v[1], 'big'), int.from_bytes(v[2], 'big')]
    img = Image.new('RGB', (w, h), (0, 0, 0))
    index = 0
    for x in range(w):
        for y in range(h):
            img.putpixel((x, y), tuple(p[l[(x*w)+y]]))
    img.save(filename.rsplit('.', 1)[0] + '.' + filetype)
    img.show()
def convert_to_ecpi(path):
    """Creates a new Efficient Colour Palette Image file from another file."""
    with Image.open(path) as img:
        filename = img.filename.rsplit('.', 1)[0] + '.ecpi'
        width, height = img.size
        palette = {}
        list = []
        for x in range(width):
            for y in range(height):
                p = img.getpixel((x, y))
                if p in palette.values():
                    pass
                else:
                    palette[len(palette)] = p
                for key, value in palette.items():
                    if value == p:
                        list.append(key)
        size = math.ceil(math.log2(max(palette)+1))
        write_new_ecpi(filename, size, width, height, palette, list)
i1 = input('Welcome to the ECPI terminal tools. What would you like to do?\n(convert (T)o, convert (F)rom, or exit (any))').lower()
if i1 == 't':
    i2 = input('File path:\n(can be local or global)\n(enter nothing to exit)\n')
    if i2 != '':
        convert_to_ecpi(i2)
    else:
        sys.exit;
elif i1 == 'f':
    i2 = input('File path:\n(can be local or global)\n(enter nothing to exit)\n')
    if i2 != '':
        i3 = input('File type:\n(extension, no full stop/period)\n(enter nothing to exit)\n')
        if i3 != '':
            convert_from_ecpi(i2, i3)
        else:
            sys.exit(0)
    else:
        sys.exit(0)
else:
    sys.exit(0)