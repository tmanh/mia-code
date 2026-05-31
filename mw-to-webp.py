import argparse
import math
import os
from pathlib import Path


# Edit these defaults when you want to run the script without command-line args.
DEFAULT_FOLDER_PATH = "/Volumes/ME/MEO/Blogging/keepupcooking/main-keepupcooking/articles_keepupcooking/00-rhubarb tea"
DEFAULT_GENERAL_NAME = "rhubarb-tea-recipe"
DEFAULT_START_INDEX = 1
DEFAULT_QUALITY = 70
DEFAULT_RESIZE_PERCENTAGE = 70

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".heif", ".webp"}
COMPRESS_FOLDER_NAME = "compress"
IMAGE_TOOLS = None
NATSORTED = None


def load_natsorted():
    global NATSORTED
    if NATSORTED is not None:
        return NATSORTED

    try:
        from natsort import natsorted
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Missing sorting dependency. Install it in the Python environment you use:\n"
            "python3 -m pip install natsort"
        ) from error

    NATSORTED = natsorted
    return NATSORTED


def load_image_tools():
    global IMAGE_TOOLS
    if IMAGE_TOOLS is not None:
        return IMAGE_TOOLS

    try:
        from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError
        from pillow_heif import register_heif_opener
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Missing image dependency. Install them in the Python environment you use:\n"
            "python3 -m pip install Pillow pillow-heif"
        ) from error

    register_heif_opener()

    # This script is for trusted local files. Keep Pillow from rejecting large
    # camera images before they can be resized, while still blocking wildly
    # oversized files.
    Image.MAX_IMAGE_PIXELS = 500_000_000
    IMAGE_TOOLS = (Image, ImageFilter, ImageOps, UnidentifiedImageError)
    return IMAGE_TOOLS


def list_image_files(folder_path):
    folder = Path(folder_path)
    image_files = []

    for path in folder.iterdir():
        if path.name.startswith(".") or path.name.startswith("._"):
            continue
        if path.name == COMPRESS_FOLDER_NAME:
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            image_files.append(path)

    return load_natsorted()(image_files, key=lambda item: item.name.lower())


def build_rename_plan(image_files, general_name, start_index):
    plan = []

    for index, source_path in enumerate(image_files, start=start_index):
        target_name = f"{general_name}-{index}{source_path.suffix.lower()}"
        target_path = source_path.with_name(target_name)
        plan.append((source_path, target_path))

    return plan


def validate_rename_plan(plan):
    target_paths = [target for _, target in plan]

    if len(target_paths) != len(set(target_paths)):
        raise ValueError("Rename plan contains duplicate target filenames.")

    source_paths = {source for source, _ in plan}
    blocking_paths = [
        target for source, target in plan
        if target.exists() and target != source and target not in source_paths
    ]

    if blocking_paths:
        blocking_names = "\n".join(f"- {path.name}" for path in blocking_paths)
        raise FileExistsError(
            "Rename stopped because these target files already exist:\n"
            f"{blocking_names}\nNo files were changed."
        )


def rename_files_safely(plan, dry_run=False):
    validate_rename_plan(plan)

    changes = [(source, target) for source, target in plan if source != target]
    if not changes:
        print("Rename: all files already use the requested names.")
        return [target for _, target in plan]

    print("Rename plan:")
    for source, target in changes:
        print(f"  {source.name} -> {target.name}")

    if dry_run:
        print("Dry run: rename skipped.")
        return [target for _, target in plan]

    temp_plan = []
    for source, _ in changes:
        temp_path = source.with_name(f".rename-tmp-{os.getpid()}-{source.name}")
        if temp_path.exists():
            raise FileExistsError(f"Temporary file already exists: {temp_path}")
        temp_plan.append((source, temp_path))

    renamed_to_temp = []
    try:
        for source, temp_path in temp_plan:
            source.rename(temp_path)
            renamed_to_temp.append((source, temp_path))

        temp_by_source = dict(temp_plan)
        for source, target in changes:
            if source == target:
                print(f"Skipping {source.name}: already correctly named.")
                continue
            temp_by_source[source].rename(target)
    except Exception:
        # Best-effort rollback so a failed rename does not leave files stranded
        # behind temporary names.
        for source, temp_path in reversed(renamed_to_temp):
            if temp_path.exists() and not source.exists():
                temp_path.rename(source)
        raise

    print(f"Renamed {len(changes)} file(s) safely.")
    return [target for _, target in plan]


def split_alpha(img):
    if img.mode in ("RGBA", "LA"):
        return img.convert("RGBA").split()[-1]
    if img.mode == "P" and "transparency" in img.info:
        return img.convert("RGBA").split()[-1]
    return None


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def median(values):
    if not values:
        return None

    sorted_values = sorted(values)
    midpoint = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[midpoint]
    return (sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2.0


def get_white_balance_gains(rgb_img):
    sample = rgb_img.copy()
    sample.thumbnail((512, 512))

    red_values = []
    green_values = []
    blue_values = []

    for red, green, blue in sample.getdata():
        brightness = (red + green + blue) / 3.0
        if brightness < 45 or brightness > 238:
            continue

        channel_spread = max(red, green, blue) - min(red, green, blue)
        if channel_spread / max(brightness, 1.0) > 0.22:
            continue

        red_values.append(red)
        green_values.append(green)
        blue_values.append(blue)

    if len(red_values) < 300:
        return 1.0, 1.0, 1.0

    red_median = median(red_values)
    green_median = median(green_values)
    blue_median = median(blue_values)
    gray_median = (red_median + green_median + blue_median) / 3.0

    if min(red_median, green_median, blue_median) <= 0:
        return 1.0, 1.0, 1.0

    return (
        clamp(gray_median / red_median, 0.88, 1.14),
        clamp(gray_median / green_median, 0.90, 1.10),
        clamp(gray_median / blue_median, 0.88, 1.14),
    )


def apply_white_balance(rgb_img):
    Image, _, _, _ = load_image_tools()
    red_gain, green_gain, blue_gain = get_white_balance_gains(rgb_img)
    red_channel, green_channel, blue_channel = rgb_img.split()

    balanced = Image.merge(
        "RGB",
        (
            red_channel.point(lambda value: clamp(int(value * red_gain), 0, 255)),
            green_channel.point(lambda value: clamp(int(value * green_gain), 0, 255)),
            blue_channel.point(lambda value: clamp(int(value * blue_gain), 0, 255)),
        ),
    )

    return Image.blend(rgb_img, balanced, 0.65)


def get_luminance_median(y_channel):
    sample = y_channel.copy()
    sample.thumbnail((512, 512))
    values = [value for value in sample.getdata() if 8 < value < 248]
    return median(values) or 128


def build_luminance_curve(y_channel):
    y_median = get_luminance_median(y_channel)
    target_median = 142
    gamma = math.log(target_median / 255.0) / math.log(clamp(y_median, 20, 235) / 255.0)
    gamma = clamp(gamma, 0.62, 1.18)

    curve = []
    for value in range(256):
        normalized = value / 255.0
        exposed = int(255 * (normalized ** gamma))

        # Lift shadows and midtones, but fade the adjustment out in highlights
        # so bright counters/mats do not become chalky or clipped.
        protect_highlights = 1.0 - (normalized ** 2.2)
        lifted_shadow = value + 18 * ((1.0 - normalized) ** 2.0)
        target = exposed * 0.78 + lifted_shadow * 0.22
        adjusted = value + (target - value) * protect_highlights
        curve.append(clamp(int(adjusted), 0, 255))

    return curve


def enhance_image(img):
    Image, ImageFilter, _, _ = load_image_tools()
    alpha = split_alpha(img)

    rgb_img = apply_white_balance(img.convert("RGB"))
    y_channel, cb_channel, cr_channel = rgb_img.convert("YCbCr").split()

    y_channel = y_channel.point(build_luminance_curve(y_channel))
    y_channel = y_channel.filter(ImageFilter.UnsharpMask(radius=1.1, percent=16, threshold=10))

    enhanced = Image.merge("YCbCr", (y_channel, cb_channel, cr_channel)).convert("RGB")

    if alpha is not None:
        enhanced = enhanced.convert("RGBA")
        enhanced.putalpha(alpha)

    return enhanced


def convert_to_webp(
    image_path,
    out_path,
    quality,
    resize_percentage,
):
    Image, _, ImageOps, UnidentifiedImageError = load_image_tools()

    try:
        with Image.open(image_path) as img:
            icc_profile = img.info.get("icc_profile")
            img = ImageOps.exif_transpose(img)

            img = enhance_image(img)

            width, height = img.size
            resized_size = (
                max(1, int(width * resize_percentage / 100.0)),
                max(1, int(height * resize_percentage / 100.0)),
            )
            img = img.resize(resized_size, resample=Image.Resampling.LANCZOS)

            try:
                img.save(out_path, "WEBP", quality=quality, method=6, icc_profile=icc_profile)
            except OSError:
                img.save(out_path, "WEBP", quality=quality, method=6)
            return True
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        print(f"Skipping {image_path.name}: {error}")
        return False


def convert_all_images(
    image_files,
    quality,
    resize_percentage,
    dry_run=False,
):
    if not image_files:
        print("Convert: no image files found.")
        return

    out_dir = image_files[0].parent / COMPRESS_FOLDER_NAME
    if not dry_run:
        out_dir.mkdir(exist_ok=True)

    converted = 0
    skipped = 0

    for image_path in image_files:
        out_path = out_dir / f"{image_path.stem}.webp"

        if out_path.exists():
            print(f"Skipping existing output: {out_path.name}")
            skipped += 1
            continue

        print(f"Converting: {image_path.name} -> {COMPRESS_FOLDER_NAME}/{out_path.name}")
        if dry_run:
            converted += 1
            continue
        if convert_to_webp(
            image_path,
            out_path,
            quality,
            resize_percentage,
        ):
            converted += 1
        else:
            skipped += 1

    if dry_run:
        print("Dry run: conversion skipped.")
    print(f"Conversion summary: {converted} new, {skipped} skipped.")


def run_pipeline(
    folder_path,
    general_name,
    start_index,
    quality,
    resize_percentage,
    dry_run=False,
):
    folder = Path(folder_path).expanduser()
    if not folder.exists():
        raise FileNotFoundError(f"The folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"This path is not a folder: {folder}")

    image_files = list_image_files(folder)
    if not image_files:
        print(f"No images found in {folder}")
        return

    if not dry_run:
        load_image_tools()

    plan = build_rename_plan(image_files, general_name, start_index)
    renamed_files = rename_files_safely(plan, dry_run=dry_run)
    convert_all_images(
        renamed_files,
        quality,
        resize_percentage,
        dry_run=dry_run,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Safely rename images, resize them, and convert them to WebP."
    )
    parser.add_argument("--folder", default=DEFAULT_FOLDER_PATH, help="Folder containing images.")
    parser.add_argument("--name", default=DEFAULT_GENERAL_NAME, help="Base name for renamed images.")
    parser.add_argument("--start", type=int, default=DEFAULT_START_INDEX, help="Starting index.")
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY, help="WebP quality, 1-100.")
    parser.add_argument(
        "--resize",
        type=int,
        default=DEFAULT_RESIZE_PERCENTAGE,
        help="Resize percentage, for example 70.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview work without changing files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        folder_path=args.folder,
        general_name=args.name,
        start_index=args.start,
        quality=args.quality,
        resize_percentage=args.resize,
        dry_run=args.dry_run,
    )
