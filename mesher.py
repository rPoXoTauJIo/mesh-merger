import os
import struct

import bf2

# https://github.com/ByteHazard/BfMeshView/blob/master/source/modStdMesh.bas


class StdMeshFile:

    class __Filestruct:  # pure containers

        class __Header:

            def __init__(self):
                self.u1 = None
                self.version = None
                self.u3 = None
                self.u4 = None
                self.u5 = None
        
        class __Unknown:

            def __init__(self):
                self.u2 = None
        
        class __Bf2Geom:
        
            class __Lod():
            
                class __Bounds():
                
                    def __init__(self):
                        self.min = None
                        self.max = None
                        self.pivot = None
                
                def __init__(self):
                    self.bounds = self.__Bounds()
                    self.rignum = None
            
            def __init__(self):
                self.num = None
                self.lodnum = None
                self.lod = self.__Lod()
        
        class __Vertattrib:
            
            def __init__(self):
                self.num = None

        def __init__(self):
            self.header = self.__Header()
            self.unknown2 = self.__Unknown()
            self.bf2geom = self.__Bf2Geom()
            self.vertattrib = self.__Vertattrib()

    def __init__(self, filepath):
        self.filepath = filepath
        self.filedata = None
        self.struct = self.__Filestruct()

    def get_filedata(self):
        if self.filedata is None:
            with open(self.filepath, 'rb') as fo:
                self.filedata = fo.read()

        return self.filedata

    def read_header(self):
        start = 0
        # u1 As long          '0
        # version As long     '10 for most bundledmesh, 6 for some bundledmesh, 11 for staticmesh
        # u3 As long          '0
        # u4 As long          '0
        # u5 As long          '0
        format = 'l l l l l'
        data_struct = struct.Struct(format)
        data_size = struct.calcsize(format)

        tail = data_size

        self.struct.header.u1, self.struct.header.version, self.struct.header.u3, self.struct.header.u4, self.struct.header.u5 = data_struct.unpack(self.get_filedata()[start:tail])
        return tail

    def read_unknown2(self):
        start = self.read_header()
        # u1 As char          'always 0?
        format = 'b'
        data_struct = struct.Struct(format)
        data_size = struct.calcsize(format)

        tail = start + data_size

        self.struct.unknown2.u1 = data_struct.unpack(self.get_filedata()[start:tail])[0]
        return tail

    def read_bf2geom_num(self):
        start = self.read_unknown2()
        # geomnum As l
        format = 'l'
        data_struct = struct.Struct(format)
        data_size = struct.calcsize(format)

        tail = start + data_size

        self.struct.bf2geom.num = data_struct.unpack(self.get_filedata()[start:tail])[0]
        return tail

    def read_bf2geom_lodnum(self):
        start = self.read_bf2geom_num()
        # geomnum As l * geomnum
        format = ' '.join(['l' for _ in range(self.struct.bf2geom.num)])
        data_struct = struct.Struct(format)
        data_size = struct.calcsize(format)

        tail = start + data_size

        self.struct.bf2geom.lodnum = data_struct.unpack(self.get_filedata()[start:tail])[0]
        return tail

    def read_vertattrib_num(self):
        start = self.read_bf2geom_lodnum()
        # vertattribnum As l
        format = 'l'
        data_struct = struct.Struct(format)
        data_size = struct.calcsize(format)

        tail = start + data_size

        self.struct.vertattrib.num = data_struct.unpack(self.get_filedata()[start:tail])[0] - 1
        return tail












