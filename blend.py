import json
import os
import argparse
import blendertoolbox as bt
import numpy as np
import trimesh

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", type=str, required=True)
parser.add_argument("-o", "--output_index", type=int, required=True)
parser.add_argument("-r", "--resolution", type=int, default=1440)
parser.add_argument("-f", "--force_update", action="store_true")

def normalize_mesh(mesh):
    """
    Normalize the mesh to the origin and scale by the maximum diagonal distance.
    """
    # Calculate the bounding box
    bounds = mesh.bounds
    # Find the diagonal of the bounding box
    diagonal = np.linalg.norm(bounds[1] - bounds[0])
    # Translate the mesh to center it at the origin
    translation = -mesh.centroid
    # Scale the mesh by the diagonal
    scale = 1.0 / diagonal
    # Apply the transformations
    mesh.apply_translation(translation)
    mesh.apply_scale(scale)
    return mesh

args = parser.parse_args()
os.makedirs("./output_images", exist_ok=True)
os.makedirs("./temp_obj", exist_ok=True)

'''
RENDER A MESH STEP-BY-STEP:
1. run "python default_mesh.py" in terminal, then terminate the code when it starts rendering. This step outputs a "test.blend"
2. open "test.blend" with your blender software
3. in blender UI, adjust:
    - "mesh_location", "mesh_rotation", "mesh_scale" of the mesh
4. type in the adjusted mesh parameters from UI to "default_mesh.py"
5. run "python default_mesh.py" again (wait a couple minutes) to output your final image
'''

obj_name = os.path.basename(args.input_file).split(".")[0]
output_path = os.path.join("./output_images", f"{obj_name}_{args.output_index}.png")
json_output = os.path.join("./output_images", f"{obj_name}_{args.output_index}.json")
input_path = os.path.join("./temp_obj", f"{obj_name}_normalized.obj")
mesh = trimesh.load(args.input_file)
mesh = normalize_mesh(mesh)
mesh.export(input_path)

arguments = {
  "output_path": output_path,
  "image_resolution": [args.resolution, args.resolution], # recommend >1080 for paper figures
  "number_of_samples": 200, # recommend >200 for paper figures
  "mesh_path": input_path, # either .ply or .obj
  "mesh_position": (1.5042, 0.027193, 1.0916), # UI: click mesh > Transform > Location
  "mesh_rotation": (-172.82, 24.136, -171.62),
  "mesh_scale": (1.5, 1.5, 1.5), # UI: click mesh > Transform > Scale
  "shading": "smooth", # either "flat" or "smooth"
  "subdivision_iteration": 0, # integer
  "mesh_RGB": [26 / 255.0, 150 / 255.0, 173 / 255.0], #coral
  "light_angle": (6, -30, -155) # UI: click Sun > Transform > Rotation
}

if not args.force_update:
    if os.path.isfile(json_output):
        with open(json_output, "r") as f:
            arguments = json.load(f)
    
with open(json_output, "w") as f:
    json.dump(arguments, f, indent=2)

# Remove all planes in the scene
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.name.startswith('Plane'):
        bpy.data.objects.remove(obj, do_unlink=True)

bt.render_mesh_default(arguments)

