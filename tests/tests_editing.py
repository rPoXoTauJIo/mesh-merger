import unittest
import os
import sys
import copy
import shutil
import math

import modmesh
from modmesh import D3DDECLTYPE
from modmesh import D3DDECLUSAGE

import tests.mock_mesh as mocks

class TestVisMeshBoxEdit(unittest.TestCase):

    def setUp(self):
        self.path_object_std = os.path.join(*['tests', 'samples', 'evil_box', 'meshes', 'evil_box.staticmesh'])

    @classmethod
    def tearDownClass(cls):
        try:
            path_clear = os.path.join(*['tests', 'generated', 'edit'])
            # not cleaning for testing
            #shutil.rmtree(path_clear)
        except FileNotFoundError:
            print('Nothing to clean up')

    def test_can_rename_texture(self):
        vmesh = modmesh.LoadBF2Mesh(self.path_object_std)
        path_object_clone = os.path.join(*['tests', 'generated', 'edit', 'evil_box_rename_texture', 'meshes', 'evil_box_rename_texture.staticmesh'])
        
        geom = 0
        lod = 0
        material = 0
        map = 0

        # ensure we have diffirent texture before test
        self.assertTrue(vmesh.
                        geoms[geom].
                        lods[lod].
                        materials[material].
                        maps[map] == b'objects/staticobjects/test/evil_box/textures/evil_box_c.dds')

        modmesh.VisMeshTransform(vmesh).rename_texture(geom,
                            lod,
                            material,
                            map,
                            'readme/assets/apps/python3/mesher/tests/samples/evil_box/textures/evil_box_c.dds')

        # save results for manual check
        vmesh.save(path_object_clone)
        self.assertTrue(vmesh.
                        geoms[geom].
                        lods[lod].
                        materials[material].
                        maps[map] == b'readme/assets/apps/python3/mesher/tests/samples/evil_box/textures/evil_box_c.dds')
    

    def test_can_get_vertex_data_position(self):
        vmesh = mocks.Box().vmesh
        
        position = vmesh.get_vertex_data(0, 'POSITION')
        self.assertTrue(position == (0.5, 1.0, -0.5))

    def test_can_edit_vertex_data_position(self):
        vmesh = mocks.Box().vmesh
        path_object_clone = os.path.join(*['tests', 'generated', 'edit', 'evil_box_vertex_position', 'meshes', 'evil_box_vertex_position.staticmesh'])
        
        position = (0.5, 2.0, -0.5)
        modmesh.VisMeshTransform(vmesh).edit_vertex(0, 'POSITION', position)
        vmesh.save(path_object_clone)

        self.assertTrue(vmesh.get_vertex_data(0, 'POSITION') == position)

    def test_can_offset_mesh(self):
        vmesh = mocks.Box().vmesh
        vmesh2 = copy.deepcopy(vmesh)
        path_object_clone = os.path.join(*['tests', 'generated', 'edit', 'evil_box_offset_mesh', 'meshes', 'evil_box_offset_mesh.staticmesh'])
        
        offset = (1.0, 0.0, 0.0)
        modmesh.VisMeshTransform(vmesh).offset_mesh_vertices(offset)
        vmesh.save(path_object_clone)
        
        for id_vertex in range(vmesh2.vertnum):
            position_old = vmesh2.get_vertex_data(id_vertex, 'POSITION')
            position_new = vmesh.get_vertex_data(id_vertex, 'POSITION')
            
            self.assertTrue(position_new == sum(i) for i in zip(position_old, offset))

    def test_can_merge_geometry_with_offset(self):
        vmesh = mocks.Box().vmesh
        vmesh_old = copy.deepcopy(vmesh)
        vmesh2 = mocks.Box().vmesh
        offset = (1.0, 0.0, 0.0)
        modmesh.VisMeshTransform(vmesh2).offset_mesh_vertices(offset)
        path_object_clone = os.path.join(*['tests', 'generated', 'edit', 'evil_box_merge_geometry', 'meshes', 'evil_box_merge_geometry.staticmesh'])
        
        modmesh.VisMeshTransform(vmesh).merge_mesh(vmesh2)
        vmesh.save(path_object_clone)
        
        self.assertTrue(vmesh.vertnum == vmesh_old.vertnum + vmesh2.vertnum)
        self.assertTrue(vmesh.indexnum == vmesh_old.indexnum + vmesh2.indexnum)
        self.assertTrue(len(vmesh.index) == len(vmesh_old.index) + len(vmesh2.index))
        self.assertTrue(vmesh.geoms[0].lods[0].materials[0].vnum == vmesh_old.geoms[0].lods[0].materials[0].vnum + vmesh2.geoms[0].lods[0].materials[0].vnum)
        self.assertTrue(vmesh.geoms[0].lods[0].materials[0].inum == vmesh_old.geoms[0].lods[0].materials[0].inum + vmesh2.geoms[0].lods[0].materials[0].inum)
        self.assertTrue(vmesh.geoms[0].lods[0].materials[0].mmin == sum(i) for i in zip(vmesh_old.geoms[0].lods[0].materials[0].mmin, vmesh2.geoms[0].lods[0].materials[0].mmin))
        self.assertTrue(vmesh.geoms[0].lods[0].materials[0].mmax == sum(i) for i in zip(vmesh_old.geoms[0].lods[0].materials[0].mmax, vmesh2.geoms[0].lods[0].materials[0].mmax))
        
        for vertid in range(vmesh.vertnum):
            if vertid < vmesh_old.vertnum:
                #print('vmesh.get_vertex_data({}, "POSITION") = {}'.format(vertid, vmesh.get_vertex_data(vertid, 'POSITION')))
                #print('vmesh_old.get_vertex_data({}, "POSITION") = {}'.format(vertid, vmesh_old.get_vertex_data(vertid, 'POSITION')))
                self.assertTrue(vmesh.get_vertex_data(vertid, 'POSITION') == vmesh_old.get_vertex_data(vertid, 'POSITION'))
            else:
                position_old = vmesh_old.get_vertex_data(vertid - vmesh_old.vertnum, 'POSITION')
                #print('[{}]position_old + offset = {}'.format(vertid, tuple(sum(i) for i in zip(position_old, offset))))
                #print('[{}]vmesh.get_vertex_data({}, "POSITION") = {}'.format(vertid, vertid, vmesh.get_vertex_data(vertid, 'POSITION')))
                self.assertTrue(vmesh.get_vertex_data(vertid, 'POSITION') == sum(i) for i in zip(position_old, offset))
        
        for idxid in range(vmesh.indexnum):
            if idxid < vmesh_old.indexnum:
                self.assertTrue(vmesh.index[idxid] == vmesh_old.index[idxid])
            else:
                print('vmesh.index[0] = {}'.format(vmesh.index[0]))
                print('vmesh.index[{}] = {}'.format(idxid, vmesh.index[idxid]))
                print('vmesh2.index[{}-->{}] = {}'.format(idxid, idxid-vmesh2.indexnum, vmesh2.index[idxid-vmesh2.indexnum]))
                #print('vmesh2.index[{}-{}] + vmesh_old.indexnum({}) = {}'.format(vmesh2.index[idxid-vmesh2.indexnum] + vmesh_old.indexnum))
                self.assertTrue(vmesh.index[idxid] == vmesh2.index[idxid-vmesh2.indexnum] + vmesh_old.vertnum)

    @unittest.skip('not working')
    def test_can_rotate_mesh(self):
        vmesh = mocks.Box().vmesh
        vmesh2 = copy.deepcopy(vmesh)
        path_object_clone = os.path.join(*['tests', 'generated', 'edit', 'evil_box_rotate_mesh', 'meshes', 'evil_box_rotate_mesh.staticmesh'])
        
        rotation = (0.0, 0.0, 0.0)
        modmesh.VisMeshTransform(vmesh).rotate_mesh(rotation)
        vmesh.save(path_object_clone)
        
        id_vertex = 0
        position_old = vmesh2.get_vertex_data(id_vertex, 'POSITION')
        position_new = vmesh.get_vertex_data(id_vertex, 'POSITION')
        
        self.assertTrue(position_old == (0.5, 1.0, -0.5))
        self.assertTrue(position_new == (0.0, 1.0, 0.0))
        

class TestVisMesh_SkinnedMesh(unittest.TestCase):

    def setUp(self):
        self.path_object_skinned = os.path.join(*['tests', 'samples', 'kits', 'mec', 'Meshes', 'mec_kits.skinnedMesh'])

    @unittest.skip('slow, refactor to copy vertex data')
    def test_can_copy_geom(self):
        vmesh = modmesh.LoadBF2Mesh(self.path_object_skinned)
        vmesh_old = copy.deepcopy(vmesh)
        if not vmesh.isSkinnedMesh:
            raise
        path_object_skinned_clone = os.path.join(*['tests', 'generated', 'edit', 'kits', 'mec_geom_copy', 'Meshes', 'mec_kits_geom_copy.skinnedMesh'])

        # example geom
        geomToCopy = 0
        geomCopyTo = 1

        # debugging
        #geom = 0
        #lod = 0
        #mat = 0
        #print('vnum = {}'.format(vmesh.geoms[geom].lods[lod].materials[mat].vnum))
        #print('vstart = {}'.format(vmesh.geoms[geom].lods[lod].materials[mat].vstart))
        #print('inum = {}'.format(vmesh.geoms[geom].lods[lod].materials[mat].inum))
        #print('istart = {}'.format(vmesh.geoms[geom].lods[lod].materials[mat].istart))
        
        modmesh.VisMeshTransform(vmesh).copy_geom_id(geomToCopy, geomCopyTo)
        vmesh.save(path_object_skinned_clone)

        self.assertTrue(vmesh.geomnum == vmesh_old.geomnum + 1)
        self.assertTrue(len(vmesh.geoms) == len(vmesh_old.geoms) + 1)
        self.assertTrue(vmesh.geoms[geomCopyTo].lodnum == vmesh_old.geoms[geomToCopy].lodnum)
        for id_lod, lod in enumerate(vmesh.geoms[geomCopyTo].lods):
            self.assertTrue(lod.rignum == vmesh_old.geoms[geomToCopy].lods[id_lod].rignum)
            for id_rig, rig in enumerate(lod.rigs):
                self.assertTrue(rig.bonenum == vmesh_old.geoms[geomToCopy].lods[id_lod].rigs[id_rig].bonenum)
                for id_bone, bone in enumerate(rig.bones):
                    self.assertTrue(bone.id == vmesh_old.geoms[geomToCopy].lods[id_lod].rigs[id_rig].bones[id_bone].id)
                    self.assertTrue(bone.matrix == vmesh_old.geoms[geomToCopy].lods[id_lod].rigs[id_rig].bones[id_bone].matrix)
            for id_mat, material in enumerate(lod.materials):
                self.assertTrue(material.vnum == vmesh_old.geoms[geomToCopy].lods[id_lod].materials[id_mat].vnum)
                self.assertTrue(material.vstart == vmesh_old.geoms[geomToCopy].lods[id_lod].materials[id_mat].vstart)
                self.assertTrue(material.inum == vmesh_old.geoms[geomToCopy].lods[id_lod].materials[id_mat].inum)
                self.assertTrue(material.istart == vmesh_old.geoms[geomToCopy].lods[id_lod].materials[id_mat].istart)

    def test_can_delete_geom(self):
        vmesh = modmesh.LoadBF2Mesh(self.path_object_skinned)
        if not vmesh.isSkinnedMesh:
            raise
        path_object_skinned_clone = os.path.join(*['tests', 'generated', 'edit', 'kits', 'mec_geom_delete', 'Meshes', 'mec_kits_geom_delete.skinnedMesh'])

        # delete from "middle"
        id_geom_delete = 1
        vstart_at = vmesh.geoms[id_geom_delete].lods[0].materials[0].vstart
        istart_at = vmesh.geoms[id_geom_delete].lods[0].materials[0].istart
        vnum_to_delete = sum([sum([material.vnum for material in lod.materials]) for lod in vmesh.geoms[id_geom_delete].lods])
        inum_to_delete = sum([sum([material.inum for material in lod.materials]) for lod in vmesh.geoms[id_geom_delete].lods])
        geomnum_before = vmesh.geomnum
        geoms_old = copy.deepcopy(vmesh.geoms)
        vertices_old = copy.deepcopy(vmesh.vertices)
        indices_old = copy.deepcopy(vmesh.index)
        vnum_before = vmesh.vertnum
        inum_before = vmesh.indexnum
        
        modmesh.VisMeshTransform(vmesh).delete_geom_id(id_geom_delete)
        vmesh.save(path_object_skinned_clone)

        self.assertTrue(vmesh.geomnum == geomnum_before - 1)
        self.assertTrue(len(vmesh.geoms) == geomnum_before - 1)
        # verify that we cleaned up unnecessary vertex data
        self.assertTrue(vmesh.vertnum == vnum_before - vnum_to_delete)
        self.assertTrue(len(vmesh.vertices) == len(vertices_old) -
            sum([len(D3DDECLTYPE(attrib.vartype)) for attrib in vmesh.vertattrib]) * vnum_to_delete)
        # and corrected vertex indices
        self.assertTrue(vmesh.indexnum == inum_before - inum_to_delete)
        self.assertTrue(len(vmesh.index) == inum_before - inum_to_delete)
        # verify that geoms adjusted vstart and istart offsets properly
        id_geom = id_geom_delete
        while id_geom < vmesh.geomnum:
            id_geom_old = id_geom+1
            for id_lod, lod in enumerate(vmesh.geoms[id_geom].lods):
                rignum_old = geoms_old[id_geom_old].lods[id_lod].rignum
                self.assertTrue(lod.rignum == rignum_old)
                for id_rig, rig in enumerate(lod.rigs):
                    bonenum_old = geoms_old[id_geom_old].lods[id_lod].rigs[id_rig].bonenum
                    self.assertTrue(rig.bonenum == bonenum_old)
                    for id_bone, bone in enumerate(rig.bones):
                        self.assertTrue(bone.id == geoms_old[id_geom_old].lods[id_lod].rigs[id_rig].bones[id_bone].id)
                        self.assertTrue(bone.matrix == geoms_old[id_geom_old].lods[id_lod].rigs[id_rig].bones[id_bone].matrix)
                for id_mat, material in enumerate(lod.materials):
                    self.assertTrue(material.vnum == geoms_old[id_geom_old].lods[id_lod].materials[id_mat].vnum)
                    self.assertTrue(material.vstart == geoms_old[id_geom_old].lods[id_lod].materials[id_mat].vstart - vnum_to_delete)
                    self.assertTrue(material.inum == geoms_old[id_geom_old].lods[id_lod].materials[id_mat].inum)
                    self.assertTrue(material.istart == geoms_old[id_geom_old].lods[id_lod].materials[id_mat].istart - inum_to_delete)
                    # and verify that we deleted vertex and index with correct offset
                    vstart = int(vmesh.vertstride / vmesh.vertformat * material.vstart)
                    vstart_old = int(vmesh.vertstride / vmesh.vertformat * geoms_old[id_geom_old].lods[id_lod].materials[id_mat].vstart)
                    vnum = int(vmesh.vertstride / vmesh.vertformat * material.vnum)
                    for id_data, data in enumerate(vmesh.vertices[vstart:vstart+vnum]):
                        # Apparently pr skinnedmeshes containing nan data in vertices array
                        #  test fails as nan != nan even through rest of data are same
                        if math.isnan(data) and math.isnan(vertices_old[vstart_old+id_data]):
                            continue
                        self.assertAlmostEqual(data, vertices_old[vstart_old+id_data],
                            msg='id {}:{} after {},\nvnum_to_delete = {},\nat geom{} lod{} material{}'.format(vstart+id_data, vstart_old+id_data,
                                id_data,
                                vnum_to_delete,
                                id_geom,
                                id_lod,
                                id_mat)
                                )
                    #'''
                    inum = material.inum
                    istart = material.istart
                    istart_old = geoms_old[id_geom_old].lods[id_lod].materials[id_mat].istart
                    for id_index, index in enumerate(vmesh.index[istart:istart+inum]):
                        self.assertEqual(index, indices_old[istart_old+id_index])
            id_geom += 1
    
    @unittest.skip('TODO: make sure to rebuild vertices and indices')
    def test_can_edit_geoms_order(self):
        vmesh = modmesh.LoadBF2Mesh(self.path_object_skinned)
        vmesh_old = copy.deepcopy(vmesh)
        if not vmesh.isSkinnedMesh:
            raise
        path_object_skinned_clone = os.path.join(*['tests', 'generated', 'edit', 'kits', 'mec_geoms_ordered', 'Meshes', 'mec_kits_geoms_ordered.skinnedMesh'])

        # new geomes
        newGeomsList = tuple([i for i in range(vmesh.geomnum-1, -1, -1)]) # revert geoms order

        modmesh.VisMeshTransform(vmesh).edit_geoms_order(newGeomsList)
        vmesh.save(path_object_skinned_clone)

        self.assertTrue(vmesh.geomnum == vmesh_old.geomnum)
        self.assertTrue(len(vmesh.geoms) == len(vmesh_old.geoms))
        
        for id_geom, geom in enumerate(vmesh.geoms):
            id_geom_old = vmesh_old.geomnum - 1 - id_geom
            self.assertTrue(geom.lodnum == vmesh_old.geoms[id_geom_old].lodnum)
            for id_lod, lod in enumerate(geom.lods):
                self.assertTrue(lod.rignum == vmesh_old.geoms[id_geom_old].lods[id_lod].rignum)
                for id_rig, rig in enumerate(lod.rigs):
                    self.assertTrue(rig.bonenum == vmesh_old.geoms[id_geom_old].lods[id_lod].rigs[id_rig].bonenum)
                    for id_bone, bone in enumerate(rig.bones):
                        self.assertTrue(bone.id == vmesh_old.geoms[id_geom_old].lods[id_lod].rigs[id_rig].bones[id_bone].id)
                        self.assertTrue(bone.matrix == vmesh_old.geoms[id_geom_old].lods[id_lod].rigs[id_rig].bones[id_bone].matrix)
                for id_mat, material in enumerate(lod.materials):
                    self.assertTrue(material.vnum == vmesh_old.geoms[id_geom_old].lods[id_lod].materials[id_mat].vnum)
                    self.assertTrue(material.vstart == vmesh_old.geoms[id_geom_old].lods[id_lod].materials[id_mat].vstart)
                    self.assertTrue(material.inum == vmesh_old.geoms[id_geom_old].lods[id_lod].materials[id_mat].inum)
                    self.assertTrue(material.istart == vmesh_old.geoms[id_geom_old].lods[id_lod].materials[id_mat].istart)




if __name__ == '__main__':
    unittest.main()
        