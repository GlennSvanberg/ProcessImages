import openai
import requests
import os
from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Replace 'your_openai_api_key' with your actual API key
openai.api_key = os.getenv('OPENAI_API_KEY')
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:/meme-384619-ef8e8872e6b3.json'

def process_image(src_path, output_folder, archive_folder, *args):
    # Analyze the image using Google Cloud Vision
    print(f"Processing {src_path}...")
    description = get_image_description(src_path)
    
    print(f"Image description: {description}")
    if not description:
        print(f"Error: Couldn't get image description for {src_path}")
        return

    # Generate meme text using OpenAI GPT-3
    meme_text = generate_meme_text(description)

    if not meme_text:
        print(f"Error: Couldn't generate meme text for {src_path}")
        return

    # Add the meme text to the image
    filename = os.path.basename(src_path)
    add_meme_text_to_image(src_path, output_folder, meme_text)
     # Move the original image to the archive folder
    os.makedirs(archive_folder, exist_ok=True)
    archive_path = os.path.join(archive_folder, filename)
    os.replace(src_path, archive_path)
    print(f"Moved {src_path} to {archive_path}")
    
def objects_relationship(obj1, obj2):
    
    # Check if the bounding boxes of two objects intersect
    def intersect(box1, box2):
        r1 = {
            'left': box1[0].x,
            'right': box1[1].x,
            'top': box1[0].y,
            'bottom': box1[2].y
        }
        r2 = {
            'left': box2[0].x,
            'right': box2[1].x,
            'top': box2[0].y,
            'bottom': box2[2].y
        }
        return not (r1['left'] > r2['right'] or r1['right'] < r2['left'] or r1['top'] > r2['bottom'] or r1['bottom'] < r2['top'])

    box1 = obj1.bounding_poly.normalized_vertices
    box2 = obj2.bounding_poly.normalized_vertices

    if intersect(box1, box2):
        return f"{obj1.name} and {obj2.name} are close to each other"
    return ""


def get_image_description(image_path, max_labels=3):
    
    client = vision.ImageAnnotatorClient()
    print("client created")
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    print("image created")
    features = [
        {"type_": vision.Feature.Type.LABEL_DETECTION},
        {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
    ]
    response = client.annotate_image({"image": image, "features": features})
    print("response created")
    descriptions = []

    # Labels
    labels = response.label_annotations
    if labels:
        descriptions.append("Labels: " + ', '.join([label.description for label in labels[:max_labels]]))
    print("labels created")
    # Objects
    objects = response.localized_object_annotations
    if objects:
        descriptions.append("Objects: " + ', '.join([obj.name for obj in objects]))

        # Check relationships between objects
        relationships = []
        for i, obj1 in enumerate(objects[:-1]):
            for obj2 in objects[i+1:]:
                relationship = objects_relationship(obj1, obj2)
                if relationship:
                    relationships.append(relationship)
            print("relationships created" + str(i))

        if relationships:
            descriptions.append("Relationships: " + ', '.join(relationships))

    if not descriptions:
        return None
    # add filename to description
    descriptions.append(f"Filename: {os.path.basename(image_path)}")
    description = '. '.join(descriptions)
    print(f"Image description: {description}")
    return description

def generate_meme_text(description):
    try:
        print(f"Generating meme text for {description}...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates funny meme text based on image descriptions. Given an image description, generate a very short and funny meme text."},
            {"role": "user", "content": "Image description: " + "Labels: Skull, Hair, Bone. Objects: Cat, Clothing. Relationships: Cat and Clothing are close to each other. Filename: cat.png"},
            {"role": "assistant", "content": "When you're trying to get a haircut but you're not sure if you're going to get a haircut."},
            {"role": "user", "content": f"Description: {description}"}
        ]
        print(f"Messages: {messages}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
        )
        print(f"Response: {response}")
        meme_text = response.choices[0].message.content.strip()
        print(f"Meme text: {meme_text}")
        
    except Exception as e:
        print(e)
        print(f"Error generating meme text: {e}")
        return None

    return meme_text


def add_meme_text_to_image(src_path, output_folder, meme_text):
    try:
        print(f"Adding meme text to {src_path}...")
        img = Image.open(src_path)
        img_width, img_height = img.size

        # Adjust font size based on image width
        font_size = int(img_width * 0.08)
        font = ImageFont.truetype("arial.ttf", font_size)

        # Split the meme text into multiple lines if necessary
        def split_text(text, max_chars_per_line):
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                if len(" ".join(current_line + [word])) <= max_chars_per_line:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

            lines.append(" ".join(current_line))
            return lines

        max_chars_per_line = int(img_width * 0.08)
        meme_lines = split_text(meme_text, max_chars_per_line)
        draw = ImageDraw.Draw(img)

        line_height = font.getsize("A")[1]
        total_height = line_height * len(meme_lines) + 20 * (len(meme_lines) - 1)
        img = ImageOps.expand(img, border=(0, 0, 0, total_height + 40), fill="black")

        draw = ImageDraw.Draw(img)

        y = img_height - total_height - 20
        for line in meme_lines:
            text_width, _ = draw.textsize(line, font)
            x = (img_width - text_width) // 2
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += line_height + 20

        
        output_file_path = os.path.join(output_folder, os.path.basename(src_path))
        # rename output file to _meme
        output_file_path = os.path.splitext(output_file_path)[0] + "_meme" + os.path.splitext(output_file_path)[1]
        img.save(output_file_path)

        print(f"Saved meme image to {output_file_path}")
    except Exception as e:
        print(f"Error adding meme text to image: {e}")