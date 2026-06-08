import argparse
import shutil
import subprocess
from pathlib import Path


DEFAULT_FOLDER_PATH = "/Users/thupham/Downloads/test tool"
DEFAULT_OUTPUT_FOLDER = "adjuster-ready"
DEFAULT_JPEG_QUALITY = 96

IMAGE_EXTS = {".avif", ".bmp", ".gif", ".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
HEIC_EXTS = {".heic", ".heif"}
IMAGE_TOOLS = None
SIPS_PATH = shutil.which("sips")


def load_image_tools():
    global IMAGE_TOOLS
    if IMAGE_TOOLS is not None:
        return IMAGE_TOOLS

    try:
        from PIL import Image, ImageOps, UnidentifiedImageError
        from pillow_heif import register_heif_opener
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Missing image dependency. Install them in the Python environment you use:\n"
            "python3 -m pip install Pillow pillow-heif"
        ) from error

    register_heif_opener()
    Image.MAX_IMAGE_PIXELS = 500_000_000
    IMAGE_TOOLS = (Image, ImageOps, UnidentifiedImageError)
    return IMAGE_TOOLS


def list_images(folder):
    folder = Path(folder).expanduser()
    if not folder.exists():
        raise FileNotFoundError(f"The folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"This path is not a folder: {folder}")

    images = []
    for path in folder.iterdir():
        if path.name.startswith(".") or path.name.startswith("._"):
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            images.append(path)

    return sorted(images, key=lambda item: item.name.lower())


def unique_path(path):
    if not path.exists():
        return path

    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def convert_heic_with_pillow(source_path, target_path, quality):
    Image, ImageOps, UnidentifiedImageError = load_image_tools()

    try:
        with Image.open(source_path) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.save(target_path, "JPEG", quality=quality, optimize=True)
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        return str(error)

    return None


def convert_heic_with_sips(source_path, target_path):
    if not SIPS_PATH:
        return "macOS sips converter is not available."

    result = subprocess.run(
        [
            SIPS_PATH,
            "-s",
            "format",
            "jpeg",
            str(source_path),
            "--out",
            str(target_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0 or not target_path.exists():
        message = (result.stderr or result.stdout or "unknown sips error").strip()
        return message

    return None


def convert_heic_to_jpeg(source_path, output_dir, quality):
    target_path = unique_path(output_dir / f"{source_path.stem}.jpg")

    pillow_error = convert_heic_with_pillow(source_path, target_path, quality)
    if pillow_error is None:
        print(f"  Converted with Pillow: {target_path.name}")
        return target_path

    if target_path.exists():
        target_path.unlink()

    sips_error = convert_heic_with_sips(source_path, target_path)
    if sips_error is None:
        print(f"  Converted with sips: {target_path.name}")
        return target_path

    print(
        f"Skipping {source_path.name}: Pillow failed ({pillow_error}); "
        f"sips failed ({sips_error})"
    )
    return None


def copy_image(source_path, output_dir):
    target_path = unique_path(output_dir / source_path.name)
    shutil.copy2(source_path, target_path)
    return target_path


def prepare_photos(folder_path, output_folder, quality, dry_run=False):
    source_dir = Path(folder_path).expanduser()
    output_dir = Path(output_folder).expanduser()
    if not output_dir.is_absolute():
        output_dir = source_dir / output_dir

    images = list_images(source_dir)
    if not images:
        print(f"No images found in {source_dir}")
        return

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    copied = 0
    skipped = 0

    for source_path in images:
        if source_path.suffix.lower() in HEIC_EXTS:
            target_name = f"{source_path.stem}.jpg"
            print(f"Converting HEIC: {source_path.name} -> {output_dir.name}/{target_name}")
            if dry_run:
                converted += 1
                continue
            if convert_heic_to_jpeg(source_path, output_dir, quality):
                converted += 1
            else:
                skipped += 1
            continue

        print(f"Copying: {source_path.name} -> {output_dir.name}/{source_path.name}")
        if dry_run:
            copied += 1
            continue
        copy_image(source_path, output_dir)
        copied += 1

    if dry_run:
        print("Dry run: no files were written.")
    print(f"Prepared {converted + copied} photo(s): {converted} converted, {copied} copied, {skipped} skipped.")
    print(f"Upload photos from: {output_dir}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare browser-friendly photos for Batch Photo Adjuster by converting HEIC/HEIF to JPEG."
    )
    parser.add_argument("--folder", default=DEFAULT_FOLDER_PATH, help="Folder containing source photos.")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FOLDER,
        help="Output folder. Relative paths are created inside the source folder.",
    )
    parser.add_argument("--quality", type=int, default=DEFAULT_JPEG_QUALITY, help="JPEG quality for converted HEIC files.")
    parser.add_argument("--dry-run", action="store_true", help="Preview work without writing files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    prepare_photos(
        folder_path=args.folder,
        output_folder=args.output,
        quality=args.quality,
        dry_run=args.dry_run,
    )
