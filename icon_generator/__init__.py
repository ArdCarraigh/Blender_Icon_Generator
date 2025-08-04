# -*- coding: utf-8 -*-
# __init__.py

bl_info = {
    "name": "Icon Generator",
    "author": "Ard Carraigh",
    "version": (1, 2),
    "blender": (4, 5, 1),
    "location": "3D View > Side Panel > Icon Generator",
    "description": "Preview and create icons",
    "doc_url": "https://github.com/ArdCarraigh/Blender_Icon_Generator",
    "tracker_url": "https://github.com/ArdCarraigh/Blender_Icon_Generator/issues",
    "support": "COMMUNITY",
    "category": "Tool",
}

import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, IntProperty
from icon_generator.main_panel import CLASSES_Main_Panel, PROPS_Main_Panel
    
class IconGeneratorProperties(PropertyGroup):
    placeholder: IntProperty(name="Placeholder")
    
PROPS = [*PROPS_Main_Panel]
CLASSES = [IconGeneratorProperties, *CLASSES_Main_Panel]

def register():
    for klass in CLASSES:
        bpy.utils.register_class(klass)
        
    setattr(bpy.types.WindowManager, "icon_generator", IconGeneratorProperties)
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.WindowManager.icon_generator, prop_name, prop_value)
    bpy.types.WindowManager.icon_generator = PointerProperty(type=IconGeneratorProperties)

def unregister():
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)

    delattr(bpy.types.WindowManager, "icon_generator")