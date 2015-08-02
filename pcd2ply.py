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
        return "Field(name={}, size={}, type={}".format(self.name, self.size, self.type)
    __repr__ = __str__


class Converter:
    def __init__(self, path):
        self.path = path
        self.basename, self.extension = os.path.splitext(os.path.basename(self.path))
        print("basename is", self.basename)
        self.points = []
        self.fields = []

        self.load()

    def load(self):
        points = 0
        print("Reading: ", self.path)
        with open(self.path, "rb") as f:
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
                    if line[1] != b"binary":
                        print("Error only binary file format supported")
                        print(line[1])
                        sys.exit(1)
                    break
            data = f.read()
        print("Length of data: ", points)
        print("Fields: ", self.fields)
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
        #embed()
        for _ in range(points):
            pt = struct.unpack(fmt, buf.read(size))
            self.points.append(pt)

    def to_ply(self):
        header = """ply
format ascii 1.0
comment : pcd2ply 
element vertex {}
property float x
property float y
property float z
end_header\n""".format(len(self.points))
        path = self.basename + ".ply"
        print('Saving point cloud to', path)
        with open(path, "wb") as f:
            f.write(header.encode())
            for pt in self.points:
                f.write("{} {} {}\n".format(pt[0], pt[1], pt[2]).encode())

        



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: pcd2ply pcdfile")
        sys.exit(1)
    c = Converter(sys.argv[1])
    c.to_ply()

