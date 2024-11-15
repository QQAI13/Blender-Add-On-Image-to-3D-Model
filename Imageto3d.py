""" image to 3d blender tool made by qqai"""

bl_info = {
    "name": "Image Displacement Tool",
    "blender": (3, 0, 0),
    "category": "Object",
    "description": "Tool to import an image, create a plane with matching aspect ratio, subdivide it, and apply a displacement modifier with the image as texture."
}

import bpy, bmesh
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator, Panel, AddonPreferences
import os

class ImportImageAndSetupPlane(Operator):
    bl_idname = "object.import_image_and_setup_plane"
    bl_label = "Import Image"
    bl_description = "Imports an image, creates a plane with matching dimensions, subdivides, and applies displacement modifier with image texture"
    
    filepath: StringProperty(subtype="FILE_PATH")
    desired_height: FloatProperty(
        name="Desired Height",
        description="Set the height of the displaced model",
        default=1.0,
        min=0.0
    )

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
        desired_height = context.scene.desired_height
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
        bpy.ops.object.mode_set(mode='EDIT')
        disp_mod = plane.modifiers.new(name="Displacement", type='DISPLACE')
        
        # Create a new texture for the displacement
        disp_texture = bpy.data.textures.new(name="Disp_Texture", type='IMAGE')
        disp_texture.image = img
        disp_mod.texture = disp_texture
        
        # Adjust displacement modifier settings
        disp_mod.texture_coords = 'UV'
        disp_mod.strength = 1.0
        
        # bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply the displacement modifier
        bpy.context.view_layer.objects.active = plane  # Ensure the plane is the active object
        bpy.ops.object.modifier_apply(modifier=disp_mod.name)

        # Switch to edit mode to delete bottom vertices
        bpy.ops.object.mode_set(mode='EDIT')

        # Enter wireframe mode
        bpy.context.space_data.shading.type = 'WIREFRAME'

        # Initialize bmesh to work directly on the mesh data
        bm = bmesh.from_edit_mesh(plane.data)

        # Find the maximum Z coordinate (top level)
        max_z = max(v.co.z for v in bm.verts)
        min_z = min(v.co.z for v in bm.verts)
        threshold = 0.1
        self.report({'INFO'}, f"max z: {max_z}, min z: {min_z}" )

        for v in bm.verts:
            v.select = (v.co.z < (min_z + threshold))

        # # Delete the selected vertices (everything except the top lid)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.select], context='VERTS')
        
        # # Update the mesh and exit edit mode
        bmesh.update_edit_mesh(plane.data)
        
        # # Go back to object mode, and flatten on Z-axis
        # bpy.ops.object.mode_set(mode='OBJECT')

        # Iterate over all vertices and set their Z coordinate to 0 if they are selected
        for vert in bm.verts:
            vert.co.z = 0  # Set Z coordinate to 0

        bmesh.update_edit_mesh(plane.data)

        # bpy.context.space_data.shading.type = 'SOLID'

        self.report({'INFO'}, f"Desired height: {desired_height}")

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, desired_height)})
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
        layout.prop(context.scene, "desired_height", text="Desired Height")
        layout.operator("object.import_image_and_setup_plane", text="Import Image")

# Register and Unregister functions for add-on functionality
def register():
    bpy.utils.register_class(ImportImageAndSetupPlane)
    bpy.utils.register_class(VIEW3D_PT_custom_panel)
    bpy.types.Scene.desired_height = FloatProperty(
        name="Desired Height",
        description="Set the height of the displaced model",
        default=1.0,
        min=0.0
    )

def unregister():
    bpy.utils.unregister_class(ImportImageAndSetupPlane)
    bpy.utils.unregister_class(VIEW3D_PT_custom_panel)
    del bpy.types.Scene.desired_height

# Allows running the script in Blender Text Editor or as an add-on
if __name__ == "__main__":
    register()

