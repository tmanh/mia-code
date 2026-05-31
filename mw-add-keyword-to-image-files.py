from pathlib import Path

# Folder containing the photos
folder = Path(r'/Volumes/ME/MEO/Blogging/miawanders/articles_miawanders/00-europe-20 best castles and palaces in europe')

# Text to add
text_to_add = "20-Best-Castles-Palace-in-Europe"

# Image extensions to process
image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}

for file_path in folder.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in image_exts:
        new_name = text_to_add + file_path.name
        new_path = file_path.with_name(new_name)

        # Avoid overwriting existing files
        if new_path.exists():
            print(f"Skipped (already exists): {new_path.name}")
            continue

        file_path.rename(new_path)
        print(f"Renamed: {file_path.name} -> {new_path.name}")