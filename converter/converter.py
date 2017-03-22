#! /usr/bin/env python

import os
import sys
import struct
import io

from IPython import embed


class Field:
    def __init__(self, name):
        self.name = name
        self.size = None
        self.type = None

    def __str__(self):
        return "Field(name={}, size={}, type={})".format(self.name, self.size, self.type)
    __repr__ = __str__


class Converter:
    def __init__(self, path_origin, path_convert):
        self.basename_ori, self.extension_ori = self.get_name(path_origin)
        self.basename_conv, self.extension_conv = self.get_name(path_convert)

        self.path_ori = path_origin
        self.path_conv = path_convert

        self._rgb = None
        self._decode = None

        self.points = []
        self.fields = []

        print("Reading: ", self.path_ori)
        if self.extension_ori == ".pcd":
            self.load_pcd()
        elif self.extension_ori == ".ply":
            self.load_ply()
        elif self.extension_ori == ".xyz":
            self.load_xyz()
        else:
            print("Error: Unknown file extension")

        self.decode_points()
        self.convert()

    def get_name(self, path):
        """
        Returns basename and extension of path
        """
        return os.path.splitext(os.path.basename(path))

    def load_pcd(self):
        _ascii = False
        _binary = False
        _bcompressed = False

        points = 0
        #print(self.path_ori)
        with open(self.path_ori, "rb") as f:
            while True:
                line = f.readline()
                if line.startswith(b"#"):
                    pass
                elif line.startswith(b"VERSION"):
                    pass
                elif line.startswith(b"FIELDS"):
                    line = line.strip()
                    line = line.split(b" ")
                    for idx, field in enumerate(line):
                        if idx != 0:
                            self.fields.append(Field(field))
                elif line.startswith(b"SIZE"):
                    line = line.strip()
                    line = line.split(b" ")
                    for idx, size in enumerate(line):
                        if idx != 0:
                            self.fields[idx-1].size = int(size)
                elif line.startswith(b"TYPE"):
                    line = line.strip()
                    line = line.split(b" ")
                    for idx, tmp in enumerate(line):
                        if idx != 0:
                            self.fields[idx-1].type = tmp 
                elif line.startswith(b"COUNT"):
                    pass
                elif line.startswith(b"WIDTH"):
                    pass
                elif line.startswith(b"HEIGHT"):
                    pass
                elif line.startswith(b"VIEWPOINT"):
                    pass
                elif line.startswith(b"POINTS"):
                    line = line.split(b" ")
                    points = int(line[1])
                elif line.startswith(b"DATA"):
                    line = line.strip()
                    line = line.split(b" ")
                    if line[1] == b"ascii":
                        _ascii = True
                    elif line[1] == b"binary":
                        _binary = True
                    elif line[1] == b"binary_compressed":
                        _bcompressed = True
                        print("Error: binary_compressed format not supported")
                        sys.exit(1)
                    else:
                        print("Error: unknown pcd file format")
                        print(line[1])
                        sys.exit(1)
                    break

            if _ascii:
                for line in f:
                    pt = line.split()
                    self.points.append(pt)

            if _binary:
                data = f.read()
            if _bcompressed:
                import lzf
                compressed_data = f.read()
                data = lzf.decompress(compressed_data, len(compressed_data))

            #print("Length of data: ", points)
            #print("Fields: ", self.fields)

        if _binary or _bcompressed:
            buf = io.BytesIO(data)
            fmt = ""
            size = 0
            for f in self.fields:
                if f.type == b"F" and f.size == 4:
                    fmt += "f" 
                elif f.type == b"F" and f.size == 8:
                    fmt += "d" 
                elif f.type == b"I" and f.size == 1:
                    fmt += "b" 
                elif f.type == b"I" and f.size == 2:
                    fmt += "h" 
                elif f.type == b"I" and f.size == 4:
                    fmt += "i" 
                elif f.type == b"U" and f.size == 1:
                    fmt += "B" 
                elif f.type == b"U" and f.size == 2:
                    fmt += "H" 
                elif f.type == b"U" and f.size == 4:
                    fmt += "I" 
                else:
                    print("Uknown type: ", f.type)
                size += f.size

            if len(self.fields) > 3 and self.fields[3].name == "rgb":
                self._rgb = True
            for _ in range(points):
                pt = struct.unpack(fmt, buf.read(size))
                embed()
                break
                self.points.append(pt)

    def load_ply(self):
        _ascii = False
        _binary = False

        points = 0
        with open(self.path_ori, "rb") as f:
            while True:
                line = f.readline()
                if line.startswith(b"ply"):
                    pass
                elif line.startswith(b"format"):
                    line = line.strip()
                    line = line.split(b" ")
                    ft = line[1]

                    if ft == b"ascii":
                        _ascii = True
                    elif ft == b'binary_little_endian':
                        _binary = True
                        _endianchar = '<'
                    elif ft == b'binary_big_endian':
                        _binary = True
                        _endianchar = '>'

                elif line.startswith(b"comment"):
                    pass
                elif line.startswith(b"element"):
                    line = line.split(b" ")
                    points = int(line[-1])
                elif line.startswith(b"property"):
                    line = line.strip()
                    line = line.split(b" ")

                    self.fields.append(Field(line[2]))
                    self.fields[-1].type = line[1]
                    self.fields[-1].size = 4

                elif line.startswith(b"end_header"):
                    pass
                    break

            if _ascii:
                for line in f:
                    pt = line.split()
                    self.points.append(pt)

            if _binary:
                data = f.read()

        if _binary:
            buf = io.BytesIO(data)
            fmt = _endianchar
            size = 0
            for f in self.fields:
                if f.type == b"float" and f.size == 4:
                    fmt += "f"
                else:
                    print("Uknown type: ", f.type)
                size += f.size
            for _ in range(points):
                pt = struct.unpack(fmt, buf.read(size))
                self.points.append(pt)

    def load_xyz(self):
        with open(self.path_ori, 'rb') as f:
            for line in f:
                xyz = line.split()
                if len(xyz) > 3:
                    self._rgb = True
                if xyz[0] != b'nan':
                    self.points.append(xyz)

    def convert(self):
        path = self.path_conv
        print('Saving point cloud to', path)
        header = self.generate_header()
        with open(path, "wb") as f:
            f.write(header.encode())
            for pt in self.points:
                if not self._rgb:
                    f.write("{} {} {}\n".format(pt[0], pt[1], pt[2]).encode())
                else:
                    #TODO: calculate rgb value from three RGB values
                    # pt[4] = TODO rgb
                    #f.write("{} {} {} {}\n".format(pt[0], pt[1], pt[2], pt[3]).encode())
                    f.write("{} {} {}\n".format(pt[0], pt[1], pt[2]).encode())

    def generate_header(self):
        if self.extension_conv == '.ply':
            header = """ply
format ascii 1.0
comment : pcd2ply
element vertex {}
property float x
property float y
property float z
end_header\n""".format(len(self.points))

        elif self.extension_conv == '.pcd':
            if self._rgb:
                #TODO calculate rgb value from three R G B values
                #fields = 'x y z rgb'
                #size = '4 4 4 4'
                #typ = 'F F F 4'
                fields = 'x y z'
                size = '4 4 4'
                typ = 'F F F'
            else:
                fields = 'x y z'
                size = '4 4 4'
                typ = 'F F F'

            header = """# .PCD v0.7 - PointCloud Data file format
VERSION 0.7
FIELDS {0}
SIZE {1}
TYPE {2}
WIDTH {3}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {4}
DATA ascii\n""".format(fields, size, typ, len(self.points), len(self.points))

        elif self.extension_conv == '.xyz':
            header = ''

        else:
            print("Error: Can't convert to {}".format(self.extension_conv))
            sys.exit(1)

        return header

    def decode_points(self):
        for num, pt in enumerate(self.points):
            self.points[num] = [pt[0].decode(), pt[1].decode(), pt[2].decode()]

def main():
    if len(sys.argv) != 3:
        print("usage: converter <original.format1> <converted.format2>")
        print("formats supported: .ply, .pcd, .xyz, .xyz+RGB")
        sys.exit(1)
    c = Converter(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
