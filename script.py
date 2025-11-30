import bpy, mathutils
from bpy.props import (StringProperty, IntProperty, PointerProperty, BoolProperty, FloatProperty)
from bpy.types import PropertyGroup
from mathutils import *; from math import *

class MyProperties(PropertyGroup):

    space_x_int: IntProperty(
        name = "Space X",
        description="Space between objects",
        default = 1,
        min=0
        )
    space_y_int: IntProperty(
        name = "Space Y",
        description="Space between objects",
        default = 1,
        min=0
        )
    row_int: IntProperty(
        name = "Row",
        description="Number of row",
        default = 1,
        min=1
        )
    
    my_string: StringProperty(
        name = 'Directory',
        description = "Export directory",
        default = "//Export\\",
        subtype='DIR_PATH'
        )
    
    my_bool: BoolProperty(
        name = "Include children",
        description = "include children in export",
        default = False)
        
    scale_float: FloatProperty(
        name = "Scale",
        description = "Global Scale",
        default = 1,
        min = 0.00000001
        )

class RJTool(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Tool"
    bl_idname = "rj.tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RJ_Tool'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rjtool = scene.my_tool

        
        layout.label(text="Clear Location:")
        row = layout.row()
        row.operator("object.location_clear")
        
        layout.label(text="Apply Scale/Rot:")
        row = layout.row()
        transform = row.operator("object.transform_apply", text="Apply Scale/Rot:")
        transform.location=False
        transform.rotation=True
        transform.scale=True
        
        layout.label(text="Rescale:")
        row = layout.row()
        button = row.operator("global.rescale")
        layout.prop(rjtool, "scale_float")
        
        layout.label(text="Spread:")
        layout.operator("objects.spread")
        
        layout.prop(rjtool, "space_x_int")
        layout.prop(rjtool, "space_y_int")
        layout.prop(rjtool, "row_int")
            
        layout.label(text="Export:")
        row = layout.row()
        button = row.operator("export.fbx")
        #layout.prop(rjtool, "my_bool")
        layout.prop(rjtool, "my_string")


class GlobalRescale(bpy.types.Operator):
    bl_label = "Global Rescale"
    bl_idname = "global.rescale"
    
    def execute(self, context):
        
        scene = context.scene
        scale = scene.my_tool.scale_float
        
        objList = bpy.context.selected_objects
        
        for select in objList :
            
            bpy.ops.object.select_all(action='DESELECT')
            select.select_set(True)
            bpy.ops.transform.resize(value=(scale, scale, scale))
            
        return {'FINISHED'}


class ExportFBX(bpy.types.Operator):
    bl_label = "Export fbx"
    bl_idname = "export.fbx"
    
    
    def execute(self, context):
        
        raytool = context.scene.my_tool
        dir = bpy.path.abspath(raytool.my_string)
        
        print("\n"+"\033[31m"+"START"+"\033[0m")
        
        objList = bpy.context.selected_objects
        
        for select in objList :
            
            name = select.name
            copy = select.copy()
            copy.data = select.data.copy()
            copy.animation_data_clear()
            
            copy.location = (0, 0, 0)
            copy.rotation_euler = (0, 0, 0)
            
            
            bpy.context.scene.collection.objects.link(copy)
            
            if copy.parent is not None:
                copy.scale = copy.parent.scale
                copy.parent = None
            
            bpy.ops.object.select_all(action='DESELECT')
            copy.select_set(True)
            
            bpy.ops.export_scene.fbx(filepath=dir+name+".fbx", use_selection=True)
            
            bpy.data.objects.remove(copy, do_unlink=True)
        
        bpy.ops.object.select_all(action='DESELECT')
        objList.clear()
        
        return {'FINISHED'}


class Spread(bpy.types.Operator):
    bl_idname = "objects.spread"
    bl_label = "Spread"
    
    
    def execute(self, context):
        
        scene = context.scene
        spaceX = scene.my_tool.space_x_int
        spaceY = scene.my_tool.space_y_int
        row = scene.my_tool.row_int
        
        
        
        index=0
        xMin=0
        xMax=0
        oldx=0
        i=0
        y=0
        objList = []
        
        
        for obj in bpy.context.selected_objects:
            
            if not obj.parent :
                
                objList.append(obj.name)
                index+=1
                print(obj.name)
                
            else :
                
                bpy.data.objects[obj.name].select_set(False)
        
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        
        objList = sorted(objList)
        
        j=index/row
        
        if j%1!=0:              #Ceil
            j = j-(j%1)+1
        
        for name in objList :     
            
            if i>=j:
                y+=1
                i=0
              
            obj = bpy.data.objects[name]
                
            xMin = (obj.bound_box[0][0])*-1 # x- compare to pivot point
            
              
            obj.location.y = y*spaceY   # new location y
                
            if i*spaceX!=0 :
                 obj.location.x = spaceX+xMax+xMin+oldx   # new location x
                    
            
            xMax = obj.bound_box[7][0] # x+ compare to pivot point
            oldx = obj.location.x # location for next object
            
            i+=1
        
        
            
        return {'FINISHED'}
        
        
def register():
    bpy.utils.register_class(MyProperties)
    bpy.utils.register_class(RJTool)
    bpy.utils.register_class(ExportFBX)
    bpy.utils.register_class(Spread)
    bpy.utils.register_class(GlobalRescale)
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
        
def unregister():
    bpy.utils.unregister_class(MyProperties)
    bpy.utils.unregister_class(RJTool)
    bpy.utils.unregister_class(ExportFBX)
    bpy.utils.unregister_class(Spread)
    bpy.utils.unregister_class(GlobalRescale)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()