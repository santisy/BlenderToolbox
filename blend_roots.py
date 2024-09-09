import json
import os
import argparse
import blendertoolbox as bt
import glob
import numpy as np
import trimesh

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, required=True, 
        help="Input folder or file.")
parser.add_argument("-o", "--output_index", type=int, required=True)
parser.add_argument("-r", "--resolution", type=int, default=1440)
parser.add_argument("-f", "--force_update", action="store_true")
parser.add_argument("-n", "--no_plane", action="store_true")
parser.add_argument("-d", "--output_folder", type=str, default="")
parser.add_argument("-v", "--voxel-txt", type=str, default=None)

def normalize_mesh(mesh):
    """
    Normalize the mesh to the origin and scale by the maximum diagonal distance.
    """
    # Calculate the bounding box
    bounds = mesh.bounds
    # Find the diagonal of the bounding box
    diagonal = np.linalg.norm(bounds[1] - bounds[0])
    # Translate the mesh to center it at the origin
    translation = - (bounds[0] + bounds[1]) / 2.0
    # Scale the mesh by the diagonal
    scale = 1.0 / diagonal
    # Apply the transformations
    mesh.apply_translation(translation)
    mesh.apply_scale(scale)
    return mesh

args = parser.parse_args()
output_dir = os.path.join("output_images", args.output_folder)
os.makedirs(output_dir, exist_ok=True)
os.makedirs("./temp_obj", exist_ok=True)

obj_name = os.path.basename(args.input).split(".")[0]
output_path = os.path.join(output_dir, f"{obj_name}_{args.output_index}.png")
json_output = os.path.join(output_dir, f"{obj_name}_{args.output_index}.json")
input_path = os.path.join("./temp_obj", f"{obj_name}_normalized.obj")
mesh = trimesh.load(args.input)
mesh = normalize_mesh(mesh)
mesh.export(input_path)

arguments = {
  "output_path": output_path,
  "image_resolution": [args.resolution, args.resolution], # recommend >1080 for paper figures
  "number_of_samples": 200, # recommend >200 for paper figures
  "mesh_path": input_path, # either .ply or .obj
  "mesh_position": (0, 0, 0), # UI: click mesh > Transform > Location
  #"mesh_rotation": (150, -360, 270),
  "mesh_rotation": (0, 0, 0),
  "mesh_scale": (1.0, 1.0, 1.0), # UI: click mesh > Transform > Scale
  "shading": "smooth", # either "flat" or "smooth"
  "subdivision_iteration": 0, # integer
  "mesh_RGB": [185 / 255.0, 157 / 255.0, 212 / 255.0], #coral
  "ground_location": (0.38244, 0.19607, 0.38647),
  "light_location": (2.35055, 0.076824, -2.3451),
  "light_angle": (-218.58, -21.71, 64.383), # UI: click Sun > Transform > Rotation
  "camLocation": (0.035952, 0.5298, -1.3928),
  "camRotation": (160, 0, 180),
}

if not args.force_update:
    if os.path.isfile(json_output):
        with open(json_output, "r") as f:
            arguments = json.load(f)
    
with open(json_output, "w") as f:
    json.dump(arguments, f, indent=2)

voxels = []
if args.voxel_txt is not None:
    with open(args.voxel_txt, "r") as f:
        voxel_lines = f.readlines()
    for v_l in voxel_lines:
        v_l = v_l.strip().split("\t")[0]
        voxels.append([float(x) for x in v_l.split(",")])

bt.render_mesh_with_voxels(arguments, voxels, no_plane=args.no_plane)
os.remove(input_path)

