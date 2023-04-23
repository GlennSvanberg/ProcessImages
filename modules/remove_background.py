import os
import time
from PIL import Image
from rembg import remove
import logging
def process_image(image_path, output_folder, archive_folder):
    # Load the input image
    time.sleep(5)  # Wait for the image to be fully written
    try:
        input_image = Image.open(image_path)
        logging.info("Removing background of image " + image_path )
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
        print("Removed background of image " + image_path)
    except Exception as e:
        # remove the image from the hot folder if there is an error
        os.remove(image_path)
        logging.error("Error processing image " + image_path + ": " + str(e))
        return False