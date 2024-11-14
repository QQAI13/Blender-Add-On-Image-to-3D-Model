""" image to 3d blender tool made by qqai"""

bl_info = {
    "name": "Image Displacement Tool",
    "blender": (3, 0, 0),
    "category": "Object",
    "description": "Tool to import an image, create a plane with matching aspect ratio, subdivide it, and apply a displacement modifier with the image as texture."
}

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel, AddonPreferences
import os

class ImportImageAndSetupPlane(Operator):
    bl_idname = "object.import_image_and_setup_plane"
    bl_label = "Import Image"
    bl_description = "Imports an image, creates a plane with matching dimensions, subdivides, and applies displacement modifier with image texture"
    
    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Load the image
        try:
            img = bpy.data.images.load(self.filepath)
        except RuntimeError:
            self.report({'ERROR'}, "Cannot load image")
            return {'CANCELLED'}
        
        # Create a plane and match the image dimensions
        width, height = img.size
        aspect_ratio = width / height
        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = context.object
        plane.name = "Displacement_Plane"
        
        # Adjust plane scale to match the image's aspect ratio
        plane.scale.x = aspect_ratio
        plane.scale.y = 1

        # Subdivide the plane
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=100)
        bpy.ops.mesh.subdivide(number_cuts=10)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add displacement modifier
        disp_mod = plane.modifiers.new(name="Displacement", type='DISPLACE')
        
        # Create a new texture for the displacement
        disp_texture = bpy.data.textures.new(name="Disp_Texture", type='IMAGE')
        disp_texture.image = img
        disp_mod.texture = disp_texture
        
        # Adjust displacement modifier settings
        disp_mod.texture_coords = 'UV'
        disp_mod.strength = 1.0

        
        
        # UV unwrap the plane for proper texture mapping
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, "Plane created and displacement modifier applied.")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VIEW3D_PT_custom_panel(Panel):
    bl_label = "Image Displacement Tool"
    bl_idname = "VIEW3D_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.import_image_and_setup_plane")

# Register and Unregister functions for add-on functionality
def register():
    bpy.utils.register_class(ImportImageAndSetupPlane)
    bpy.utils.register_class(VIEW3D_PT_custom_panel)

def unregister():
    bpy.utils.unregister_class(ImportImageAndSetupPlane)
    bpy.utils.unregister_class(VIEW3D_PT_custom_panel)

# Allows running the script in Blender Text Editor or as an add-on
if __name__ == "__main__":
    register()

