import os
import cv2
import time

def process_image(image_path, output_folder, archive_folder, scale_factor):
    print("Starting process_image function")
    time.sleep(1)  # Wait for the image to be fully written
    # Read the input image with alpha channel
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Validate if the image is read properly
    if image is None:
        print(f"Error: Unable to read image {image_path}")
        return

    print("Image read successfully")

    # Calculate new dimensions
    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)

    # Check if the image has an alpha channel
    if image.shape[2] == 4:
        print("Image has alpha channel")  # Added print statement

        # Split the image into color and alpha channels
        channels = cv2.split(image)
        color = cv2.merge(channels[:3])
        alpha = channels[3]

        # Perform the upscaling using linear interpolation on the color and alpha channels
        upscaled_color = cv2.resize(color, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        upscaled_alpha = cv2.resize(alpha, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        # Merge the upscaled color and alpha channels
        upscaled_image = cv2.merge((*cv2.split(upscaled_color), upscaled_alpha))
    else:
        print("Image does not have alpha channel")  # Added print statement
        # Perform the upscaling using linear interpolation
        upscaled_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    print("Upscaling complete")

    # Save the upscaled image
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_{int(scale_factor)}x.png")
    cv2.imwrite(output_path, upscaled_image)

    print("Upscaled image saved")

    # Move the original image to the archive folder
    os.makedirs(archive_folder, exist_ok=True)
    archive_path = os.path.join(archive_folder, filename)
    os.replace(image_path, archive_path)
    print(f"Upscaled image {image_path}")
