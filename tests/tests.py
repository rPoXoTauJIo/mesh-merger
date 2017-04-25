import unittest
import unittest.mock as mock
import tempfile
import os

import bf2
import mesher


class TestMod(unittest.TestCase):
    
    @mock.patch('os.getcwd')
    def test_can_find_mod_root(self, mock_function):
        mocked_mod_root = os.sep.join(['games', 'PRGame', 'mods', 'pr'])
        mocked_work_dir = os.sep.join(['games', 'PRGame', 'mods', 'pr', 'readme'])
        mock_function.return_value = mocked_work_dir

        mod = bf2.Mod()
        self.assertTrue(mod.find_mod_root() == mocked_mod_root)

    def test_mod_init_with_mod_root(self):
        mod = bf2.Mod()
        self.assertTrue('mods' in mod.root.split(os.sep))

    def test_can_get_object_path(self):
        test_object_name = 'faction_type_name_variant'
        test_folder = os.path.join('objects', 'vehicles', 'land')
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_mod = os.path.join(temp_dir, test_folder)
            os.makedirs(temp_mod)
            with tempfile.NamedTemporaryFile('w', suffix='.con', dir=temp_mod, delete=False) as confile:
                confile.write('ObjectTemplate.create PlayerControlObject ' + test_object_name)
                confile.close()
                mod = bf2.Mod()
                mod.root = temp_dir
                self.assertTrue(mod.get_object_path(test_object_name) == os.path.join(temp_mod, test_object_name, confile.name))

class TestStdMesh(unittest.TestCase):

    def setUp(self):
        # NOTE: THIS IS VERY SPECIFIC TESTS FOR TEST MODEL READ
        test_object_std = os.path.join(*['objects', 'staticobjects', 'test', 'evil_box1', 'meshes', 'evil_box1.staticmesh'])
        test_object_alt_uvw = os.path.join(*['objects', 'staticobjects', 'test', 'evil_box2', 'meshes', 'evil_box2.staticmesh'])
        test_object_two_lods = os.path.join(*['objects', 'staticobjects', 'test', 'evil_box3', 'meshes', 'evil_box3.staticmesh'])
        test_object_dest = os.path.join(*['objects', 'staticobjects', 'test', 'evil_box4', 'meshes', 'evil_box4.staticmesh'])

        self.path_object_std = os.path.join(bf2.Mod().root, test_object_std)
        self.path_object_alt_uvw = os.path.join(bf2.Mod().root, test_object_alt_uvw)
        self.path_object_two_lods = os.path.join(bf2.Mod().root, test_object_two_lods)
        self.path_object_dest = os.path.join(bf2.Mod().root, test_object_dest)

    def test_can_read_header(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.head.u1 is 0)
        self.assertTrue(vmesh.head.version in [10, 6, 11])
        self.assertTrue(vmesh.head.u3 is 0)
        self.assertTrue(vmesh.head.u4 is 0)
        self.assertTrue(vmesh.head.u5 is 0)
    
    def test_can_read_u1(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.head.u1 is 0)

    def test_can_read_geomnum(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        print(vmesh.geomnum)
        self.assertTrue(vmesh.geomnum is 1)

        vmesh = mesher.LoadBF2Mesh(self.path_object_dest)
        self.assertTrue(vmesh.geomnum is 2)

    def test_can_read_geom_table(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.geom[0].lodnum is 1)

        vmesh = mesher.LoadBF2Mesh(self.path_object_two_lods)
        self.assertTrue(vmesh.geom[0].lodnum is 2)

        vmesh = mesher.LoadBF2Mesh(self.path_object_dest)
        self.assertTrue(len(vmesh.geom) is 2)
        self.assertTrue(vmesh.geom[0].lodnum is 2)
        self.assertTrue(vmesh.geom[1].lodnum is 2)

    def test_can_read_vertattribnum_CUSTOM_PR_DEST(self):
        try:
            test_object_custom = os.path.join(*['objects', 'staticobjects', 'pr', 'destroyable_objects', 'doors', 'wooddoor1m_03', 'meshes', 'wooddoor1m_03.staticmesh'])
            self.path_object_custom = os.path.join(bf2.Mod().root, test_object_custom)
            vmesh = mesher.LoadBF2Mesh(self.path_object_custom)
            self.assertTrue(vmesh.vertattribnum is 10)
        except FileNotFoundError:
            self.skipTest('cannot find PR "wooddoor1m_03" mesh')

    def test_can_read_vertex_attribute_table(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.vertattrib[0] == (0, 0, 2, 0))
        self.assertTrue(vmesh.vertattrib[1] == (0, 12, 2, 3))
        self.assertTrue(vmesh.vertattrib[2] == (0, 24, 4, 2))
        self.assertTrue(vmesh.vertattrib[3] == (0, 28, 1, 5))
        self.assertTrue(vmesh.vertattrib[4] == (0, 36, 1, 261))
        self.assertTrue(vmesh.vertattrib[5] == (0, 44, 1, 517))
        self.assertTrue(vmesh.vertattrib[6] == (0, 52, 1, 773))
        self.assertTrue(vmesh.vertattrib[7] == (0, 60, 2, 6))
        self.assertTrue(vmesh.vertattrib[8] == (255, 0, 17, 0))

    def test_can_read_vertformat(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.vertformat == 4)

    def test_can_read_vertstride(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.vertstride == 72)

    def test_can_read_vertnum(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.vertnum == 25)

    def test_can_read_vertex_block(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(len(vmesh.vertices) == 450)

    def test_can_read_indexnum(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.indexnum is 36)

    def test_can_read_index_block(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(len(vmesh.index) == 36)

    def test_can_read_u2(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.u2 is 8)

    def test_can_read_nodes_bounds(self):
        vmesh = mesher.LoadBF2Mesh(self.path_object_std)
        self.assertTrue(vmesh.geom[0].lod[0].min == (-0.5, 0, -0.5))
        self.assertTrue(vmesh.geom[0].lod[0].max == (0.5, 1.0, 0.5))
        self.assertTrue(vmesh.geom[0].lod[0].pivot == (0.5, 1.0, 0.5))

















