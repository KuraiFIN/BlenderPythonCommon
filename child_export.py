# This file has misc functions to visualize armatures via empties with accessible bone matrices,
# convert particle systems into transform hierarchies and merge them or export them as file, etc

import bpy
import bmesh
from mathutils import Vector
from mathutils import Matrix
import os

outpath = 'C:\\Users\\Kurai\\source\\repos\\KuraiEngine\\KuraiEngine\\resource\\'
parent = bpy.context.object
parentHome = parent.location[0:]
parentRot = parent.rotation_euler[0:]
origin = (0.0, 0.0, 0.0)


def add_empties():
    armature = bpy.context.object
    if armature.type != 'ARMATURE':
        return
    empty_parent = bpy.data.objects.new('skeleton.objs',None)
    empty_parent.empty_display_size = 4
    bpy.context.scene.collection.objects.link(empty_parent)
    empty_parent.name = 'skeleton.objs'
    empty_parent.matrix_world = armature.matrix_world.copy()
    dict = {}
    for bone in skeleton.pose.bones:
        empty = bpy.data.objects.new(bone.name, None)
        empty.empty_display_size = 0.25
        empty.parent = empty_parent
        empty.matrix_world = armature.matrix_world @ bone.matrix
        bpy.context.scene.collection.objects.link(empty)
        dict[bone.name] = empty
    for bone in skeleton.pose.bones:
        parent = bone.parent
        if parent is None:
            continue
        empty = dict.get(bone.name, None)
        empty_parent = dict.get(parent.name, None)
        if empty is None or empty_parent is None:
            continue
        m = empty.matrix_world.copy()
        empty.parent = empty_parent
        empty.matrix_world = m



def ExportChildren():
    parent.location = origin
    for child in parent.children:
        childHome = child.location
        child.location = origin
        bpy.ops.object.select_all(action='DESELECT')
        child.select_set(state=True)
        parent.select_set(state=True)
        exportName = outpath + child.name + '.fbx'
        #bpy.ops.export_scene.fbx(filepath=exportName, use_selection=True, use_armature_deform_only=True, bake_anim=False)
        bpy.ops.export_scene.obj(filepath=exportName, use_selection=True)
        child.location = childHome
    parent.location = parentHome
        
#ExportChildren()
 
def ExportObj(object, filedir):
    #.obm equivalent
    parent = object.parent
    object.parent = None
    object_loc = object.location[0:]
    object_rot = object.rotation_euler[0:]
    object.location = origin
    object.rotation_euler = origin
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(state=True)
    object_name = object.name
    if object.type == 'MESH':
        object_name = object.data.name
    export_name = os.path.join(filedir, object_name + '.obj')#outpath + object_name + '.obj'
    bpy.ops.export_scene.obj(filepath=export_name, use_selection=True)
    #bpy.ops.export_scene.obj(filepath=export_name, use_selection=True, use_triangles=True, use_materials=False)
    print('exported ' + object_name + '.obj at location ' + str(object.location.x) + ', ' + str(object.location.y) + ', ' + str(object.location.z))
    object.location = object_loc[0:]
    object.rotation_euler = object_rot[0:]
    object.parent = parent
    #bpy.context.scene.update()#might have to call
     
#ExportObj(parent)


def get_obj_lines(object, spacing, do_export, export_obj_filepath):
    lines = []
    if object.parent: #is not None:
        old_mat = object.matrix_world.copy()
        object.matrix_parent_inverse.identity()
        object.matrix_basis = object.parent.matrix_world.inverted() @ old_mat
        loc = str(object.location.x) + ' ' + str(object.location.z) + ' ' + str(-object.location.y)
        object_rotation = object.rotation_euler.to_quaternion()
        rot = str(object_rotation.x) + ' ' + str(object_rotation.y) + ' ' + str(object_rotation.z) + ' ' + str(object_rotation.w)
        object_name = object.name
        if object.type == 'MESH':
            object_name += ' ' + object.data.name
        lines.append(spacing + '  o ' + object_name)
        lines.append(spacing + '  l local ' + loc)
        lines.append(spacing + '  r local ' + rot)
        if do_export:
            ExportObj(object, export_obj_filepath)
    else:
        print('object has no parent!')
        loc = str(object.location.x) + ' ' + str(object.location.z) + ' ' + str(-object.location.y)
        object_rotation = object.rotation_euler.to_quaternion()
        rot = str(object_rotation.x) + ' ' + str(object_rotation.y) + ' ' + str(object_rotation.z) + ' ' + str(object_rotation.w)
        object_name = object.name
        if object.type == 'MESH':
            object_name += ' ' + object.data.name
        lines.append(spacing + '  o ' + object_name)
        lines.append(spacing + '  l local ' + loc)
        lines.append(spacing + '  r local ' + rot)
        if do_export:
            ExportObj(object, export_obj_filepath)
        
    if len(object.children) != 0:
        child_names = []
        for child in object.children:
            child_name = child.name
            if child.type == 'MESH':
                child_name = child.data.name
            export_obj = False
            if child_name not in child_names:
                child_names.append(child_name)
                export_obj = True
            new_lines = get_obj_lines(child, spacing + '  ', export_obj, export_obj_filepath)
            for line in new_lines:
                lines.append(line)
    return lines
def get_root_obj_lines(export_obj_filepath):
    #Automatically assumes root is empty!!!
    lines = []
    object = bpy.context.active_object
    object_name = object.name
    if object.type == 'MESH':
        object_name += ' ' + object.data.name
    lines.append('o ' + object_name)
    child_names = []
    for child in object.children:
        child_name = child.name
        if child.type == 'MESH':
            child_name = child.data.name
        export_obj = False
        if child_name not in child_names:
            child_names.append(child_name)
            export_obj = True
            #TODO: export_obj param
        new_lines = get_obj_lines(child, '', export_obj, export_obj_filepath)
        for line in new_lines:
            lines.append(line)
    file = open(os.path.join(export_obj_filepath, object.name + '.obt'), 'w')
    for line in lines:
        file.write(line)
        file.write('\n')
    file.close()
        

def ExportObjsAndFiles(object, filepath):
    lines = []
    object_loc = object.location[0:]
    object_rot = object.rotation_euler[0:]
    object.location = origin[0:]
    object.rotation_euler = origin[0:]
    bpy.ops.object.select_all(action='DESELECT')
    object_str = 'o ' + object.name
    lines.append(object_str)
    for child in object.children:
        old_mat = child.matrix_world.copy()
        child.matrix_parent_inverse.identity()
        child.matrix_basis = object.matrix_world.inverted() @ old_mat
        loc = str(child.location.x) + ' ' + str(child.location.y) + ' ' + str(child.location.z)
        child_rotation = child.rotation_euler.to_quaternion()
        rot = str(child_rotation.x) + ' ' + str(child_rotation.y) + ' ' + str(child_rotation.z) + ' ' + str(child_rotation.w)
        child_name = child.name
        if child.type == 'MESH':
            child_name += ' ' + child.data.name
        lines.append('  o ' + child_name)
        lines.append('  l local ' + loc)
        lines.append('  r local ' + rot)
    #filepath = outpath + 'export.obt'
    file = open(filepath, "w")
    for line in lines:
        file.write(line)
        file.write("\n")
    file.close()
    object.location = object_loc[0:]
    object.rotation_euler = object_rot[0:]

def get_children_recursive(object):
    objects = []
    for child in object.children:
        if child.type == 'MESH':
            objects.append(child)
        grandchildren = get_children_recursive(child)
        for grandchild in grandchildren:
            if grandchild.type == 'MESH':
                objects.append(grandchild)
    return objects
def get_collection(object):
    if len(object.users_collection) > 0:
        return object.users_collection[0]
    return bpy.context.scene.collection
def copy(new_name, object, collection):
    new_object = None
    if object.type == 'MESH':
        new_object = object.copy()
        new_object.data = object.data.copy()
        new_object.name = new_name
        new_object.data.name = new_name
    else:
        new_mesh = bpy.data.meshes.new(new_name)
        new_object = bpy.data.objects.new(new_name, new_mesh)
    collection.objects.link(new_object)
    return new_object

def convert_particle_system():
    objects = []
    object = bpy.context.active_object
    if 'ParticleSettings' not in object.modifiers:
        return None
    particle_modifier = object.modifiers['ParticleSettings']
    for modifier in object.modifiers:
        upper = modifier.type.upper()
        if upper == 'PARTICLE_SYSTEM':
            particle_modifier = modifier
    if particle_modifier is None:
        return None
    particle_system = particle_modifier.particle_system.settings
    particle_type = particle_system.type
    particle_collection = particle_system.instance_collection
    #particle_system.render_type == 'COLLECTION'
    if particle_type != 'HAIR' or particle_collection is None:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    dg = bpy.context.evaluated_depsgraph_get()
    objects = []
    for instance in dg.object_instances:
        if not instance.is_instance:
            continue
        is_particle = instance.object.name in particle_collection.objects
        if not is_particle:
            continue
        particle_attached = instance.particle_system.name == particle_modifier.particle_system.name
        if not particle_attached:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = instance.object.original
        dg2 = bpy.context.evaluated_depsgraph_get()
        ob = instance.object.original.evaluated_get(dg)
        dupli = instance.object.original.copy()
        dupli.data = bpy.data.meshes.new_from_object(ob)#instance.object.original.data.copy()
        dupli.location = Vector((0,0,0))
        dupli.data.transform(instance.matrix_world)
        bpy.context.scene.collection.objects.link(dupli)
        objects.append(dupli)
        dupli.select_set(True)
        bpy.context.view_layer.objects.active = dupli
        dupli.select_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
        obj.modifiers.clear()
    bpy.context.view_layer.objects.active = objects[0]
    new_object = objects[0]
    bpy.ops.object.join()
    bpy.context.active_object.scale = Vector((1,1,1))
    new_origin = object.location
    new_object.data.transform(Matrix.Translation(-new_origin))
    new_object.location += new_origin
    return new_object

def merge_meshes_new():
    object = bpy.context.active_object
    objects = get_children_recursive(object)
    collection = get_collection(object)
    new_object = copy(object.name + '.objs', object, collection)
    new_objects = []
    for obj in objects:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        dg = bpy.context.evaluated_depsgraph_get()
        ob = obj.evaluated_get(dg)
        #n_obj = bpy.data.objects.new(obj.name + '_copy', ob.data)
        n_obj = obj.copy()
        n_obj.data = bpy.data.meshes.new_from_object(ob)
        collection.objects.link(n_obj)
        new_objects.append(n_obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in new_objects:
        obj.select_set(True)
    new_object.select_set(True)
    bpy.context.view_layer.objects.active = new_object
    bpy.ops.object.join()
    new_origin = object.location - new_object.location
    new_object.data.transform(Matrix.Translation(-new_origin))
    new_object.location += new_origin
    return new_object

    
            
#get_root_obj_lines(outpath)
merge_meshes_new()
#convert_particle_system()
