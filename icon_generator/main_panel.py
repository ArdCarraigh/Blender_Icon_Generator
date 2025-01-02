# -*- coding: utf-8 -*-
# main_panel.py

import bpy
from bpy.props import FloatProperty, PointerProperty, StringProperty, FloatVectorProperty, IntVectorProperty, EnumProperty, BoolProperty
from bpy.types import Operator
from icon_generator.render_tools import render_icon
import numpy as np
from math import atan, sqrt, tan

class PreviewIcon(Operator):
    """Preview Icon"""
    bl_idname = "icon_generator.preview_icon"
    bl_label = "Preview Icon"
    bl_options = {'REGISTER', 'UNDO'}
    
    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    def execute(self, context):
        return {'FINISHED'}
    
    def modal(self, context, event):
        if event.type in ['LEFTMOUSE', 'MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
            return {'PASS_THROUGH'}
                
        elif not context.window_manager.icon_generator.PreviewBool:
            self.execute(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
class RenderIcon(Operator):
    """Render Icon"""
    bl_idname = "icon_generator.render_icon"
    bl_label = "Render Icon"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.context.scene.cursor.rotation_euler = (0.0, 0.0, 0.0)
        wm = context.window_manager.icon_generator
        dds_dxgi = None
        if wm.FileFormat == 'DDS':
            dds_dxgi = wm.DxgiFormat
        fov = 0
        if wm.Type == 'PERSP':
            fov = wm.FOV
        render_icon(context, wm.FocusItem, wm.Rotation, wm.Scale, wm.Offset, 
                    wm.Resolution, wm.Type, fov, 
                    wm.KeyLight, wm.FillLight, wm.BackLight,  
                    wm.OutputFile, wm.FileFormat, dds_dxgi)
        return {'FINISHED'}

class IconGeneratorMainPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Icon Generator'
    bl_idname = 'VIEW3D_PT_Icon_Generator_panel'
    bl_label = 'Icon Generator'
    
    def draw(self, context):
        wm = context.window_manager.icon_generator
        layout = self.layout
        row = layout.row()
        box = row.box()
        box.label(text="Focus Object", icon='OBJECT_DATAMODE')
        box_row = box.row()
        box_row.enabled = not wm.PreviewBool
        box_row.prop(wm, "FocusItem", text = 'Item')
        if wm.FocusItem and (wm.FocusItem.users == 0 or len(wm.FocusItem.users_scene) == 0):
            wm.FocusItem = None
        box_row = box.row()
        col = box_row.column()
        col.prop(wm, "Rotation", text = 'Rotation')
        box_row = box.row()
        col = box_row.column()
        col.prop(wm, "Scale", text = 'Scale')
        box_row = box.row()
        col = box_row.column()
        col.prop(wm, "Offset", text = 'Offset')
        
        row = layout.row()
        box = row.box()
        box.label(text="Camera", icon='SCENE')
        box_row = box.row()
        col = box_row.column()
        col.prop(wm, "Resolution", text = 'Resolution')
        box_row = box.row()
        box_row.prop(wm, "Type", text = 'Type')
        if wm.Type == 'PERSP':
            box_row = box.row()
            box_row.prop(wm, "FOV", text = 'FOV')
            
        row = layout.row()
        box = row.box()
        box.label(text="Lighting", icon='OUTLINER_OB_LIGHT')
        box_row = box.row()
        box_row.prop(wm, "KeyLight", text = 'Key Light')
        box_row = box.row()
        box_row.prop(wm, "FillLight", text = 'Fill Light')
        box_row = box.row()
        box_row.prop(wm, "BackLight", text = 'Back Light')
        
        row = layout.row()
        box = row.box()
        box.label(text="Output", icon='OUTPUT')
        box_row = box.row()
        box_row.prop(wm, "OutputFile", text = 'Output File')
        if not wm.OutputFile.endswith('.png') and wm.FileFormat == 'PNG':
            if wm.OutputFile.endswith('.dds') or wm.OutputFile.endswith('.tga'):
                wm.OutputFile = wm.OutputFile[:-3] + "png"
            else:
                wm.OutputFile += ".png"
        if not wm.OutputFile.endswith('.tga') and wm.FileFormat == 'TARGA':
            if wm.OutputFile.endswith('.dds') or wm.OutputFile.endswith('.png'):
                wm.OutputFile = wm.OutputFile[:-3] + "tga"
            else:
                wm.OutputFile += ".tga"
        if not wm.OutputFile.endswith('.dds') and wm.FileFormat == 'DDS':
            if wm.OutputFile.endswith('.png') or wm.OutputFile.endswith('.tga'):
                wm.OutputFile = wm.OutputFile[:-3] + "dds"
            else:
                wm.OutputFile += ".dds"
        box_row = box.row()
        box_row.prop(wm, "FileFormat", text = 'File Format')
        if wm.FileFormat == "DDS":
            box_row = box.row()
            box_row.prop(wm, "DxgiFormat", text = 'DXGI Format')
        box_row = box.row()
        if wm.PreviewBool:
            icon = "HIDE_OFF"
            txt = "Disable Preview"
        else:
            icon = "HIDE_ON"
            txt = "Enable Preview"
        box_row.enabled = wm.FocusItem is not None
        box_row.alert = wm.PreviewBool
        box_row.prop(wm, "PreviewBool", text = txt, icon = icon)
        box_row = box.row()
        box_row.enabled = wm.FocusItem is not None
        box_row.operator(RenderIcon.bl_idname, text = "Render", icon = "OUTPUT")
        
        return
    
def isObjectSelectable(self, object):
    return (hasattr(object.data, "materials") and object.users != 0 and len(object.users_scene) != 0)

def updatePreviewBool(self, context):
    if self.PreviewBool:
        bpy.ops.icon_generator.preview_icon('INVOKE_DEFAULT')
        
        # Set Scene                
        temp_scene = context.scene.copy()
        context.window.scene = temp_scene
        temp_scene.name = "SceneTemp_Icon"
        view_layer = context.view_layer
        temp_scene.render.film_transparent = True
        temp_scene.render.resolution_x = self.Resolution[0]
        temp_scene.render.resolution_y = self.Resolution[1]
        
        # Get Bounding Box and Set Transforms
        context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = self.FocusItem
        self.FocusItem.select_set(state=True)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        object = context.active_object
        object.name = "ObjectTemp_Icon"
        object.hide_viewport = False
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        object.rotation_euler = self.Rotation
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
        object.scale[0] = self.Scale[0]
        object.scale[2] = self.Scale[1]
        object.location[0] = self.Offset[0]
        object.location[2] = self.Offset[1]
        
        for obj in bpy.data.objects:
            if obj != object:
                obj.hide_viewport = True
                
        # Set Camera
        if self.Type == 'ORTHO':
            bpy.ops.object.camera_add(location = (loc_x,loc_plus_y,loc_z), rotation = (np.pi*0.5, 0, 0))
            cam = context.active_object
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = dim_max * (max(self.Resolution) / min(self.Resolution)) * 1.1
                
        elif self.Type == 'PERSP':
            loc_y = center_y - ((dim_max * 1.1) / 2) / tan(self.FOV / (max(self.Resolution) / min(self.Resolution)) / 2)
            bpy.ops.object.camera_add(location = (loc_x,loc_y,loc_z), rotation = (np.pi*0.5, 0, 0))
            cam = bpy.context.active_object
            cam.data.type = 'PERSP'
            cam.data.lens_unit = 'FOV'
            cam.data.angle = self.FOV
        
        cam.name = "CameraTemp_Icon"
        temp_scene.camera = cam
        
        # Add Lighting
        dist_plus_y = abs(center_y - loc_plus_y)
        deg_90 = np.pi*0.5
        deg_45 = np.pi*0.25
        loc_minus_y = bound_max[1] + dim_max
        dist_minus_y = abs(center_y - loc_minus_y)
        
        bpy.ops.object.light_add(type='AREA', location=(loc_x + dist_plus_y, loc_plus_y, bound_max[2]),
                                rotation=(atan(sqrt(2 * dist_plus_y ** 2) / (bound_max[2] - loc_z)), 0, deg_45))
        key_light = context.active_object
        key_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        key_light.data.energy = self.KeyLight
        key_light.name = "KeyLightTemp_Icon"
        self.KeyLight_BaseScale[0] = key_light.scale[0]
        self.KeyLight_BaseScale[1] = key_light.scale[1]
        self.KeyLight_BaseLocation[0] = key_light.location[0]
        self.KeyLight_BaseLocation[1] = key_light.location[2]
        key_light.scale[0] *= self.Scale[0]
        key_light.scale[1] *= self.Scale[1]
        key_light.location[0] += self.Offset[0]
        key_light.location[2] += self.Offset[1]
        
        bpy.ops.object.light_add(type='AREA', location=(loc_x - dist_plus_y, loc_plus_y, loc_z),
                                rotation=(deg_90, 0, -deg_45))
        fill_light = context.active_object
        fill_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        fill_light.data.energy = self.FillLight
        fill_light.name = "FillLightTemp_Icon"
        self.FillLight_BaseScale[0] = fill_light.scale[0]
        self.FillLight_BaseScale[1] = fill_light.scale[1]
        self.FillLight_BaseLocation[0] = fill_light.location[0]
        self.FillLight_BaseLocation[1] = fill_light.location[2]
        fill_light.scale[0] *= self.Scale[0]
        fill_light.scale[1] *= self.Scale[1]
        fill_light.location[0] += self.Offset[0]
        fill_light.location[2] += self.Offset[1]
        
        bpy.ops.object.light_add(type='AREA', location=(loc_x - dist_minus_y, loc_minus_y, loc_z),
                                rotation=(deg_90, 0, -deg_45*3))
        back_light = context.active_object
        back_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        back_light.data.energy = self.BackLight
        back_light.name = "BackLightTemp_Icon"
        self.BackLight_BaseScale[0] = back_light.scale[0]
        self.BackLight_BaseScale[1] = back_light.scale[1]
        self.BackLight_BaseLocation[0] = back_light.location[0]
        self.BackLight_BaseLocation[1] = back_light.location[2]
        back_light.scale[0] *= self.Scale[0]
        back_light.scale[1] *= self.Scale[1]
        back_light.location[0] += self.Offset[0]
        back_light.location[2] += self.Offset[1]
        
        context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                area.spaces[0].shading.type = 'RENDERED'
                break
        
    else:
        
        # Clean up
        bpy.data.objects.remove(bpy.data.objects["ObjectTemp_Icon"])
        bpy.data.objects.remove(bpy.data.objects["KeyLightTemp_Icon"])
        bpy.data.objects.remove(bpy.data.objects["FillLightTemp_Icon"])
        bpy.data.objects.remove(bpy.data.objects["BackLightTemp_Icon"])
        bpy.data.objects.remove(bpy.data.objects["CameraTemp_Icon"])
        bpy.data.scenes.remove(bpy.data.scenes["SceneTemp_Icon"])
      
        # Purge orphan data left unused
        override = context.copy()
        override["area.type"] = ['OUTLINER']
        override["display_mode"] = ['ORPHAN_DATA']
        with context.temp_override(**override):
            bpy.ops.outliner.orphans_purge()
            
        for obj in bpy.data.objects:
            obj.hide_viewport = False
            
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.type = 'MATERIAL'
                break
            
def updateResolution(self, context):
    if self.PreviewBool:
        temp_scene = bpy.data.scenes["SceneTemp_Icon"]
        temp_scene.render.resolution_x = self.Resolution[0]
        temp_scene.render.resolution_y = self.Resolution[1]
        updateType(self, context)
        
def updateType(self, context):
    if self.PreviewBool:
        cam = bpy.data.objects["CameraTemp_Icon"]
        object = bpy.data.objects["ObjectTemp_Icon"]
        bound_min = np.array(object.bound_box[0])
        bound_max = np.array(object.bound_box[6])
        center_y = (bound_min[1] + bound_max[1]) / 2
        dim_z = abs(bound_max[2] - bound_min[2])
        dim_x = abs(bound_max[0] - bound_min[0])
        dim_max = max(dim_z, dim_x)
        
        if self.Type == 'ORTHO':
            loc_y = bound_min[1] - dim_max
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = dim_max * (max(self.Resolution) / min(self.Resolution)) * 1.1
                
        elif self.Type == 'PERSP':
            loc_y = center_y - ((dim_max * 1.1) / 2) / tan(self.FOV / (max(self.Resolution) / min(self.Resolution)) / 2)
            cam.data.type = 'PERSP'
            cam.data.lens_unit = 'FOV'
            cam.data.angle = self.FOV
            
        cam.location[1] = loc_y
        
def updateFOV(self, context):
    if self.PreviewBool:
        cam = bpy.data.objects["CameraTemp_Icon"]
        object = bpy.data.objects["ObjectTemp_Icon"]
        bound_min = np.array(object.bound_box[0])
        bound_max = np.array(object.bound_box[6])
        center_y = (bound_min[1] + bound_max[1]) / 2
        dim_z = abs(bound_max[2] - bound_min[2])
        dim_x = abs(bound_max[0] - bound_min[0])
        dim_max = max(dim_z, dim_x)
        cam.data.angle = self.FOV
        cam.location[1] = center_y - ((dim_max * 1.1) / 2) / tan(self.FOV / (max(self.Resolution) / min(self.Resolution)) / 2)

def updateRotation(self, context):
    if self.PreviewBool:
        key_light = bpy.data.objects["KeyLightTemp_Icon"]
        fill_light = bpy.data.objects["FillLightTemp_Icon"]
        back_light = bpy.data.objects["BackLightTemp_Icon"]
        cam = bpy.data.objects["CameraTemp_Icon"]
        
        # Clean up
        bpy.data.objects.remove(bpy.data.objects["ObjectTemp_Icon"])
        self.FocusItem.hide_viewport = False
            
        # Get Bounding Box and Set Transforms
        context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = self.FocusItem
        self.FocusItem.select_set(state=True)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        object = context.active_object
        object.name = "ObjectTemp_Icon"
        object.hide_viewport = False
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        object.rotation_euler = self.Rotation
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
        object.scale[0] = self.Scale[0]
        object.scale[2] = self.Scale[1]
        object.location[0] = self.Offset[0]
        object.location[2] = self.Offset[1]
        
        self.FocusItem.hide_viewport = True
                
        # Set Camera
        if self.Type == 'ORTHO':
            cam.location = (loc_x,loc_plus_y,loc_z)
            cam.data.ortho_scale = dim_max * (max(self.Resolution) / min(self.Resolution)) * 1.1
                
        elif self.Type == 'PERSP':
            loc_y = center_y - ((dim_max * 1.1) / 2) / tan(self.FOV / (max(self.Resolution) / min(self.Resolution)) / 2)
            cam.location = (loc_x,loc_y,loc_z)
        
        # Add Lighting
        dist_plus_y = abs(center_y - loc_plus_y)
        deg_45 = np.pi*0.25
        loc_minus_y = bound_max[1] + dim_max
        dist_minus_y = abs(center_y - loc_minus_y)
        
        key_light.location = (loc_x + dist_plus_y, loc_plus_y, bound_max[2])
        key_light.rotation_euler = (atan(sqrt(2 * dist_plus_y ** 2) / (bound_max[2] - loc_z)), 0, deg_45)
        key_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        self.KeyLight_BaseScale[0] = key_light.scale[0]
        self.KeyLight_BaseScale[1] = key_light.scale[1]
        self.KeyLight_BaseLocation[0] = key_light.location[0]
        self.KeyLight_BaseLocation[1] = key_light.location[2]
        key_light.scale[0] *= self.Scale[0]
        key_light.scale[1] *= self.Scale[1]
        key_light.location[0] += self.Offset[0]
        key_light.location[2] += self.Offset[1]
        
        fill_light.location = (loc_x - dist_plus_y, loc_plus_y, loc_z)
        fill_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        self.FillLight_BaseScale[0] = fill_light.scale[0]
        self.FillLight_BaseScale[1] = fill_light.scale[1]
        self.FillLight_BaseLocation[0] = fill_light.location[0]
        self.FillLight_BaseLocation[1] = fill_light.location[2]
        fill_light.scale[0] *= self.Scale[0]
        fill_light.scale[1] *= self.Scale[1]
        fill_light.location[0] += self.Offset[0]
        fill_light.location[2] += self.Offset[1]
        
        back_light.location = (loc_x - dist_minus_y, loc_minus_y, loc_z)
        back_light.scale = (dim_x*1.5, dim_z*1.5, 1)
        self.BackLight_BaseScale[0] = back_light.scale[0]
        self.BackLight_BaseScale[1] = back_light.scale[1]
        self.BackLight_BaseLocation[0] = back_light.location[0]
        self.BackLight_BaseLocation[1] = back_light.location[2]
        back_light.scale[0] *= self.Scale[0]
        back_light.scale[1] *= self.Scale[1]
        back_light.location[0] += self.Offset[0]
        back_light.location[2] += self.Offset[1]
        
        context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
            
def updateScale(self, context):
    if self.PreviewBool:
        object = bpy.data.objects["ObjectTemp_Icon"]
        object.scale[0] = self.Scale[0]
        object.scale[2] = self.Scale[1]
        key_light = bpy.data.objects["KeyLightTemp_Icon"]
        key_light.scale[0] = self.KeyLight_BaseScale[0] * self.Scale[0]
        key_light.scale[1] = self.KeyLight_BaseScale[1] * self.Scale[1]
        fill_light = bpy.data.objects["FillLightTemp_Icon"]
        fill_light.scale[0] = self.FillLight_BaseScale[0] * self.Scale[0]
        fill_light.scale[1] = self.FillLight_BaseScale[1] * self.Scale[1]
        back_light = bpy.data.objects["BackLightTemp_Icon"]
        back_light.scale[0] = self.BackLight_BaseScale[0] * self.Scale[0]
        back_light.scale[1] = self.BackLight_BaseScale[1] * self.Scale[1]

def updateOffset(self, context):
    if self.PreviewBool:
        object = bpy.data.objects["ObjectTemp_Icon"]
        object.location[0] = self.Offset[0]
        object.location[2] = self.Offset[1]
        key_light = bpy.data.objects["KeyLightTemp_Icon"]
        key_light.location[0] = self.KeyLight_BaseLocation[0] + self.Offset[0]
        key_light.location[2] = self.KeyLight_BaseLocation[1] + self.Offset[1]
        fill_light = bpy.data.objects["FillLightTemp_Icon"]
        fill_light.location[0] = self.FillLight_BaseLocation[0] + self.Offset[0]
        fill_light.location[2] = self.FillLight_BaseLocation[1] + self.Offset[1]
        back_light = bpy.data.objects["BackLightTemp_Icon"]
        back_light.location[0] = self.BackLight_BaseLocation[0] + self.Offset[0]
        back_light.location[2] = self.BackLight_BaseLocation[1] + self.Offset[1]
            
def updateKeyLight(self, context):
    if self.PreviewBool:
        bpy.data.objects["KeyLightTemp_Icon"].data.energy = self.KeyLight
        
def updateFillLight(self, context):
    if self.PreviewBool:
        bpy.data.objects["FillLightTemp_Icon"].data.energy = self.FillLight
        
def updateBackLight(self, context):
    if self.PreviewBool:
        bpy.data.objects["BackLightTemp_Icon"].data.energy = self.BackLight
            
PROPS_Main_Panel = [
('FocusItem', PointerProperty(
        type=bpy.types.Object,
        name="Focus Item",
        description="Set the object for which you want to create an icon",
        poll = isObjectSelectable
    )),
('Resolution', IntVectorProperty(
        name="Resolution",
        description="Set the x and y resolutions of the output icon picture",
        size=2,
        default=(64,64),
        min=0,
        subtype='COORDINATES',
        update=updateResolution
    )),
('Type', EnumProperty(
        name="Camera Type",
        description="Set the camera type",
        items=(
            ('ORTHO', "Orthographic", "Set the camera type to orthographic"),
            ('PERSP', "Perspective", "Set the camara type to perspective")
            ),
        default='ORTHO',
        update=updateType
    )),
('FOV', FloatProperty(
        name="Field Of View",
        description="Set the field of view of the perspective camera",
        default=0.691,
        min=0.006,
        max=3.017,
        precision=1,
        subtype='ANGLE',
        update=updateFOV
    )),
('Rotation', FloatVectorProperty(
        name="Rotation",
        description="Set the x, y and z rotations of the focus object",
        size=3,
        default=(0,0,0),
        subtype='EULER',
        update=updateRotation
    )),
('Scale', FloatVectorProperty(
        name="Resolution",
        description="Set the x, y and z scales of the focus object",
        size=2,
        default=(1,1),
        subtype='COORDINATES',
        update=updateScale
    )),
('Offset', FloatVectorProperty(
        name="Offset",
        description="Set the x, y and z offsets of the focus object",
        size=2,
        default=(0,0),
        subtype='COORDINATES',
        update=updateOffset
    )),
('KeyLight', FloatProperty(
        name="Key Light Power",
        description="Set the power of the key light",
        default=10,
        min=0,
        step=10,
        precision=1,
        subtype="POWER",
        update=updateKeyLight
    )),
('KeyLight_BaseScale', FloatVectorProperty(
        name="Key Light Base Scale",
        description="Set the base scale of the key light",
        default=(1,1),
        size=2
    )),
('KeyLight_BaseLocation', FloatVectorProperty(
        name="Key Light Base Location",
        description="Set the base location of the key light",
        default=(0,0),
        size=2
    )),
('FillLight', FloatProperty(
        name="Fill Light Power",
        description="Set the power of the fill light",
        default=5,
        min=0,
        step=10,
        precision=1,
        subtype="POWER",
        update=updateFillLight
    )),
('FillLight_BaseScale', FloatVectorProperty(
        name="Key Light Base Scale",
        description="Set the base scale of the fill light",
        default=(1,1),
        size=2
    )),
('FillLight_BaseLocation', FloatVectorProperty(
        name="Key Light Base Location",
        description="Set the base location of the fill light",
        default=(0,0),
        size=2
    )),
('BackLight', FloatProperty(
        name="Back Light Power",
        description="Set the power of the back light",
        default=5,
        min=0,
        step=10,
        precision=1,
        subtype="POWER",
        update=updateBackLight
    )),
('BackLight_BaseScale', FloatVectorProperty(
        name="Key Light Base Scale",
        description="Set the base scale of the back light",
        default=(1,1),
        size=2
    )),
('BackLight_BaseLocation', FloatVectorProperty(
        name="Key Light Base Location",
        description="Set the base location of the back light",
        default=(0,0),
        size=2
    )),
("OutputFile", StringProperty(
        name = "Output File",
        subtype='FILE_PATH',
        default = "/tmp/tmp.png",
        description="Path to the output file"
    )),
("FileFormat", EnumProperty(
        name = "File Format",
        description = "Set the format of the output file",
        default = 'PNG',
        items =(
            ('PNG', "PNG", "Set the format of the output file to PNG"),
            ('TARGA', "TGA", "Set the format of the output file to TGA/Targa")
            ) if 'blender_dds_addon' not in bpy.context.preferences.addons else
            (
            ('PNG', "PNG", "Set the format of the output file to PNG"),
            ('TARGA', "TGA", "Set the format of the output file to TGA/Targa"),
            ('DDS', "DDS", "Set the format of the output file to DDS")
            )
    )),
("DxgiFormat", EnumProperty(
        name='DXGI Format',
        description="DXGI format for DDS",
        default='BC3_UNORM',
        items= (
        ('BC1_UNORM', "BC1_UNORM", "BC1_UNORM"),
        ('BC3_UNORM', "BC3_UNORM", "BC3_UNORM"),
        ('BC5_UNORM', "BC5_UNORM", "BC5_UNORM"),
        ('BC7_UNORM', "BC7_UNORM", "BC7_UNORM")
        )
    )),
("PreviewBool", BoolProperty(
        name='Preview Boolean',
        description="Enable/diable preview mode",
        default=False,
        update=updatePreviewBool
    ))
]

CLASSES_Main_Panel = [PreviewIcon, RenderIcon, IconGeneratorMainPanel]