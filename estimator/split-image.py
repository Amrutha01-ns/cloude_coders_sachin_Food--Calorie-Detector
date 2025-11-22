from PIL import Image
import os
import zipfile

# Path to your grid image (update this to your local path)
img = Image.open("A_digital_photograph_compilation_of_50_food_items_.png")

# Dimensions
w, h = img.size
cols, rows = 5, 10
tile_w, tile_h = w // cols, h // rows

# Output folder
out_dir = "food_items"
os.makedirs(out_dir, exist_ok=True)

# Crop into 50 individual images
index = 1
for r in range(rows):
    for c in range(cols):
        left = c * tile_w
        top = r * tile_h
        right = left + tile_w
        bottom = top + tile_h
        tile = img.crop((left, top, right, bottom))

        path = f"{out_dir}/food_item_{index}.png"
        tile.save(path)
        index += 1

print("Done! 50 images saved in the 'food_items' folder.")
