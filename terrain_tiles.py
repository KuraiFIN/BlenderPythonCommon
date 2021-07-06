import bpy
import bmesh
import random
from mathutils import Vector

def nearest_vert(object, vector):
    vert = object.data.vertices[0]
    thresh = 10000.0
    for vertex in object.data.vertices:
        vl = Vector((vertex.co.x, vertex.co.y, vector.z))
        l = (vl - vector).length_squared
        if l < thresh:
            vert = vertex
            thresh = l
    vert.select = True
    return vert
def nearest_bvert(bm, vector):
    vert = bm.verts[0]
    thresh = 10000.0
    for vertex in bm.verts:
        vl = Vector((vertex.co.x, vertex.co.y, vector.z))
        l = (vl - vector).length_squared
        if l < thresh:
            vert = vertex
            thresh = l
    vert.select = True
    return vert
def nearest_vert_from_objects(objectA, objectB, vertA):
    return nearest_vert(objectB, vertA.co)
def near(number, threshold, error):
    difference = threshold - number
    if difference < 0.0:
        difference *= -1.0
    return difference <= error
def abs(number):
    n = number
    if n < 0.0:
        n *= -1.0
    return n
def lerp(numA, numB, amt):
    diff = (numB - numA) * amt
    return numA + diff
def neighboring_vert_left(object, vertex):
    for edge in object.data.edges:
        if vertex.index not in edge.vertices:
            continue
        other = object.data.vertices[edge.vertices[0]]
        if vertex.index == edge.vertices[0]:
            other = object.data.vertices[edge.vertices[1]]
        if other.co.x + 0.005 < vertex.co.x:
            return other
    return None
def neighboring_vert_right(object, vertex):
    for edge in object.data.edges:
        if vertex.index not in edge.vertices:
            continue
        other = object.data.vertices[edge.vertices[0]]
        if vertex.index == edge.vertices[0]:
            other = object.data.vertices[edge.vertices[1]]
        if other.co.x - 0.005 > vertex.co.x:
            return other
    return None
def neighboring_vert_forward(object, vertex):
    for edge in object.data.edges:
        if vertex.index not in edge.vertices:
            continue
        other = object.data.vertices[edge.vertices[0]]
        if vertex.index == edge.vertices[0]:
            other = object.data.vertices[edge.vertices[1]]
        if other.co.y + 0.005 < vertex.co.y:
            return other
    return None
def neighboring_vert_backward(object, vertex):
    for edge in object.data.edges:
        if vertex.index not in edge.vertices:
            continue
        other = object.data.vertices[edge.vertices[0]]
        if vertex.index == edge.vertices[0]:
            other = object.data.vertices[edge.vertices[1]]
        if other.co.y - 0.005 > vertex.co.y:
            return other
    return None
def get_bounding_box_extremes(object):
    object_matrix = object.matrix_world
    bbox_corners = [object_matrix @ Vector(corner) for corner in object.bound_box]
    left = bbox_corners[0]
    right = left
    upward = left
    downward = left
    forward = left
    backward = left
    for corner in bbox_corners:
        if corner.x < left.x:
            left = corner
        if corner.x > right.x:
            right = corner
        if corner.y < forward.y:
            forward = corner
        if corner.y > backward.y:
            backward = corner
        if corner.z < downward.z:
            downward = corner
        if corner.z > upward.z:
            upward = corner
    list = [left, right, upward, downward, forward, backward]
    return list
def get_bounding_box_dimensions(object):
    list = get_bounding_box_extremes(object)
    vec = Vector(((list[1].x - list[0].x)/1, (list[5].y - list[4].y)/1, (list[2].z - list[3].z)/1))
    return vec
def get_bounding_box_center(object):
    extremes = get_bounding_box_extremes(object)
    locx = (extremes[1].x + extremes[0].x) * 0.5
    locy = (extremes[5].y + extremes[4].y) * 0.5
    locz = (extremes[3].z + extremes[2].z) * 0.5
    vec = Vector((locx, locy, locz))
    return vec
def get_object_relations(objects, object):
    if len(objects) < 2:
        rels = [None, None, None, None]
        return rels
    default_obj = objects[0]
    if object == objects[0]:
        default_obj = objects[1]
    main_loc = get_bounding_box_center(object)
    def_loc = get_bounding_box_center(default_obj)
    left = default_obj
    left_loc = def_loc
    right = default_obj
    right_loc = def_loc
    forward = default_obj
    forward_loc = def_loc
    backward = default_obj
    backward_loc = def_loc
    for obj in objects:
        if obj == object:
            continue
        loc = get_bounding_box_center(obj)
        isleft = loc.x + 0.005 < main_loc.x
        isright = loc.x - 0.005 > main_loc.x
        isforward = loc.y + 0.005 < main_loc.y
        isbackward = loc.y - 0.005 > main_loc.y
        if isleft or isright:
            if not near(loc.y, main_loc.y, 0.01):
                continue
        if isforward or isbackward:
            if not near(loc.x, main_loc.x, 0.01):
                continue
        if (left == default_obj or loc.x > left_loc.x) and isleft:
            left = obj
            left_loc = loc
        elif (right == default_obj or loc.x < right_loc.x) and isright:
            right = obj
            right_loc = loc
        if (forward == default_obj or loc.y > forward_loc.y) and isforward:
            forward = obj
            forward_loc = loc
        elif (backward == default_obj or loc.y < backward_loc.y) and isbackward:
            backward = obj
            backward_loc = loc
    if left_loc.x - 0.005 > main_loc.x:
        left = None
    if right_loc.x + 0.005 < main_loc.x:
        right = None
    if forward_loc.y - 0.005 > main_loc.y:
        forward = None
    if backward_loc.y + 0.005 < main_loc.y:
        backward = None
    relations = [left, right, forward, backward]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in relations:
        if obj is not None:
            obj.select_set(True)
    return relations
        
        
def make_circles_in_bounds(object, number):
    circles = []
    offset = object.matrix_world @ object.location
    bbox = get_bounding_box_extremes(object)
    left = bbox[0] - offset
    right = bbox[1] - offset
    forward = bbox[4] - offset
    backward = bbox[5] - offset
    co = Vector((left.x, forward.y, 0))
    ax = Vector((right.x - left.x, 0, 0))
    ay = Vector((0, backward.y - forward.y, 0))
    #bm = bmesh.new()
    #bm.from_mesh(object.data)
    #bm.verts.ensure_lookup_table()
    for n in range(0, number):
        v = co + (ax * random.random()) + (ay * random.random())
        v.z = random.random() * 25.0
        nearest = nearest_vert(object, v).index#nearest_bvert(bm, v).index
        circle = (nearest, v)
        circles.append(circle)
    #bm.to_mesh(object.data)
    object.data.update()
    #bm.free()
    return circles
#def select_vertices_by_indices(object, vertices)
def get_border_verts_separate(object):
    offset = object.matrix_world @ object.location
    bbox = get_bounding_box_extremes(object)
    left = bbox[0] - offset
    right = bbox[1] - offset
    forward = bbox[4] - offset
    backward = bbox[5] - offset
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.verts.ensure_lookup_table()
    all_left = []
    all_right = []
    all_forward = []
    all_backward = []
    for i, vertex in enumerate(bm.verts):
        if near(vertex.co.x, left.x, 0.01):
            all_left.append(vertex.index)
        elif near(vertex.co.x, right.x, 0.01):
            all_right.append(vertex.index)
        elif near(vertex.co.y, forward.y, 0.01):
            all_forward.append(vertex.index)
        elif near(vertex.co.y, backward.y, 0.01):
            all_backward.append(vertex.index)
        else:
            vertex.select = False
            continue
        vertex.select = True
    bm.to_mesh(object.data)
    object.data.update()
    bm.free()
    lists = [all_left, all_right, all_forward, all_backward]
    return lists
def get_border_verts_all(object):
    #alternative approach: verts having only one face are boundary verts
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    #bpy.ops.object.mode_set(mode='EDIT')
    offset = object.matrix_world @ object.location
    bbox = get_bounding_box_extremes(object)
    left = bbox[0] - offset
    right = bbox[1] - offset
    forward = bbox[4] - offset
    backward = bbox[5] - offset
    #bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.verts.ensure_lookup_table()
    #bm.verts[0].select = True
    for i, vertex in enumerate(bm.verts):
        border = False
        if near(vertex.co.x, left.x, 0.01):
            border = True
        elif near(vertex.co.x, right.x, 0.01):
            border = True
        elif near(vertex.co.y, forward.y, 0.01):
            border = True
        elif near(vertex.co.y, backward.y, 0.01):
            border = True
        vertex.select = border
    bm.to_mesh(object.data)
    object.data.update()
    bm.free()
    verts = [vert for vert in object.data.vertices if vert.select]
    #print(len(verts))
    #bpy.ops.object.mode_set(mode='OBJECT')
    return verts
def get_left_verts(object):
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    bbox = get_bounding_box_extremes(object)
    left = bbox[0] - (object.matrix_world @ object.location)
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.verts.ensure_lookup_table()
    for i, vertex in enumerate(bm.verts):
        border = False
        if near(vertex.co.x, left.x, 0.01):
            border = True
        vertex.select = border
    bm.to_mesh(object.data)
    object.data.update()
    bm.free()
    verts = [vert for vert in object.data.vertices if vert.select]
    return verts
def get_left_edgeloops(object):
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    bbox = get_bounding_box_extremes(object)
    left = bbox[0] - (object.matrix_world @ object.location)
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.verts.ensure_lookup_table()
    bverts = []
    for i, vertex in enumerate(bm.verts):
        border = False
        if near(vertex.co.x, left.x, 0.01):
            border = True
        vertex.select = border
        if border:
            bverts.append(vertex)
    bm.select_mode = {'EDGE'}
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    bloops = []#edges
    loops = []#lists
    for edge in bm.edges:
        edge.select = False
    #assumed to be ordered
    for i, edge in enumerate(bm.edges):
        #TODO: selects all edge loops BUT ONE(at end)
        both = edge.verts[0] in bverts and edge.verts[1] in bverts
        if both:
            continue
        connected = edge.verts[0] in bverts or edge.verts[1] in bverts
        if not connected:
            continue
        #edge.verts[0].select = True
        #edge.verts[1].select = True
        eloops = []
        if edge not in eloops:
            eloops.append(edge)
        loop = edge.link_loops[0]
        count = 0
        while count < 100:
            if loop.edge not in eloops:
                bloops.append(loop.edge)
                eloops.append(loop.edge)
            loop = loop.link_loop_prev.link_loop_radial_prev.link_loop_prev
            loop.edge.select = True
            count += 1
        loops.append(eloops)
    vg = object.vertex_groups.active
    deform = bm.verts.layers.deform.active
    vgi = object.vertex_groups.active_index
    #group = object.vertex_groups.new(name=str(x)+'_'+str(y))
    for loop in loops:
        first = loop[0].verts[0] in loop[1].verts
        vert = loop[0].verts[0]
        if first:
            vert = loop[0].verts[1]
        w = 1.0
        for edge in loop:
            if vert is None:
                continue
            w -= 0.009
            #v = []
            #v.append(vert.index)
            #vg.add(v, 0.6, 'ADD')
            g = vert[deform]
            g[vgi] = w#0.73
            #vert = edge.other_vert(vert)
            sfirst = vert == edge.verts[0]
            vert = edge.verts[0]
            if sfirst:
                vert = edge.verts[1]
    bm.to_mesh(object.data)
    object.data.update()
    bm.free()
    verts = [vert for vert in object.data.vertices if vert.select]
    return verts

def vertex_group_border_remove(object):
    verts = get_border_verts_all(object)
    indices = [v.index for v in verts]
    avg = object.vertex_groups.active
    for vg in object.vertex_groups:
        if vg.name != 'center':
            continue
        object.vertex_groups.active = vg
        #bpy.ops.object.vertex_group_remove_from()
        vg.remove(indices)
    object.vertex_groups.active = avg
def name_numbers_to_chess(object):
    real_name = object.name[0:].replace('.001', 'A1')
    real_name = real_name.replace('.002', 'B1')
    real_name = real_name.replace('.003', 'A2')
    real_name = real_name.replace('.004', 'B2')
    object.name = real_name
def name_mesh_copy(object):
    object.data.name = object.name[0:]
    return object.data.name
def name_mesh_copy_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        name_mesh_copy(object)
        #bpy.ops.object.select_all(action='DESELECT')
        #object.select_set(True)
        #bpy.context.view_layer.objects.active = object
        #bpy.ops.object.mode_set(mode='OBJECT')
    return objects

def all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        vertex_group_border_remove(object)
        name_numbers_to_chess(object)
        name_mesh_copy(object)
def project_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.mode_set(mode='EDIT')
        for oWindow in bpy.context.window_manager.windows:
            oScreen = oWindow.screen
            for oArea in oScreen.areas:
                if oArea.type == 'VIEW_3D':  
                    for oRegion in oArea.regions:
                        if oRegion.type == 'WINDOW':
                            override = {'window': oWindow, 'screen': oScreen, 'area': oArea, 'region': oRegion, 'scene': bpy.context.scene, 'edit_object': bpy.context.edit_object, 'active_object': bpy.context.active_object, 'selected_objects': bpy.context.selected_objects}
                            bpy.ops.uv.project_from_view(override, correct_aspect=True, scale_to_bounds=True)
                            bpy.ops.object.mode_set(mode='OBJECT')
def calc_slope_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        vg = object.vertex_groups.get('slope')
        if vg is not None:
            object.vertex_groups.remove(vg)
        bpy.ops.mesh.ant_slope_map(group_name="slope")
        bpy.ops.object.mode_set(mode='OBJECT')
erosion_layers = ['rainmap', 'scree', 'avalanced', 'water', 'scour', 'deposit', 'flowrate', 'sediment', 'sedimentpct', 'capacity']
def delete_vertex_group(object, group_name):
    vg = object.vertex_groups.get(group_name)
    if vg is not None:
        object.vertex_groups.remove(vg)
    return None
def calc_erosion_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bm = bmesh.new()
        bm.from_mesh(object.data)
        bm.verts.ensure_lookup_table()
        for vg in erosion_layers:
            delete_vertex_group(object, vg)
        bpy.ops.mesh.eroder(Iterations=1, IterRiver=30, IterAva=5, IterDiffuse=5, Ef=0, Kd=0.1, Kt=1.0472, Kr=0.01, Kv=0, userainmap=True, Ks=0.5, Kdep=0.1, Kz=0.3, Kc=0.9, Ka=1, Kev=0.5, numexpr=True, Pd=0.2, Pa=0.5, Pw=1, smooth=True, showiterstats=False, showmeshstats=False)
        for i, v in enumerate(object.data.vertices):
            object.data.vertices[i].co = bm.verts[i].co + Vector((0,0,0))
        bm.free()
        bpy.ops.object.mode_set(mode='OBJECT')

def random_vertex_group_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        vg = object.vertex_groups.active
        #left_verts = get_left_edgeloops(object)
        circles = make_circles_in_bounds(object, 100)#TODO: set radius multiplier param
        bm = bmesh.new()
        bm.from_mesh(object.data)
        bm.verts.ensure_lookup_table()
        vg = object.vertex_groups.active
        deform = bm.verts.layers.deform.active
        vgi = object.vertex_groups.active_index
        for circle in circles:
            ci = circle[0]
            cv = circle[1]
            #print('vert at index ' + str(ci) + ' at ' + str(cv))
            for vert in bm.verts:
                g = vert[deform]
                diff = (cv - Vector((vert.co.x, vert.co.y, cv.z))).length#_squared
                sqr25 = 25.0# * 25.0
                if diff > sqr25:
                    diff = sqr25
                diff = (sqr25 - diff) / (sqr25 * 10.0)
                if vgi not in g:
                    g[vgi] = 0.0
                g[vgi] += diff
            
        bm.to_mesh(object.data)
        object.data.update()
        bm.free()
def bleed_vertex_group_all_objects():
    objects = [obj for obj in bpy.context.selected_objects]
    for object in objects:
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        relations = get_object_relations(objects, object)
        obj_right = relations[1]
        #obj_back = relations[2]
        border_main = get_border_verts_separate(object)
        border_right = None
        if obj_right is not None:
            border_right = get_border_verts_separate(obj_right)
        else:
            continue
        #border_back = None
        #if obj_back is not None:
        #    border_back = get_border_verts_separate(obj_back)
        #TODO: check NoneType
        vMainRight = border_main[1]
        #vMainBack = border_main[3]
        vRight = border_right[0]
        #vBack = border_back[2]
        bm = bmesh.new()
        bm.from_mesh(object.data)
        bm.verts.ensure_lookup_table()
        bmr = bmesh.new()
        bmr.from_mesh(obj_right.data)
        bmr.verts.ensure_lookup_table()
        vg = object.vertex_groups.active
        deform = bm.verts.layers.deform.active
        vgi = object.vertex_groups.active_index
        vgr = obj_right.vertex_groups.active
        deformr = bmr.verts.layers.deform.active
        vgir = obj_right.vertex_groups.active_index
        for vindex in vMainRight:
            vertex = object.data.vertices[vindex]
            vert = nearest_vert_from_objects(object, obj_right, vertex)
            bv = bm.verts[vindex]
            g = bv[deform]
            bvr = bmr.verts[vert.index]
            gr = bvr[deformr]
            if vgi not in g:
                g[vgi] = 0.0
            if vgir not in gr:
                gr[vgir] = 0.0
            diff = 1.0 - abs(gr[vgir] - g[vgi])
            w = gr[vgir]
            g[vgi] = w
            trail_length = lerp(random.random(), 0.5, 0.8)#implied 0-10
            trail_inv = 1.0 / trail_length
            trail = 1.0
            v = vertex
            while trail > 0.0:
                trail -= trail_inv * 0.015 * diff
                v = neighboring_vert_left(object, v)
                if v is None:
                    break
                bv = bm.verts[v.index]
                g = bv[deform]
                if vgi not in g:
                    g[vgi] = 0.0
                w2 = lerp(g[vgi], w, trail)
                g[vgi] = w2
            #sampled right obj onto main(left)
            #now bleed outwards leftwards
        bm.to_mesh(object.data)
        object.data.update()
        bm.free()
        bmr.free()
            

active = bpy.context.view_layer.objects.active

#project_all_objects()
#calc_erosion_all_objects()
#random_vertex_group_all_objects()
#get_object_relations(bpy.context.selected_objects, bpy.context.view_layer.objects.active)
#print(neighboring_vert_forward(active, active.data.vertices[250]))
bleed_vertex_group_all_objects()

#string = 'some string or something right here'
#string = string.replace('in', 'at')
#print(string)
