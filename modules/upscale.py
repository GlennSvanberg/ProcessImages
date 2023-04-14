import os
import cv2
import time

def process_image(image_path, output_folder, archive_folder, scale_factor):
    time.sleep(1) # Wait for the image to be fully written
    # Read the input image
    image = cv2.imread(image_path)

    # Validate if the image is read properly
    if image is None:
        print(f"Error: Unable to read image {image_path}")
        return

    # Calculate new dimensions
    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)

    # Perform the upscaling using linear interpolation
    upscaled_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    # Save the upscaled image
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_{int(scale_factor)}x.png")
    cv2.imwrite(output_path, upscaled_image)

    # Move the original image to the archive folder
    os.makedirs(archive_folder, exist_ok=True)
    archive_path = os.path.join(archive_folder, filename)
    os.replace(image_path, archive_path)
