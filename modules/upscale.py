from PIL import Image
import os
import shutil
from PIL import Image
import os
import shutil
from PIL import Image
import os
import shutil
import subprocess
import codecs
import sys
import time

# Example upscale:  D:\waifu2x-caffe\waifu2x-caffe-cui.exe -i Hotfolder\Upscale\2.png -o Output\Upscale\2_upscaled4x.png -s 4 -m noise_scale -n 0 --model_dir D:\waifu2x-caffe\models\photo --process cpu --model 1 --output_depth 8 
# Set encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def upscale_image_with_waifu2x(input_path, output_path, scale_factor):
    waifu2x_executable = "D:\\waifu2x-caffe\\waifu2x-caffe-cui.exe"

    # Parameters from the settings.ini
    mode = "noise_scale"
    noise_level = "0"
    process_type = "cpu"
    model_dir = "D:\\waifu2x-caffe\\models\photo"
    model = "1"
    use_tta = True
    output_depth = "8"
    output_ext = ".png"

    # Check if the output path has the correct extension
    output_path = os.path.splitext(output_path)[0] + output_ext

    args = [waifu2x_executable, "-i", input_path, "-o", output_path, "-s", str(scale_factor), "-m", mode, "-n", noise_level, "--model_dir", model_dir, "--process", process_type, "--model", model, "--output_depth", output_depth]

    if use_tta:
        args.append("--use_tta")

    print("Full command:", " ".join(args))

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip())
        error_output = process.stderr.readline()
        if error_output:
            print(f"Error: {error_output.strip()}")
        if output == '' and error_output == '' and process.poll() is not None:
            print(f"waifu2x-caffe-cui.exe process finished with return code {process.poll()}")
            break
    return process.poll()

def process_image(src_path, output_folder, archive_folder, scale_factor):
    try:
        print(f"Upscaling image: {src_path}")
        start_time = time.time()

        input_image = Image.open(src_path)
        input_filename = os.path.splitext(os.path.basename(src_path))[0]
        ext = os.path.splitext(os.path.basename(src_path))[1]
        output_filename = f"{input_filename}_upscaled{scale_factor}x{ext}"
        output_path = os.path.join(output_folder, output_filename)

        # Save the input image as a temporary file
        temp_input_path = os.path.join(output_folder, f"{input_filename}_temp{ext}")
        input_image.save(temp_input_path)
        print(f"Temporary input file saved at {temp_input_path}")

        # Call waifu2x to upscale the image
        print(f"Upscaling with waifu2x {scale_factor}x")
        upscale_image_with_waifu2x(temp_input_path, output_path, scale_factor)

        # Remove the temporary input file
        os.remove(temp_input_path)
        print(f"Temporary input file removed")

        print(f"Upscaled image saved at {output_path}")

        # Move the original image to the archive folder
        archive_file_path = os.path.join(archive_folder, os.path.basename(src_path))
        shutil.move(src_path, archive_file_path)

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time taken: {total_time:.2f} seconds")

    except Exception as e:
        print(f"Error upscaling image: {e}")



"""
import logging
import os
import time
from pathlib import Path
from PIL import Image
from super_image import EdsrModel, ImageLoader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import shutil
import warnings

def process_image(src_path, output_folder, archive_folder, scale_factor):
    try:
        print(f"Upscaling image: {src_path}")
        input_image = Image.open(src_path)
        inputs = ImageLoader.load_image(input_image)

        input_filename = os.path.splitext(os.path.basename(src_path))[0]
        ext = os.path.splitext(os.path.basename(src_path))[1]

        # First upscale with 2x model
        model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=2)
        preds_2x = model(inputs)
        output_filename_2x = f"{input_filename}_2x{ext}"
        print("Upscaling 2X")
        output_path_2x = os.path.join(output_folder, output_filename_2x)
        ImageLoader.save_image(preds_2x, output_path_2x)

        # Then upscale the 2x upscaled image with 4x model
        inputs_4x = ImageLoader.load_image(Image.open(output_path_2x))
        model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=4)
        preds_4x = model(inputs_4x)
        print("Upscaling 4X")
        output_filename_4x = f"{input_filename}_8x{ext}"
        output_path_4x = os.path.join(output_folder, output_filename_4x)
        ImageLoader.save_image(preds_4x, output_path_4x)

        print(f"Upscaled image saved at {output_path_4x}")

        # Move the original image to the archive folder
        archive_file_path = os.path.join(archive_folder, os.path.basename(src_path))
        shutil.move(src_path, archive_file_path)

        # Remove the intermediate upscaled image (2x)
        os.remove(output_path_2x)

    except Exception as e:
        print(f"Error upscaling image: {e}")
"""
"""
Linear upsample images using OpenCV
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
"""