# Author: Mike Long
# Date: 02-26-2025
# Description: Blender Script to extracts icons from toolbar.blend file and saves them as PNG files
# toolbar.blend can be found in the blender-assets git submodule: link: https://projects.blender.org/blender/blender-assets 
# 
 
import bpy
import os
import math

# Get the current .blend file directory
blend_file_path = bpy.data.filepath
blend_file_dir = os.path.dirname(blend_file_path)

# Create output directory if it doesn't exist
output_dir = os.path.join(blend_file_dir, "blenderIcons")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Store the original state to restore later
original_active_object = bpy.context.active_object
original_selected_objects = bpy.context.selected_objects
original_hide_status = {obj.name: obj.hide_viewport for obj in bpy.data.objects}

# Store original render settings
original_render_settings = {
    'engine': bpy.context.scene.render.engine,
    'resolution_x': bpy.context.scene.render.resolution_x,
    'resolution_y': bpy.context.scene.render.resolution_y,
    'resolution_percentage': bpy.context.scene.render.resolution_percentage,
    'film_transparent': bpy.context.scene.render.film_transparent,
    'filepath': bpy.context.scene.render.filepath
}

# Setup render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' 
bpy.context.scene.render.resolution_x = 256
bpy.context.scene.render.resolution_y = 256
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.film_transparent = True 


def setup_top_view_camera(obj):
    # Create a new Render camera if none exists
    if 'RenderCam' not in bpy.data.objects:
        cam_data = bpy.data.cameras.new('RenderCam')
        cam = bpy.data.objects.new('RenderCam', cam_data)
        bpy.context.collection.objects.link(cam)
    else:
        cam = bpy.data.objects['RenderCam']
    
    # Set as active camera
    bpy.context.scene.camera = cam
    
    # Make the object active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Get the object's dimensions and center
    bound_box = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum((Vector(b) for b in bound_box), Vector()) / 8
    
    # Calculate the distance needed to frame the object
    max_dim = max(obj.dimensions.x, obj.dimensions.y)
    distance = max_dim * 2.5  # Adjust this factor as needed
    
    # Position the camera directly above the object
    cam.location = Vector((center.x, center.y, center.z + distance))
    
    # Point the camera straight down
    cam.rotation_euler = (0, 0, 0)  # Reset rotation
    
    # Set orthographic if you want a true top-down view without perspective
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = max_dim * 1.2  # Adjust scale to fit object
    
    return cam


# Import Vector if it's not already available
if 'Vector' not in locals():
    from mathutils import Vector

# Get current view layer
view_layer = bpy.context.view_layer

# Iterate objects in layer
for obj in view_layer.objects:
        if obj.parent is None and obj.visible_get() and obj.type == "MESH":
            print(f"Processing object: {obj.name}")

            cam = setup_top_view_camera(obj)

            # Set the output path for the render
            safe_name = "".join([c for c in obj.name if c.isalpha() or c.isdigit() or c==' ' or c=='.' or c=='_']).rstrip()
            output_path = os.path.join(output_dir, f"{safe_name}.png")
            bpy.context.scene.render.filepath = output_path
            
            # Render the image
            bpy.ops.render.render(write_still=True)
            
            print(f"Rendered {obj.name} to {output_path}")     
    
# Restore original settings
bpy.context.scene.render.engine = original_render_settings['engine']
bpy.context.scene.render.resolution_x = original_render_settings['resolution_x']
bpy.context.scene.render.resolution_y = original_render_settings['resolution_y']
bpy.context.scene.render.resolution_percentage = original_render_settings['resolution_percentage']
bpy.context.scene.render.film_transparent = original_render_settings['film_transparent']
bpy.context.scene.render.filepath = original_render_settings['filepath']    