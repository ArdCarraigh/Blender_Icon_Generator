# -*- coding: utf-8 -*-
# render_tools.py

import bpy
import os
from glob import glob
import numpy as np
from math import atan, sqrt, tan
        
def render_icon(context, object, rotation = (0,0,0), scale = (1,1,1), offset = (0,0,0), 
                resolution = (64,64), type = 'ORTHO', fov = 0, 
                side = 'RIGHT', key_power = 10, fill_power = 5, back_power = 5, 
                shadow_catch = False, depth = 0,
                output = "/tmp/tmp.png", format = 'PNG', dxgi = None):
    
    wm = context.window_manager.icon_generator 
    prev_mode = wm.PreviewBool
    if prev_mode: 
        wm.PreviewBool = False
    
    # Set Scene                
    temp_scene = bpy.context.scene.copy()
    bpy.context.window.scene = temp_scene
    view_layer = bpy.context.view_layer
    temp_scene.render.film_transparent = True
    temp_scene.use_nodes = True
    ntree = temp_scene.node_tree
    nodes = ntree.nodes
    links = ntree.links
    temp_scene.render.resolution_x = resolution[0]
    temp_scene.render.resolution_y = resolution[1]
    
    # Get Bounding Box and Set Transforms
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(state=True)
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    object = bpy.context.active_object
    object.hide_render= False
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    object.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    bound_min = np.array(object.bound_box[0])
    bound_max = np.array(object.bound_box[6])
    loc_z = (bound_min[2] + bound_max[2]) / 2
    loc_x = (bound_min[0] + bound_max[0]) / 2
    center_y = (bound_min[1] + bound_max[1]) / 2
    dim_z = abs(bound_max[2] - bound_min[2])
    dim_x = abs(bound_max[0] - bound_min[0])
    dim_max = max(dim_z, dim_x)
    loc_plus_y = bound_min[1] - dim_max
    object.scale[0] = scale[0]
    object.scale[2] = scale[1]
    object.location[0] = offset[0]
    object.location[2] = offset[1]
    
    for obj in bpy.data.objects:
        if obj != object:
            obj.hide_render = True
                  
    # Get File Format
    is_dds = False
    if format == 'DDS':
        from blender_dds_addon.directx.texconv import Texconv
        is_dds = True
        format = 'TARGA'
        output = output[:-3] + "tga"
    
    dir_name = os.path.dirname(output)
    file_name = os.path.basename(output)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
                     
    # Compositing
    for nod in nodes:
        nodes.remove(nod)
    render_node = nodes.new('CompositorNodeRLayers')
    render_node.scene = temp_scene
    render_node.layer = view_layer.name
    file_output = nodes.new('CompositorNodeOutputFile')
    file_output.base_path = dir_name
    file_output.file_slots[0].path = file_name
    file_output.format.file_format = format
    links.new(render_node.outputs['Image'], file_output.inputs[0])
              
    # Set Camera
    if type == 'ORTHO':
        bpy.ops.object.camera_add(location = (loc_x,min(bound_min[1] - 0.5, loc_plus_y),loc_z), rotation = (np.pi*0.5, 0, 0))
        cam = bpy.context.active_object
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = dim_max * (max(resolution) / min(resolution)) * 1.1
    
    elif type == 'PERSP':
        loc_y = center_y - ((dim_max * 1.1) / 2) / tan(fov/ (max(resolution) / min(resolution)) / 2)
        bpy.ops.object.camera_add(location = (loc_x,loc_y,loc_z), rotation = (np.pi*0.5, 0, 0))
        cam = bpy.context.active_object
        cam.data.type = 'PERSP'
        cam.data.lens_unit = 'FOV'
        cam.data.angle = fov
        
    temp_scene.camera = cam  
    
    # Add Lighting
    dist_plus_y = abs(center_y - loc_plus_y)
    deg_90 = np.pi*0.5
    deg_45 = np.pi*0.25
    loc_minus_y = bound_max[1] + dim_max
    dist_minus_y = abs(center_y - loc_minus_y)
    
    if side == 'RIGHT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x + dist_plus_y, loc_plus_y, bound_max[2]),
                                rotation=(atan(sqrt(2 * dist_plus_y ** 2) / (bound_max[2] - loc_z)), 0, deg_45))
    elif side == 'LEFT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x - dist_plus_y, loc_plus_y, bound_max[2]),
                                rotation=(atan(sqrt(2 * dist_plus_y ** 2) / (bound_max[2] - loc_z)), 0, -deg_45))
    key_light = bpy.context.active_object
    key_light.scale = (dim_x*1.5, dim_z*1.5, 1)
    key_light.data.normalize = False
    key_light.data.energy = key_power
    key_light.scale[0] *= scale[0]
    key_light.scale[1] *= scale[1]
    key_light.location[0] += offset[0]
    key_light.location[2] += offset[1]
    
    if side == 'RIGHT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x - dist_plus_y, loc_plus_y, loc_z),
                                rotation=(deg_90, 0, -deg_45))
    elif side == 'LEFT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x + dist_plus_y, loc_plus_y, loc_z),
                                rotation=(deg_90, 0, deg_45))
    fill_light = bpy.context.active_object
    fill_light.scale = (dim_x*1.5, dim_z*1.5, 1)
    fill_light.data.normalize = False
    fill_light.data.energy = fill_power
    fill_light.scale[0] *= scale[0]
    fill_light.scale[1] *= scale[1]
    fill_light.location[0] += offset[0]
    fill_light.location[2] += offset[1]
    
    if side == 'RIGHT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x - dist_minus_y, loc_minus_y, loc_z),
                                rotation=(deg_90, 0, -deg_45*3))
    elif side == 'LEFT':
        bpy.ops.object.light_add(type='AREA', location=(loc_x + dist_minus_y, loc_minus_y, loc_z),
                                rotation=(deg_90, 0, deg_45*3))
    back_light = bpy.context.active_object
    back_light.scale = (dim_x*1.5, dim_z*1.5, 1)
    back_light.data.normalize = False
    back_light.data.energy = back_power
    back_light.scale[0] *= scale[0]
    back_light.scale[1] *= scale[1]
    back_light.location[0] += offset[0]
    back_light.location[2] += offset[1]
    
    # Shadow Catcher
    if shadow_catch:
        loc_y_shadow_catcher = bound_max[1]
        bpy.ops.mesh.primitive_plane_add(size=dim_max*4, enter_editmode=False, align='WORLD', 
                                        location=(loc_x + offset[0], loc_y_shadow_catcher + depth, loc_z + offset[1]), 
                                        rotation=(np.pi*0.5, 0, 0))
        shadow_catcher = bpy.context.active_object
        shadow_catcher.scale[0] = scale[0]
        shadow_catcher.scale[1] = scale[1]
        shadow_catcher.name = "ShadowCatcherTemp_Icon"
        with bpy.data.libraries.load(os.path.dirname(__file__) + "/shadow_catcher_material.blend", link = False) as (data_from, data_to):
            data_to.materials = data_from.materials
        shadow_catcher.data.materials.append(bpy.data.materials["ShadowCatcherMaterial"]) 
                        
    # Render
    bpy.ops.render.render(scene = temp_scene.name)
    
    # Rename File
    match format:
        case 'PNG':
             old_path = glob(output+"[0-9]*.png")[0]
        case 'TARGA':
             old_path = glob(output+"[0-9]*.tga")[0]
    try:
        os.rename(old_path, output)
    except FileExistsError:
        os.remove(output)
        os.rename(old_path, output)
                                 
    # Convert to DDS if requested
    if is_dds:
        texconv = Texconv()
        texconv.convert_to_dds(file = output, dds_fmt = dxgi, out = dir_name)
        texconv.unload_dll()
        os.remove(output)
        output = output[:-3]
        file_name = file_name[:-3]
    
    # Clean up
    bpy.data.objects.remove(object)
    bpy.data.objects.remove(key_light)
    bpy.data.objects.remove(fill_light)
    bpy.data.objects.remove(back_light)
    bpy.data.objects.remove(cam)
    if shadow_catch:
            bpy.data.objects.remove(shadow_catcher)  
    bpy.data.scenes.remove(temp_scene)
  
    # Purge orphan data left unused
    override = context.copy()
    override["area.type"] = ['OUTLINER']
    override["display_mode"] = ['ORPHAN_DATA']
    with context.temp_override(**override):
        bpy.ops.outliner.orphans_purge()
        
    for obj in bpy.data.objects:
        obj.hide_render = False
    
    if prev_mode:    
        wm.PreviewBool = prev_mode
                                  
    return   