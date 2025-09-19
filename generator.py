#program to create NIL apparel images
#Created by Dave Nissly

import csv
import os
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from tkinter import Tk, filedialog

#TODO
#space between name letters (spacing factor logic)
#shift number left

BIN_DIR = os.path.join(os.getcwd(), 'bin')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
WEB_DIR = os.path.join(OUTPUT_DIR, 'web-images')        # main images
PRINT_DIR = os.path.join(OUTPUT_DIR, 'printer-images')  # print files

# percent of the line bar width used as padding on EACH side of the name gap
GAP_PADDING_PCT = 0.08  # 8% per side

def number_render(image, coords, number, font_path):
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = coords.get('coords', [0,0,0,0])
    box_width = x2 - x1
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))

    font_size = box_height
    font = ImageFont.truetype(font_path, font_size)
    bbox = font.getbbox(number)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    while text_height > box_height and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(number)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    text_x = x1 + (box_width - text_width) // 2
    text_y = y1 + (box_height - text_height) // 2

    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((text_x+dx, text_y+dy), number, font=font, fill=border_color)

    draw.text((text_x, text_y), number, font=font, fill=color)

def first_name_render(image, coords, first_name, font_path, lines_coords):
    y1, y2 = coords.get('y-coords', [0, 0])
    box_height = y2 - y1
    color = coords.get('color', '#ffffff')
    border = coords.get('border', 'False') == 'True'
    border_color = coords.get('border_color', '#000000')
    border_width = int(coords.get('border_width', 0))
    spacing_factor = float(coords.get('spacing_factor', 0))

    min_font_size = 1
    max_font_size = max(1, box_height)
    best_font_size = min_font_size

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
    _, _, char_widths = get_text_size(first_name, font, spacing_factor)
    num_gaps = max(len(first_name) - 1, 0)
    total_char_width = sum(char_widths)
    total_spacing = sum(int(char_widths[i] * spacing_factor) for i in range(num_gaps))
    name_width = total_char_width + total_spacing
    true_text_height = ascent + descent

    text_img = Image.new("RGBA", (name_width, true_text_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)

    if border and border_width > 0:
        for dx in range(-border_width, border_width + 1):
            for dy in range(-border_width, border_width + 1):
                if dx == 0 and dy == 0:
                    continue
                cx = 0
                for i, char in enumerate(first_name):
                    text_draw.text((cx + dx, dy), char, font=font, fill=border_color)
                    char_width = char_widths[i]
                    cx += char_width
                    if i < len(first_name) - 1:
                        cx += int(char_width * spacing_factor)

    cx = 0
    for i, char in enumerate(first_name):
        text_draw.text((cx, 0), char, font=font, fill=color)
        char_width = char_widths[i]
        cx += char_width
        if i < len(first_name) - 1:
            cx += int(char_width * spacing_factor)

    stretched_img = text_img.resize((name_width, box_height), Image.LANCZOS)
    image_width = image.width
    center_x = (image_width - name_width) // 2
    image.paste(stretched_img, (center_x, y1), stretched_img)
    draw_lines(image, name_width, lines_coords)

def draw_lines(image, name_width, coords):
    x1, y1, x2, y2 = coords.get('coords', [0, 0, 0, 0])
    color = coords.get('color', '#ffffff')

    # Compute gap as: name width + padding on both sides, where padding is a
    # global percent of the line bar width (consistent across all designs).
    bar_width = max(0, x2 - x1)
    side_pad = int(bar_width * GAP_PADDING_PCT)
    gap_width = min(bar_width, max(0, name_width + 2 * side_pad))

    # Keep the gap centered under the centered first name
    image_center_x = image.width // 2
    gap_left = max(x1, image_center_x - gap_width // 2)
    gap_right = min(x2, gap_left + gap_width)

    draw = ImageDraw.Draw(image)
    if gap_left > x1:
        draw.rectangle([x1, y1, gap_left, y2], fill=color)
    if gap_right < x2:
        draw.rectangle([gap_right, y1, x2, y2], fill=color)

def last_name_render(image, coords, last_name, font_path):
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

    min_font_size = 1
    max_font_size = max(1, box_height)
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
    _, _, char_widths = get_text_size(last_name, font, 0)
    num_gaps = max(len(last_name) - 1, 0)
    total_char_width = sum(char_widths)
    total_spacing = sum(int(char_widths[i] * base_spacing_factor) for i in range(num_gaps))
    total_unstretched_width = total_char_width + total_spacing
    max_stretch = 5
    stretch_factor = min(box_width / total_unstretched_width, max_stretch)
    stretched_total_width = total_unstretched_width * stretch_factor
    text_x = x1 + (box_width - stretched_total_width) // 2
    text_y = y1

    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(last_name):
                    char_width = char_widths[i]
                    stretched_char_width = int(char_width * stretch_factor)
                    char_img = Image.new("RGBA", (char_width * 2, best_font_size * 2), (0,0,0,0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0,0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    if char_bbox:
                        char_img = char_img.crop(char_bbox)
                    char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_char_width
                    if i < len(last_name) - 1:
                        spacing = int(char_widths[i] * base_spacing_factor * stretch_factor)
                        cx += spacing

    cx = text_x
    for i, char in enumerate(last_name):
        char_width = char_widths[i]
        stretched_char_width = int(char_width * stretch_factor)
        char_img = Image.new("RGBA", (char_width * 2, best_font_size * 2), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0,0), char, font=font, fill=color)
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

    min_font_size = 1
    max_font_size = max(1, box_height)
    best_font_size = min_font_size
    while min_font_size <= max_font_size:
        mid_font_size = (min_font_size + max_font_size)//2
        font = ImageFont.truetype(font_path, mid_font_size)
        _, text_height, _ = get_text_size(sport_text, font, base_spacing_factor)
        if text_height <= box_height:
            best_font_size = mid_font_size
            min_font_size = mid_font_size + 1
        else:
            max_font_size = mid_font_size - 1

    font = ImageFont.truetype(font_path, best_font_size)
    _, _, char_widths = get_text_size(sport_text, font, 0)
    num_gaps = max(len(sport_text) - 1, 0)
    total_char_width = sum(char_widths)
    min_spacings = [int(char_widths[i] * base_spacing_factor) for i in range(num_gaps)]
    total_min_spacing = sum(min_spacings)
    total_unstretched_width = total_char_width + total_min_spacing
    max_stretch = 2.4
    stretch_factor = min(box_width / total_unstretched_width, max_stretch)
    stretched_total_width = total_unstretched_width * stretch_factor

    if stretched_total_width < box_width and num_gaps > 0:
        extra_space = box_width - stretched_total_width
        extra_spacing_per_gap = extra_space // num_gaps
        extra_spacing_remainder = extra_space % num_gaps
        spacings = [
            int(min_spacings[i] * stretch_factor) + extra_spacing_per_gap + (1 if i < extra_spacing_remainder else 0)
            for i in range(num_gaps)
        ]
        stretched_char_widths = [int(w * stretch_factor) for w in char_widths]
        stretched_total_width = box_width
    else:
        spacings = [int(min_spacings[i] * stretch_factor) for i in range(num_gaps)]
        stretched_char_widths = [int(w * stretch_factor) for w in char_widths]

    text_x = x1 + (box_width - stretched_total_width) // 2
    text_y = y1

    if border and border_width > 0:
        for dx in range(-border_width, border_width+1):
            for dy in range(-border_width, border_width+1):
                if dx == 0 and dy == 0:
                    continue
                cx = text_x
                for i, char in enumerate(sport_text):
                    stretched_char_width = stretched_char_widths[i]
                    char_img = Image.new("RGBA", (char_widths[i]*2, best_font_size*2), (0,0,0,0))
                    char_draw = ImageDraw.Draw(char_img)
                    char_draw.text((0,0), char, font=font, fill=border_color)
                    char_bbox = char_img.getbbox()
                    if char_bbox:
                        char_img = char_img.crop(char_bbox)
                    char_img = char_img.resize((stretched_char_width, box_height), Image.LANCZOS)
                    image.paste(char_img, (int(cx+dx), int(text_y+dy)), char_img)
                    cx += stretched_char_width
                    if i < num_gaps:
                        cx += spacings[i]

    cx = text_x
    for i, char in enumerate(sport_text):
        stretched_char_width = stretched_char_widths[i]
        char_img = Image.new("RGBA", (char_widths[i]*2, best_font_size*2), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0,0), char, font=font, fill=color)
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
    class_parts = class_field.split(": ")
    class_text = class_parts[2] if len(class_parts) > 2 else class_parts[-1]
    return f"{team}-{color}-{art_type}-{class_text}"

def build_image_from_assets(row, asset_path):
    blank_img_path = os.path.join(asset_path, 'blank.png')
    coords_path = os.path.join(asset_path, 'coords.json')
    text_font_path = os.path.join(asset_path, 'text.otf')
    number_font_path = os.path.join(asset_path, 'number.ttf')

    try:
        image = Image.open(blank_img_path).convert('RGBA')
    except FileNotFoundError:
        return None, "blank.png missing"
    try:
        with open(coords_path, 'r', encoding='utf-8') as f:
            coords = json.load(f)
    except FileNotFoundError:
        return None, "coords.json missing"

    first_name = (row.get('First Name') or '').strip().upper()
    last_name = (row.get('Last Name') or '').strip().upper()
    # Use Jersey Number, fall back to Jersey Characters
    jersey_value = (row.get('Jersey Number') or row.get('Jersey Characters') or '').strip()

    if jersey_value:
        number_render(image, coords.get('Number', {}), jersey_value, number_font_path)
    if first_name:
        first_name_render(image, coords.get('FirstName', {}), first_name, text_font_path, coords.get("Lines", {}))
    if last_name:
        last_name_render(image, coords.get('LastName', {}), last_name, text_font_path)
    render_sport(image, coords.get('Sport', {}), (row.get('Sport Specific') or '').upper(), text_font_path)

    return image, None

def sanitize_filename(s):
    return "".join(c for c in s.replace(" ", "_") if c not in '/\\').strip("_")

def combo_key(art_type, player_name):
    return (art_type.strip().lower(), player_name.strip().lower())

def choose_input_csv():
    try:
        root = Tk()
        root.withdraw()
        root.update()
        path = filedialog.askopenfilename(
            title="Select input CSV",
            initialdir=os.getcwd(),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        root.destroy()
        return path or ""
    except Exception as e:
        print(f"File dialog error: {e}")
        return ""

def main():
    # Reset output directory each run
    if os.path.isdir(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
            print(f"Cleared output directory: {OUTPUT_DIR}")
        except Exception as e:
            print(f"ERROR: Failed to clear output directory {OUTPUT_DIR}: {e}")
            return
    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(PRINT_DIR, exist_ok=True)

    if not os.path.isdir(BIN_DIR):
        print(f"ERROR: bin directory not found at {BIN_DIR}")
        return

    input_csv = choose_input_csv()
    if not input_csv:
        print("No input file selected. Exiting.")
        return

    # Runtime-only registry of created combos
    processed_art_player = set()
    combos_created = []

    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_id = (row.get('Name') or '').strip()  # used only for per-row output filename
            art_type_val = (row.get('Art Type') or '').strip()
            player_name = (row.get('Player Name') or '').strip()

            # Normal per-row image
            asset_folder = get_asset_folder(row)
            asset_path = os.path.join(BIN_DIR, asset_folder)
            if os.path.isdir(asset_path):
                image, err = build_image_from_assets(row, asset_path)
                if image:
                    # Main image filename: <Name>-1.png (no JPEG conversion)
                    product_id_s = (row.get('Name') or '').strip()
                    main_base = sanitize_filename(f"{product_id_s}-1")
                    output_path = os.path.join(WEB_DIR, f"{main_base}.png")
                    image.save(output_path)
                    print(f"Created style: {output_path}")
                else:
                    print(f"Skipping {asset_folder}: {err}")
            else:
                print(f"Skipping: asset folder missing {asset_path}")

            # One-per (Art Type + Player Name) print file, runtime only
            if art_type_val and player_name:
                key = combo_key(art_type_val, player_name)
                if key not in processed_art_player:
                    art_only_path = os.path.join(BIN_DIR, art_type_val)
                    # Print file filename: <Description>.png
                    desc = (row.get('Description') or '').strip()
                    extra_base = sanitize_filename(desc)
                    extra_out = os.path.join(PRINT_DIR, f"{extra_base}.png")

                    if os.path.isdir(art_only_path):
                        extra_image, err2 = build_image_from_assets(row, art_only_path)
                        if extra_image:
                            extra_image.save(extra_out)
                            print(f"Created combo: {extra_out}")
                            processed_art_player.add(key)
                            combos_created.append({"art_type": art_type_val, "player_name": player_name, "path": extra_out})
                        else:
                            print(f"Combo skip ({art_type_val}, {player_name}): {err2}")
                            processed_art_player.add(key)
                    else:
                        print(f"Combo assets missing for {art_type_val} at {art_only_path}")
                        processed_art_player.add(key)

    # Optional summary
    print(f"\nCombo summary (this run only): {len(combos_created)} created")
    for c in combos_created:
        print(f"- {c['art_type']} - {c['player_name']} -> {c['path']}")

if __name__ == "__main__":
    main()