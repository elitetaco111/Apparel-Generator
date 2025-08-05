#program to create NIL apparel images
#Created by Dave Nissly

import csv
import os
import json
from PIL import Image, ImageDraw, ImageFont

def number_render(image, coords, number, font_path):
    # TODO: Implement number rendering logic
    pass

def first_name_render(image, coords, first_name, font_path):
    # TODO: Implement first name rendering logic
    pass

def last_name_render(image, coords, last_name, font_path):
    # TODO: Implement last name rendering logic
    pass

def get_asset_folder(row):
    team = row['Team']
    color = row['Color List']
    art_type = row['Art Type']
    class_field = row['Class']
    # Get text after second ": "
    class_parts = class_field.split(": ")
    class_text = class_parts[2] if len(class_parts) > 2 else class_parts[-1]
    folder_name = f"{team}-{color}-{art_type}-{class_text}"
    return folder_name

def main():
    with open('to_create.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            asset_folder = get_asset_folder(row)
            asset_path = os.path.join(os.getcwd(), asset_folder)
            blank_img_path = os.path.join(asset_path, 'blank.png')
            coords_path = os.path.join(asset_path, 'coords.json')
            text_font_path = os.path.join(asset_path, 'text.otf')
            number_font_path = os.path.join(asset_path, 'number.ttf')

            # Load base image
            image = Image.open(blank_img_path).convert('RGBA')

            # Load coords
            with open(coords_path, 'r', encoding='utf-8') as f:
                coords = json.load(f)

            # Render number
            number_render(image, coords.get('Number', {}), row['Jersey Characters'], number_font_path)

            # Render first name
            first_name_render(image, coords.get('FirstName', {}), row['Player Name'].split()[0], text_font_path)

            # Render last name
            last_name_render(image, coords.get('LastName', {}), row['Player Name'].split()[-1], text_font_path)

            # Save image
            output_path = os.path.join(asset_path, f"{row['Name']}_output.png")
            image.save(output_path)

if __name__ == "__main__":
    main()

