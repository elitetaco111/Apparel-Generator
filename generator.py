#program to create NIL apparel images
#Created by Dave Nissly

import csv
import os
import json
from PIL import Image, ImageDraw, ImageFont

def number_render(image, coords, number, font_path):
    """
    Renders the number onto the image using the provided coordinates and styling.
    - Fills the height of the box (coords) with the number, keeping font scaling consistent.
    - Centers the number in the box.
    - Applies color and optional border/stroke.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = coords.get('coords', [0,0,0,0])
    box_width = x2 - x1
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))

    # Find font size that fits the height
    font_size = box_height
    font = ImageFont.truetype(font_path, font_size)
    bbox = font.getbbox(number)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Reduce font size until it fits the box height
    while text_height > box_height:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(number)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    # Center the text in the box
    text_x = x1 + (box_width - text_width) // 2
    text_y = y1 + (box_height - text_height) // 2

    # Draw border if needed
    if border and border_width > 0:
        # Draw text multiple times offset by border_width in all directions
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((text_x+dx, text_y+dy), number, font=font, fill=border_color)

    # Draw main text
    draw.text((text_x, text_y), number, font=font, fill=color)

def first_name_render(image, coords, first_name, font_path):
    """
    Renders the first name onto the image using the provided coordinates and styling.
    - Fills the height of the box (coords) with the name, keeping font scaling consistent.
    - Centers the name in the box.
    - Applies color, optional border/stroke, and custom letter spacing.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = coords.get('coords', [0,0,0,0])
    box_width = x2 - x1
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))
    spacing_factor = float(coords.get('spacing_factor', 0))

    # Find font size that fits the height
    font_size = box_height
    font = ImageFont.truetype(font_path, font_size)

    def get_text_size(text, font, spacing):
        width = 0
        max_height = 0
        for i, char in enumerate(text):
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            width += char_width
            max_height = max(max_height, char_height)
            if i < len(text) - 1:
                width += int(char_width * spacing)
        return width, max_height

    text_width, text_height = get_text_size(first_name, font, spacing_factor)

    # Reduce font size until it fits the box height
    while text_height > box_height:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = get_text_size(first_name, font, spacing_factor)

    # Center the text in the box
    text_x = x1 + (box_width - text_width) // 2
    text_y = y1 + (box_height - text_height) // 2

    # Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for char in first_name:
                    draw.text((cx+dx, text_y+dy), char, font=font, fill=border_color)
                    char_width = font.getbbox(char)[2] - font.getbbox(char)[0]
                    cx += char_width + int(char_width * spacing_factor)

    # Draw main text
    cx = text_x
    for char in first_name:
        draw.text((cx, text_y), char, font=font, fill=color)
        char_width = font.getbbox(char)[2] - font.getbbox(char)[0]
        cx += char_width + int(char_width * spacing_factor)

def last_name_render(image, coords, last_name, font_path):
    """
    Renders the last name onto the image using the provided coordinates and styling.
    - Fills the height of the box (coords) with the name, keeping font scaling consistent.
    - Stretches the letters and adds spacing as needed to fit BOTH the height and width of the box.
    - Centers the name in the box.
    - Applies color, optional border/stroke, and custom letter spacing.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = coords.get('coords', [0,0,0,0])
    box_width = x2 - x1
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))
    base_spacing_factor = float(coords.get('spacing_factor', 0))

    def get_text_size(text, font, spacing):
        width = 0
        max_height = 0
        char_widths = []
        for i, char in enumerate(text):
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            char_widths.append(char_width)
            width += char_width
            max_height = max(max_height, char_height)
            if i < len(text) - 1:
                width += int(char_width * spacing)
        return width, max_height, char_widths

    # 1. Find the largest font size that fits the box height
    min_font_size = 1
    max_font_size = box_height
    best_font_size = min_font_size
    while min_font_size <= max_font_size:
        mid_font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_path, mid_font_size)
        _, text_height, _ = get_text_size(last_name, font, base_spacing_factor)
        if text_height <= box_height:
            best_font_size = mid_font_size
            min_font_size = mid_font_size + 1
        else:
            max_font_size = mid_font_size - 1

    font = ImageFont.truetype(font_path, best_font_size)
    _, text_height, char_widths = get_text_size(last_name, font, 0)
    num_gaps = max(len(last_name) - 1, 0)

    # 2. Calculate required total width (including spacing and stretching)
    total_char_width = sum(char_widths)
    max_stretch = 1.5
    stretch_factor = min(box_width / total_char_width, max_stretch)
    stretched_width = total_char_width * stretch_factor
    remaining_width = box_width - stretched_width
    spacing = max(remaining_width / num_gaps, 0)

    # If stretch_factor is less than max_stretch, spacing will be 0 or negative, so clamp to 0 and recalc stretch
    if spacing < 0:
        spacing = 0
        stretch_factor = box_width / total_char_width

    # 3. Center the text in the box
    total_width = stretched_width + spacing * num_gaps
    text_x = x1 + (box_width - total_width) // 2
    text_y = y1
    # 4. Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(last_name):
                    char_img = Image.new("RGBA", (best_font_size * 2, best_font_size * 2), (0, 0, 0, 0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0, 0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    char_img = char_img.crop(char_bbox)
                    char_width = char_bbox[2] - char_bbox[0]
                    char_height = char_bbox[3] - char_bbox[1]
                    stretched_char_width = int(char_width * stretch_factor)
                    stretched_char_height = box_height  # Stretch vertically to fill box
                    char_img = char_img.resize((stretched_char_width, stretched_char_height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_char_width
                    if i < len(last_name) - 1:
                        cx += spacing

    # 5. Draw main text
    cx = text_x
    for i, char in enumerate(last_name):
        char_img = Image.new("RGBA", (best_font_size * 2, best_font_size * 2), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=color)
        char_bbox = char_img.getbbox()
        char_img = char_img.crop(char_bbox)
        char_width = char_bbox[2] - char_bbox[0]
        char_height = char_bbox[3] - char_bbox[1]
        stretched_char_width = int(char_width * stretch_factor)
        stretched_char_height = box_height  # Stretch vertically to fill box
        char_img = char_img.resize((stretched_char_width, stretched_char_height), Image.LANCZOS)
        image.paste(char_img, (int(cx), int(text_y)), char_img)
        cx += stretched_char_width
        #only add spacing if not the last character
        if i < len(last_name) - 1:
            cx += spacing

def render_sport(image, coords, sport_text, font_path):
    """
    Renders the sport text onto the image using the provided coordinates and styling.
    - Fits BOTH the height and width of the bounding box by stretching letters and adding even spacing.
    - Centers the sport text in the box.
    - Applies color, optional border/stroke, and custom letter spacing.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = coords.get('coords', [0,0,0,0])
    box_width = x2 - x1
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))
    base_spacing_factor = float(coords.get('spacing_factor', 0))

    def get_text_size(text, font, spacing):
        width = 0
        max_height = 0
        char_widths = []
        for i, char in enumerate(text):
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            char_widths.append(char_width)
            width += char_width
            max_height = max(max_height, char_height)
            if i < len(text) - 1:
                width += int(char_width * spacing)
        return width, max_height, char_widths

    # 1. Find the largest font size that fits the box height
    min_font_size = 1
    max_font_size = box_height
    best_font_size = min_font_size
    while min_font_size <= max_font_size:
        mid_font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_path, mid_font_size)
        _, text_height, _ = get_text_size(sport_text, font, base_spacing_factor)
        if text_height <= box_height:
            best_font_size = mid_font_size
            min_font_size = mid_font_size + 1
        else:
            max_font_size = mid_font_size - 1

    font = ImageFont.truetype(font_path, best_font_size)
    _, text_height, char_widths = get_text_size(sport_text, font, 0)
    num_gaps = max(len(sport_text) - 1, 1)

    # 2. Calculate required total width (including spacing and stretching)
    total_char_width = sum(char_widths)
    # The minimum width is just the sum of the chars (no spacing)
    # The maximum width is box_width
    # We want: total_stretched_width + total_spacing = box_width
    # Let stretch_factor be applied to each char, and spacing be the space between each char

    # Solve for stretch_factor and spacing:
    # total_stretched_width = sum(char_widths) * stretch_factor
    # total_spacing = spacing * num_gaps
    # total_stretched_width + total_spacing = box_width
    # => (sum(char_widths) * stretch_factor) + (spacing * num_gaps) = box_width

    # We'll try to maximize stretch_factor up to a reasonable limit (e.g., 1.5), then use spacing for the rest
    max_stretch = 1.5
    stretch_factor = min(box_width / total_char_width, max_stretch)
    stretched_width = total_char_width * stretch_factor
    remaining_width = box_width - stretched_width
    spacing = max(remaining_width / num_gaps, 0)

    # If stretch_factor is less than max_stretch, spacing will be 0 or negative, so clamp to 0 and recalc stretch
    if spacing < 0:
        spacing = 0
        stretch_factor = box_width / total_char_width

    # 3. Center the text in the box
    total_width = stretched_width + spacing * num_gaps
    text_x = x1 + (box_width - total_width) // 2
    text_y = y1 + (box_height - text_height) // 2

    # 4. Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(sport_text):
                    char_img = Image.new("RGBA", (best_font_size * 2, best_font_size * 2), (0, 0, 0, 0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0, 0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    char_img = char_img.crop(char_bbox)
                    char_width = char_bbox[2] - char_bbox[0]
                    stretched_width = int(char_width * stretch_factor)
                    char_img = char_img.resize((stretched_width, char_img.height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_width
                    if i < len(sport_text) - 1:
                        cx += spacing

    # 5. Draw main text
    cx = text_x
    for i, char in enumerate(sport_text):
        char_img = Image.new("RGBA", (best_font_size * 2, best_font_size * 2), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=color)
        char_bbox = char_img.getbbox()
        char_img = char_img.crop(char_bbox)
        char_width = char_bbox[2] - char_bbox[0]
        stretched_width = int(char_width * stretch_factor)
        char_img = char_img.resize((stretched_width, char_img.height), Image.LANCZOS)
        image.paste(char_img, (int(cx), int(text_y)), char_img)
        cx += stretched_width
        if i < len(sport_text) - 1:
            cx += spacing

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

            # Render sport
            render_sport(
                image,
                coords.get('Sport', {}),
                row['Sport Specific'].upper(),  # Make sport text uppercase
                text_font_path
            )

            # Save image with "-1" at the end of the name
            output_path = os.path.join(asset_path, f"{row['Name']}-1.png")
            image.save(output_path)
            print(f"Created style: {output_path}")

if __name__ == "__main__":
    main()

