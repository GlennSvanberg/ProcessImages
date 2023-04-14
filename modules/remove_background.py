import os
import time
from PIL import Image
from rembg import remove

def process_image(image_path, output_folder, archive_folder):
    # Load the input image
    time.sleep(1)  # Wait for the image to be fully written
    input_image = Image.open(image_path)

    # Remove the background
    output_image = remove(input_image)

    # Save the processed image
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_transparent.png")
    output_image.save(output_path, "PNG")
    
    # Move the original image to the archive folder
    os.makedirs(archive_folder, exist_ok=True)
    archive_path = os.path.join(archive_folder, filename)
    os.replace(image_path, archive_path)
