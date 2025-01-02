# Blender_Icon_Generator

## Content of the addon

Versatile tool to generate icons for games or others. Fine tune while previewing in Blender and batch process with desired settings. 
Developed for Blender 4.3.2, other versions are not tested.
In short, the addon automatically creates a three-point lighting shot of the selected object with an adjusted framing. You can then manually fine tune the framing and lighting to your liking. When you are satisfied with a set of parameters you can use that preset for other similar assets, either manually or with a python script for batch processing with a single click. 

Each paramater works as follows:
- **Item:** the object you want to generate an icon from. Only objects that can hold material data are shown.
- **Rotation:** the 3D rotation of the object in the 3D space. Camera, framing and lights get re-arranged automatically to ensure an adjusted shot.
- **Scale:** the 2D scale of the object in the camera view space. Use to fine tune the size of the object in the shot. Lights get resized accordingly.
- **Offset:** the 2D positional offset of the object in the camera view space. Use to fine tune the location of the object in the shot. Lights get re-positioned accordingly.
- **Resolution:** the resoltion of the output file. The camera gets re-positioned accordingly.
- **Type:** the type of camera used for the shot. Either Orthographic or Perspective.
- **FOV:** the Field Of View of the perspective camera. The camera gets re-positioned accordingly.
- **Key Light:** the power of the key light. It determines the shot's overall design.
- **Fill Light:** the power of the fill light. It balances the key by illuminating shaded surfaces.
- **Back Light:** the power of the back light. It gives the subject a rim of light, serving to separate the subject from the background and highlighting contours.
- **Output File:** the path in which the output file gets written. The extension gets adjusted depending on the file format.
- **File Format:** the format of the output file. Either PNG, Targa or DDS. The extension of the output file gets adjusted depending on it.
- **DXGI Format:** the compression method used by the DDS output file. Either BC1, BC3, BC5 or BC7.
- **Preview Button:** enables or disables preview to allow fine tuning parameters with visual feedback. Enabling the preview locks the user inputs except for mouse movements and left clicks. This is meant to limit the damages the user can cause to what the addon is trying to do for them. Left clicks can still cause a lot of damages, so still be careful when preview is enabled.
- **Render Button:** creates the output file with the defined set of parameters, whether the preview is enabled of not.

## Recommendations

- The addon is able to leverage the [DDS Addon](https://github.com/matyalatte/Blender-DDS-Addon/releases). The option to generate your icon as DDS won't appear if the addon is not installed.

## Limitations

- When preview is enabled, the user's left clicks are authorised everywhere in the UI (unfortunately not just limited to the side panel), thus empowering the user with the necessary means to break the addon. 

## Demonstration

Because an action speaks louder than words, here is the addon in action:

[![Addon Video](https://i.ytimg.com/vi/HxzlBzgtcEY/maxresdefault.jpg)](https://www.youtube.com/watch?v=HxzlBzgtcEY)

*Note that the icons produced by the script at the end are different because the custom normals were imported with the script while they were not during the rest of the video.*

And here is an example script that you can use (and rework) for batch processing:

```python
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
            # - or whatever else
                
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
                    'key_power': 50,
                    'fill_power': 15,
                    'back_power': 16,
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
                    'key_power': 18,
                    'fill_power': 9,
                    'back_power': 3,
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
                        key_power = icon_preset['key_power'], 
                        fill_power = icon_preset['fill_power'], 
                        back_power = icon_preset['back_power'], 
                        output = icon_preset['output'], 
                        format = 'PNG', 
                        dxgi = None)
            
            # Clean the scene before moving on to the next mesh            
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
            
            # Purge orphan data left unused
            override = bpy.context.copy()
            override["area.type"] = ['OUTLINER']
            override["display_mode"] = ['ORPHAN_DATA']
            with bpy.context.temp_override(**override):
                bpy.ops.outliner.orphans_purge()
```

*This script is available in the addon as batch_process_example.py*

## Documentation

Some information on [Three-point lighting](https://en.wikipedia.org/wiki/Three-point_lighting)

Copyright (c) 2025 Ard Carraigh

This project is licensed under the terms of the Creative Commons Attribution-NonCommercial 4.0 International Public License.
