#! /usr/bin/env python

import os
import sys
import struct
import io

import numpy as np

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
    def __init__(self):

        self._rgb = None
        self._rgba = None
        self._decode = None

        self.points = []
        self.fields = []

    def load_points(self, path):
        self.points = []
        self.fields = []

        print("Reading: ", path)
        name, extension = self._get_name(path)
        if extension == ".pcd":
            self._load_pcd(path)
        elif extension == ".ply":
            self._load_ply(path)
        elif extension == ".zdf":
            self._load_zdf(path)
        elif extension == ".xyz":
            self._load_xyz(path)
        elif extension in [".stl", ".STL"]:
            self._load_stl(path)
        elif extension == ".a3d":
            # Scorpion vision format
            self._load_a3d(path)
        else:
            print("Error: Unknown file extension {}".format(extension))
            sys.exit(1)

        self._decode_points()

        for field in self.fields:
            if field.name == 'red' and self._rgba == None:
                self._rgb = True
            elif field.name == 'alpha':
                self._rgba = True
                self._rgb = False

    def _get_name(self, path):
        """
        Returns basename and extension of path
        """
        return os.path.splitext(os.path.basename(path))

    def _load_pcd(self, path):
        _ascii = False
        _binary = False
        _bcompressed = False

        points = 0
        with open(path, "rb") as f:
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
                break
                self.points.append(pt)

    def _load_ply(self, path):
        _ascii = False
        _binary = False

        points = 0
        with open(path, "rb") as f:
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

                    self.fields.append(Field(line[2].decode()))
                    self.fields[-1].type = line[1].decode()
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

    def _load_zdf(self, path):
        from netCDF4 import Dataset

        f = Dataset(path,'r')
        xyz = f['data']['pointcloud'][:,:,:]
        img = f['data']['rgba_image'][:,:,:]
        f.close()

        pc = np.dstack([xyz, img])
        pc_reshaped = pc.reshape(pc.shape[0]*pc.shape[1], pc.shape[2])

        self._rgba = True

        for pt in pc_reshaped:
            if not np.isnan(pt[0]):
                self.points.append(pt)
            else:
                self.points.append([0,0,0,0,0,0,255])

    def _load_xyz(self, path):
        import ast

        with open(path, 'rb') as f:
            for line in f:
                xyz = line.split()
                if xyz[0] != b'nan':
                    self.points.append([float(val) for val in xyz])
                else:
                    self.points.append(len(xyz)*[0])

            if len(xyz) == 6:
                self._rgb = True
            elif len(xyz) == 7:
                self._rgba = True

    def _load_stl(self, path):
        from stl import mesh

        stlmesh = mesh.Mesh.from_file(path)
        vects = stlmesh.data["vectors"]
        self.points = vects.reshape(vects.shape[0]*vects.shape[1], vects.shape[2])

    def _load_a3d(self, path):
        import ast

        with open(path, 'r') as f:
            for line in f:
                line = line.replace("\n", "")
                xyzraw = line.split(",")
                xyz = "[{}.{}, {}.{}, {}.{}]".format(xyzraw[0], xyzraw[1], \
                                                     xyzraw[2], xyzraw[3], \
                                                     xyzraw[4], xyzraw[5])
                self.points.append(ast.literal_eval(xyz))

    def convert(self, path):
        print('Saving point cloud to', path)
        name, extension = self._get_name(path)
        header = self._generate_header(extension)

        with open(path, "wb") as f:
            f.write(header.encode())
            for pt in self.points:
                if self._rgb:
                    f.write("{} {} {} {} {} {}\n".format(\
                            pt[0], pt[1], pt[2],\
                            int(pt[3]), int(pt[4]), int(pt[5])).encode())

                elif self._rgba:
                    f.write("{} {} {} {} {} {} {}\n".format(\
                            pt[0], pt[1], pt[2],\
                            int(pt[3]), int(pt[4]), int(pt[5]), int(pt[6])).encode())

                else:
                    f.write("{} {} {}\n".format(pt[0], pt[1], pt[2]).encode())

    def _generate_header(self, extension):
        if extension == '.ply':

            properties = "property float x\n" \
                       + "property float y\n" \
                       + "property float z\n"

            if self._rgb:
                properties += "property uchar red\n" \
                            + "property uchar green\n" \
                            + "property uchar blue\n"
            elif self._rgba:
                properties += "property uchar red\n" \
                            + "property uchar green\n" \
                            + "property uchar blue\n" \
                            + "property uchar alpha\n"

            header = 'ply\n' \
                   + "format ascii 1.0\n" \
                   + "comment https://github.com/SintefRaufossManufacturing/convertcloud\n" \
                   + "element vertex {}\n".format(len(self.points)) \
                   + properties \
                   + "end_header\n"

        elif extension == '.pcd':
            fields = "x y z"
            size = "4 4 4"
            typ = "F F F"
            if self._rgb or self._rgba:
                #TODO calculate rgb value from three R G B values (bitshift)
                fields += " r g b"
                size += " 4 4 4"
                typ += " 4 4 4"
            elif self._rgba:
                fields += " r g b a"
                size += " 4 4 4 4"
                typ += " 4 4 4 4"

            header = "# .PCD v0.7 - PointCloud Data file format\n" \
                   + "VERSION 0.7\n" \
                   + "FIELDS {}\n".format(fields) \
                   + "SIZE {}\n".format(size) \
                   + "TYPE {}\n".format(typ) \
                   + "WIDTH {}\n".format(len(self.points)) \
                   + "HEIGHT 1\n" \
                   + "VIEWPOINT 0 0 0 1 0 0 0\n" \
                   + "POINTS {}\n".format(len(self.points)) \
                   + "DATA ascii\n"

        elif extension == '.xyz':
            header = ''

        else:
            print("Error: Can't convert to {}".format(extension))
            sys.exit(1)

        return header

    def _decode_points(self):
        for num, point in enumerate(self.points):
            if isinstance(point[0], bytes):
                self.points[num] = [val.decode() for val in point]
            else:
                break

        self.points = np.array(self.points).astype("float32")
                
            
def main():
    if len(sys.argv) != 3:
        print("usage: converter <original.format1> <converted.format2>")
        print("formats supported: .ply, .pcd, .xyz, .zdf")
        sys.exit(1)

    c = Converter()

    c.load_points(sys.argv[1])
    c.convert(sys.argv[2])

if __name__ == "__main__":
    main()
