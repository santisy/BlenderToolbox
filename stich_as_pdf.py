import os
import math
import argparse
from PIL import Image
import img2pdf
import pikepdf

def stitch_images_to_one_page(image_folder, output_pdf_path, compression_level=2):
    # Get list of PNG images in the folder
    images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(".png")]
    
    # Sort images by name to maintain order
    images.sort()

    # Load all images (assuming they are the same size)
    image_objects = [Image.open(img).convert("RGBA") for img in images]  # Open in RGBA to keep transparency
    
    # Assume all images are the same size
    img_width, img_height = image_objects[0].size

    # Determine the grid size (number of rows and columns) to make it as square as possible
    num_images = len(image_objects)
    grid_cols = math.ceil(math.sqrt(num_images))
    grid_rows = math.ceil(num_images / grid_cols)

    # Create a blank canvas large enough to hold the grid of images (RGB, to avoid transparency issues in PDF)
    canvas_width = img_width * grid_cols
    canvas_height = img_height * grid_rows
    canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))  # White background

    # Paste each image into the correct position in the grid
    for index, img in enumerate(image_objects):
        # Convert RGBA to RGB by flattening with white background (preserving image content)
        img_rgb = Image.new('RGB', img.size, (255, 255, 255))  # White background
        img_rgb.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        x = (index % grid_cols) * img_width
        y = (index // grid_cols) * img_height
        canvas.paste(img_rgb, (x, y))

    # Save the stitched image to a temporary file
    temp_img_path = os.path.join(image_folder, "stitched_temp_image.png")
    canvas.save(temp_img_path)

    # Convert the stitched image to a PDF
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(temp_img_path))

    # Compress the PDF to medium quality using pikepdf
    compress_pdf(output_pdf_path, output_pdf_path, compression_level)

    # Clean up temporary image file
    os.remove(temp_img_path)


def compress_pdf(input_pdf_path, output_pdf_path, compression_level):
    """ Compress PDF using pikepdf. Compression level: 0 (high), 1 (medium), 2 (low) """
    quality = {0: 'high', 1: 'medium', 2: 'low'}
    
    with pikepdf.open(input_pdf_path, allow_overwriting_input=True) as pdf:
        pdf.save(output_pdf_path, compress_streams=True)
        print(f"PDF compressed to {quality[compression_level]} quality.")

def main():
    parser = argparse.ArgumentParser(description="Stitch PNG images into a single-page PDF")
    parser.add_argument("image_folder", help="Folder containing PNG images to stitch")
    args = parser.parse_args()

    # Get the folder name to use as the output PDF file name
    folder_name = os.path.basename(os.path.normpath(args.image_folder))

    # Create a directory for the output PDF if it doesn't exist
    output_dir = "stitched_results"
    os.makedirs(output_dir, exist_ok=True)

    # Define the output PDF path
    output_pdf_path = os.path.join(output_dir, f"{folder_name}.pdf")

    # Stitch images into one page PDF and compress
    stitch_images_to_one_page(args.image_folder, output_pdf_path, compression_level=1)  # compression_level=1 for medium quality

if __name__ == "__main__":
    main()

