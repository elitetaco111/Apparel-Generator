#program to create NIL apparel images
#Created by Dave Nissly

#add printer file png of just logo with no blank
#jpg for website image png for printer image
#deduplication for printer images
#

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

def first_name_render(image, coords, first_name, font_path, lines_coords):
    """
    Renders the first name vertically stretched to fit the y-coords box, centered horizontally.
    - Reads y-coords from coords['y-coords'] (top and bottom).
    - Stretches the text to fill the vertical space.
    - Centers the text horizontally in the image.
    - Calculates and stores the width as name_width.
    - Calls draw_lines(name_width, coords) (to be implemented).
    - Uses spacing_factor for extra spacing between letters.
    - Implements border logic.
    """
    y1, y2 = coords.get('y-coords', [0, 0])
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))
    spacing_factor = float(coords.get('spacing_factor', 0))

    # Find the largest font size that fits the box height
    min_font_size = 1
    max_font_size = box_height
    best_font_size = min_font_size
    from PIL import ImageFont, ImageDraw, Image
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

    while min_font_size <= max_font_size:
        mid_font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_path, mid_font_size)
        _, text_height, _ = get_text_size(first_name, font, spacing_factor)
        if text_height <= box_height:
            best_font_size = mid_font_size
            min_font_size = mid_font_size + 1
        else:
            max_font_size = mid_font_size - 1

    font = ImageFont.truetype(font_path, best_font_size)
    ascent, descent = font.getmetrics()
    _, text_height, char_widths = get_text_size(first_name, font, spacing_factor)
    num_gaps = max(len(first_name) - 1, 0)

    # Calculate total width with spacing
    total_char_width = sum(char_widths)
    total_spacing = sum([int(char_widths[i] * spacing_factor) for i in range(num_gaps)])
    name_width = total_char_width + total_spacing

    # Use ascent + descent for true text height
    true_text_height = ascent + descent

    # Create a transparent image for the text (use true_text_height)
    text_img = Image.new("RGBA", (name_width, true_text_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)

    # Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width + 1):
            for dy in range(-border_width, border_width + 1):
                if dx == 0 and dy == 0:
                    continue
                cx = 0
                for i, char in enumerate(first_name):
                    # Draw at (cx + dx, ascent + dy - ascent) so baseline is correct
                    text_draw.text((cx + dx, dy), char, font=font, fill=border_color)
                    char_width = char_widths[i]
                    cx += char_width
                    if i < len(first_name) - 1:
                        cx += int(char_width * spacing_factor)

    # Draw main text
    cx = 0
    for i, char in enumerate(first_name):
        text_draw.text((cx, 0), char, font=font, fill=color)
        char_width = char_widths[i]
        cx += char_width
        if i < len(first_name) - 1:
            cx += int(char_width * spacing_factor)

    # Stretch vertically to fit the box
    stretched_img = text_img.resize((name_width, box_height), Image.LANCZOS)

    # Center horizontally on the image
    image_width = image.width
    center_x = (image_width - name_width) // 2
    image.paste(stretched_img, (center_x, y1), stretched_img)

    # Call draw_lines with name_width and coords
    draw_lines(image, name_width, lines_coords)

def draw_lines(image, name_width, coords):
    """
    Draws a horizontal rectangle (line) within the box defined by coords['coords'] (x1, y1, x2, y2),
    with a centered gap that is name_width + 80 pixels wide.
    The center of the gap is aligned with the center of the image.
    The rectangle uses the color from coords['color'].
    """
    x1, y1, x2, y2 = coords.get('coords', [0, 0, 0, 0])
    color = coords.get('color', '#ffffff')
    gap_width = name_width + 80

    image_center_x = image.width // 2
    gap_left = image_center_x - gap_width // 2
    gap_right = gap_left + gap_width

    # Clamp gap to box
    gap_left = max(gap_left, x1)
    gap_right = min(gap_right, x2)

    draw = ImageDraw.Draw(image)
    # Draw left rectangle (from x1 to gap_left)
    if gap_left > x1:
        draw.rectangle([x1, y1, gap_left, y2], fill=color)
    # Draw right rectangle (from gap_right to x2)
    if gap_right < x2:
        draw.rectangle([gap_right, y1, x2, y2], fill=color)

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

    # 2. Calculate required total width (including spacing factor)
    total_char_width = sum(char_widths)
    total_spacing = sum([int(char_widths[i] * base_spacing_factor) for i in range(num_gaps)])
    total_unstretched_width = total_char_width + total_spacing

    # Now calculate stretch factor so that (char widths + spacing) fit box_width
    max_stretch = 5
    stretch_factor = min(box_width / total_unstretched_width, max_stretch)
    stretched_total_width = total_unstretched_width * stretch_factor

    # 3. Center the text in the box
    text_x = x1 + (box_width - stretched_total_width) // 2
    text_y = y1

    # 4. Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(last_name):
                    char_width = char_widths[i]
                    stretched_char_width = int(char_width * stretch_factor)
                    char_img = Image.new("RGBA", (char_width * 2, best_font_size * 2), (0, 0, 0, 0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0, 0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    if char_bbox:
                        char_img = char_img.crop(char_bbox)
                    char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_char_width
                    if i < len(last_name) - 1:
                        spacing = int(char_widths[i] * base_spacing_factor * stretch_factor)
                        cx += spacing

    # 5. Draw main text
    cx = text_x
    for i, char in enumerate(last_name):
        char_width = char_widths[i]
        stretched_char_width = int(char_width * stretch_factor)
        char_img = Image.new("RGBA", (char_width * 2, best_font_size * 2), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=color)
        char_bbox = char_img.getbbox()
        if char_bbox:
            char_img = char_img.crop(char_bbox)
        char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
        image.paste(char_img, (int(cx), int(text_y)), char_img)
        cx += stretched_char_width
        if i < len(last_name) - 1:
            spacing = int(char_widths[i] * base_spacing_factor * stretch_factor)
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
    num_gaps = max(len(sport_text) - 1, 0)

    # 2. Calculate required total width (including min spacing factor)
    total_char_width = sum(char_widths)
    min_spacings = [int(char_widths[i] * base_spacing_factor) for i in range(num_gaps)]
    total_min_spacing = sum(min_spacings)
    total_unstretched_width = total_char_width + total_min_spacing

    # 3. Calculate stretch factor and check if we need to add extra spacing
    # 2.7 for 5 letters and below
    # 2.4 for 6 letters to 8
    max_stretch = 2.4
    stretch_factor = min(box_width / total_unstretched_width, max_stretch)
    stretched_total_width = total_unstretched_width * stretch_factor

    # If after max stretch, text still doesn't fill the box, add extra spacing
    if stretched_total_width < box_width and num_gaps > 0:
        extra_space = box_width - stretched_total_width
        extra_spacing_per_gap = extra_space // num_gaps
        extra_spacing_remainder = extra_space % num_gaps
        spacings = [
            int(min_spacings[i] * stretch_factor) + extra_spacing_per_gap + (1 if i < extra_spacing_remainder else 0)
            for i in range(num_gaps)
        ]
        stretched_char_widths = [int(w * stretch_factor) for w in char_widths]
        stretched_total_width = box_width  # Now it will fill the box exactly
    else:
        spacings = [int(min_spacings[i] * stretch_factor) for i in range(num_gaps)]
        stretched_char_widths = [int(w * stretch_factor) for w in char_widths]

    # 4. Center the text in the box
    text_x = x1 + (box_width - stretched_total_width) // 2
    text_y = y1

    # 5. Draw border if needed
    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(sport_text):
                    stretched_char_width = stretched_char_widths[i]
                    char_img = Image.new("RGBA", (char_widths[i] * 2, best_font_size * 2), (0, 0, 0, 0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0, 0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    if char_bbox:
                        char_img = char_img.crop(char_bbox)
                    char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_char_width
                    if i < num_gaps:
                        cx += spacings[i]

    # 6. Draw main text
    cx = text_x
    for i, char in enumerate(sport_text):
        stretched_char_width = stretched_char_widths[i]
        char_img = Image.new("RGBA", (char_widths[i] * 2, best_font_size * 2), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=color)
        char_bbox = char_img.getbbox()
        if char_bbox:
            char_img = char_img.crop(char_bbox)
        char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
        image.paste(char_img, (int(cx), int(text_y)), char_img)
        cx += stretched_char_width
        if i < num_gaps:
            cx += spacings[i]

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

            # Read names from CSV (always uppercase)
            first_name = (row.get('First Name') or '').strip().upper()
            last_name = (row.get('Last Name') or '').strip().upper()

            # Render number (skip if blank)
            jersey_value = (row.get('Jersey Characters') or '').strip()
            if jersey_value:
                number_render(image, coords.get('Number', {}), jersey_value, number_font_path)

            # Render first name (skip if blank)
            if first_name:
                first_name_render(
                    image,
                    coords.get('FirstName', {}),
                    first_name,
                    text_font_path,
                    coords.get("Lines", {})
                )

            # Render last name (skip if blank)
            if last_name:
                last_name_render(
                    image,
                    coords.get('LastName', {}),
                    last_name,
                    text_font_path
                )

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

