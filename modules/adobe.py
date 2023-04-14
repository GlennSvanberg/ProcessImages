import os
import shutil
from PIL import Image
import zipfile
import subprocess
import math
import pysftp
import time

def process_image(image_path, output_folder, archive_folder, megapixels):
    time.sleep(1)  # Wait for the image to be fully written
    file_name, file_ext = os.path.splitext(image_path)
    output_jpg_path = os.path.join(output_folder, f"{os.path.basename(file_name)}_resized.jpg")
    output_eps_path = os.path.join(output_folder, f"{os.path.basename(file_name)}_resized.eps")
    optimized_eps_path = os.path.join(output_folder, f"{os.path.basename(file_name)}_optimized.eps")
    output_zip_path = os.path.join(output_folder, f"{os.path.basename(file_name)}.zip")

    try:
        img = Image.open(image_path)
        width, height = img.size

        new_size = calculate_new_size(width, height, megapixels)
        img_resized = img.resize(new_size, Image.ANTIALIAS)

        # Save as JPEG
        img_resized_rgb = img_resized.convert("RGB")
        img_resized_rgb.save(output_jpg_path)

        # Save as EPS
        img_resized_rgb.save(output_eps_path, format="EPS")

        img.close()

        # Optimize EPS file size using Ghostscript
        ghostscript_executable = "C:/Program Files/gs/gs10.01.1/bin/gswin64c.exe"
        gs_command = f'"{ghostscript_executable}" -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -sDEVICE=eps2write -r300 -sOutputFile="{optimized_eps_path}" "{output_eps_path}"'

        subprocess.run(gs_command, shell=True, check=True)

        # Create ZIP containing both files
        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            zipf.write(output_jpg_path, os.path.basename(output_jpg_path))
            zipf.write(optimized_eps_path, os.path.basename(optimized_eps_path))

        # Remove temporary files
        os.remove(output_eps_path)
        os.remove(optimized_eps_path)
        os.remove(output_jpg_path)

        # Move the original image to the archive folder
        os.makedirs(archive_folder, exist_ok=True)
        archive_path = os.path.join(archive_folder, os.path.basename(image_path))
        os.replace(image_path, archive_path)

        # Upload to Adobe Stock FTP
        upload_to_adobe_stock_sftp(output_zip_path)

    except Exception as e:
        print(f"Error processing {image_path}: {e}")


def upload_to_adobe_stock_sftp(file_path):
    sftp_host = "sftp.contributor.adobestock.com"
    username = "211314053"
    password = "JJvl$2N@"

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    try:
        # Connect to the Adobe Stock SFTP server
        with pysftp.Connection(sftp_host, username=username, password=password, cnopts=cnopts) as sftp:
            # Upload the file
            sftp.put(file_path)

            print(f"Successfully uploaded {file_path} to Adobe Stock via SFTP")
    except Exception as e:
        print(f"Error uploading {file_path} to Adobe Stock via SFTP: {e}")


def calculate_new_size(width, height, megapixels):
    aspect_ratio = float(width) / float(height)
    new_width = int(math.sqrt(megapixels * 1000000 * aspect_ratio))
    new_height = int(math.sqrt(megapixels * 1000000 / aspect_ratio))
    return new_width, new_height

