from PIL import Image
import os
import shutil

def process_image(input_path, output_folder, archive_folder, template_path):
    print(f"Adding image to template: {input_path}")
    input_image = Image.open(input_path)
    print(f"Image opened")
    print(f"Opening template image: {template_path}")
    template_image = Image.open(template_path)
    print(f"Template image opened")

    # Resize the input image to match either the width or height of the box
    box_width, box_height = 1100, 750
    image_aspect_ratio = input_image.width / input_image.height
    box_aspect_ratio = box_width / box_height

    if image_aspect_ratio > box_aspect_ratio:
        new_width = box_width
        new_height = int(box_width / image_aspect_ratio)
    else:
        new_width = int(box_height * image_aspect_ratio)
        new_height = box_height

    input_image = input_image.resize((new_width, new_height), Image.ANTIALIAS)
    print(f"Image resized")

    # Calculate the position to paste the image centered in the box
    box_x, box_y = 50, 200
    paste_x = box_x + (box_width - input_image.width) // 2
    paste_y = box_y + (box_height - input_image.height) // 2
    
    template_image.paste(input_image, (paste_x, paste_y))
    print(f"Image pasted on template")

    # Save the output as a JPEG file
    output_filename = os.path.splitext(os.path.basename(input_path))[0] + '.jpg'
    output_path = os.path.join(output_folder, output_filename)
    template_image.save(output_path, format='JPEG', quality=95)

    print(f"Image saved at {output_path}")

    # Move the original image to the archive folder
    archive_file_path = os.path.join(archive_folder, os.path.basename(input_path))
    shutil.move(input_path, archive_file_path)
