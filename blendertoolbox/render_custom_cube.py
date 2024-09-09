import bpy
from mathutils import Vector, Euler

def render_custom_cube(bounds, transparency=1.0, color=(1, 1, 1), shift=(0, 0, 0), orientation=(0, 0, 0)):
    """
    Renders a cube with specific dimensions, transparency, color, and orientation, and places a non-transparent dot at its center.
    
    :param bounds: Tuple (x_min, x_max, y_min, y_max, z_min, z_max)
    :param transparency: Transparency value (0.0 fully transparent, 1.0 fully opaque)
    :param color: RGB tuple for the cube color
    :param shift: Tuple (x_shift, y_shift, z_shift) to move the cube in space
    :param orientation: Tuple (x_angle, y_angle, z_angle) in degrees for the cube's orientation
    """
    x_min, x_max, y_min, y_max, z_min, z_max = bounds

    # Calculate the center and size of the cube based on bounds
    size_x = x_max - x_min
    size_y = y_max - y_min
    size_z = z_max - z_min
    center_x = (x_max + x_min) / 2
    center_y = (y_max + y_min) / 2
    center_z = (z_max + z_min) / 2

    # Create a cube and scale it
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, center_y, center_z))
    cube = bpy.context.object
    cube.scale = (size_x, size_y, size_z)  # Corrected scaling

    # Shift the cube (translation)
    cube.location.x += shift[0]
    cube.location.y += shift[1]
    cube.location.z += shift[2]

    # Rotate the cube using the provided orientation angles (convert degrees to radians)
    cube.rotation_euler = Euler((orientation[0], orientation[1], orientation[2]), 'XYZ')

    # Create a new material for the cube
    mat = bpy.data.materials.new(name="CustomCubeMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')

    # Set color and transparency
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)  # Color, alpha remains 1 for Base Color
    bsdf.inputs['Alpha'].default_value = transparency  # Transparency control

    # Enable transparency in the material
    mat.blend_method = 'BLEND'
    cube.data.materials.append(mat)
    
    voxel_size = min(size_x, size_y, size_z) / 10

    # Create a small non-transparent dot (e.g., a small sphere) at the center of the cube
    bpy.ops.mesh.primitive_uv_sphere_add(radius=voxel_size, location=(center_x, center_y, center_z))  # Small radius
    dot = bpy.context.object

    # Apply the same shift to the dot as the cube
    dot.location.x += shift[0]
    dot.location.y += shift[1]
    dot.location.z += shift[2]

    # Create a new material for the dot (non-transparent)
    dot_mat = bpy.data.materials.new(name="DotMaterial")
    dot_mat.use_nodes = True
    dot_bsdf = dot_mat.node_tree.nodes.get('Principled BSDF')
    dot_bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)  # Red color, fully opaque

    # Assign the material to the dot
    dot.data.materials.append(dot_mat)

    # Return the created cube and dot objects for further manipulation if needed
    return cube, dot
