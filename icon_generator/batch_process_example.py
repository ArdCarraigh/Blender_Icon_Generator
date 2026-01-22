# -*- coding: utf-8 -*-
# batch_process_example.py

# Preferably execute in an empty scene

import bpy
import os
from math import radians
from icon_generator.render_tools import render_icon

# The path to your model directory
rootdir = "C:/The/Path/To/Your/Models"

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        filepath = os.path.join(subdir, file)
        
        if file.endswith(".fbx"):   # Used here to check that it is a 3D model file. 
                                    # Could add a OR with other file extensions typical of 3D models
                                    
            # Make sure that the mode and cursor location are set to default
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
            bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        
            # Open a FBX
            if file.endswith(".fbx"):
                bpy.ops.import_scene.fbx('EXEC_DEFAULT', filepath = filepath)
                
            # Could support other file formats here
            
            # Could do something to:
            # - the materials, 
            # - the normals, 
            # - the bone pose,
            # - the animations,
            # - or whatever else...
                
            # Presets can be defined based on a pattern in the file name, the bounding box of the model or whatever else
            # l_ can define pants
            if file.startswith("l_"):
                icon_preset = {
                    'rotation':  (0, 0, 0),
                    'scale': (1.75, 1.75),
                    'offset': (0, 0.07),
                    'resolution': (64, 128),
                    'type': 'PERSP',
                    'fov': radians(28),
                    'side': 'RIGHT',
                    'key_power': 50,
                    'fill_power': 15,
                    'back_power': 16,
                    'shadow_catch': False,
                    'depth': 0
                }
                
            # s_ can define shoes    
            elif file.startswith("s_"):
                icon_preset = {
                    'rotation':  (0, 0, radians(-58)),
                    'scale': (0.85, 0.85),
                    'offset': (-0.04, 0.03),
                    'resolution': (64, 64),
                    'type': 'PERSP',
                    'fov': radians(43),
                    'side': 'RIGHT',
                    'key_power': 18,
                    'fill_power': 9,
                    'back_power': 3,
                    'shadow_catch': False,
                    'depth': 0
                }
                
            # Name the output file depending on the input file
            icon_preset['output'] = "/tmp/" + file[:-4] + ".png"
            
            # Create the icon can desired preset                
            render_icon(context = bpy.context, 
                        object = bpy.data.objects["Mesh"],
                        rotation = icon_preset['rotation'],
                        scale = icon_preset['scale'],
                        offset = icon_preset['offset'], 
                        resolution = icon_preset['resolution'], 
                        type = icon_preset['type'], 
                        fov = icon_preset['fov'],
                        side = icon_preset['side'],
                        key_power = icon_preset['key_power'], 
                        fill_power = icon_preset['fill_power'], 
                        back_power = icon_preset['back_power'],
                        shadow_catch = icon_preset['shadow_catch'],
                        depth = icon_preset['depth'],
                        output = icon_preset['output'], 
                        format = 'PNG', 
                        dxgi = None)
                        
            # Could import the produced icon into the compositor for:
            # - color correction,
            # - artistic effects,
            # - projected shadows,
            # - or whatever else...
            
            # Clean the scene before moving on to the next mesh            
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
            
            # Purge orphan data left unused
            override = bpy.context.copy()
            override["area.type"] = ['OUTLINER']
            override["display_mode"] = ['ORPHAN_DATA']
            with bpy.context.temp_override(**override):
                bpy.ops.outliner.orphans_purge()
                