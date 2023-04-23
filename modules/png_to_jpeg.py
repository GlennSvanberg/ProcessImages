from PIL import Image
import os

def process_image(src_path, output_folder, archive_folder, *args):
    try:
        img = Image.open(src_path)
    except IOError as e:
        print(f"Error opening image {src_path}: {e}")
        return

    file_name, _ = os.path.splitext(os.path.basename(src_path))
    jpg_file_path = os.path.join(output_folder, f"{file_name}.jpg")

    try:
        img = img.convert("RGB")
        img.save(jpg_file_path, "JPEG", quality=95)
    except Exception as e:
        print(f"Error converting {src_path} to JPEG: {e}")
        return

    # Move the original file to the archive folder
    try:
        archive_file_path = os.path.join(archive_folder, os.path.basename(src_path))
        os.rename(src_path, archive_file_path)
    except OSError as e:
        print(f"Error moving {src_path} to the archive folder: {e}")
        return

    print(f"Converted {src_path} to JPEG and saved it as {jpg_file_path}")
