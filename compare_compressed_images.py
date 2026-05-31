import argparse
import csv
import math
from pathlib import Path


DEFAULT_OLD_DIR = "/Volumes/ME/MEO/Blogging/keepupcooking/canon rp/progressing/tokbokki tu com nguoi/old-compress"
DEFAULT_NEW_DIR = "/Volumes/ME/MEO/Blogging/keepupcooking/canon rp/progressing/tokbokki tu com nguoi/compress"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".gif"}
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
        from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Missing image dependency. Install it in the Python environment you use:\n"
            "python3 -m pip install Pillow"
        ) from error

    IMAGE_TOOLS = (Image, ImageChops, ImageDraw, ImageOps, ImageStat)
    return IMAGE_TOOLS


def list_images(folder):
    folder = Path(folder).expanduser()
    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    images = {}
    for path in folder.iterdir():
        if path.name.startswith(".") or path.name.startswith("._"):
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            images[path.name] = path

    return images


def fit_image(img, size):
    Image, _, _, ImageOps, _ = load_image_tools()
    fitted = ImageOps.contain(img.convert("RGB"), size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    left = (size[0] - fitted.width) // 2
    top = (size[1] - fitted.height) // 2
    canvas.paste(fitted, (left, top))
    return canvas


def image_metrics(old_path, new_path):
    Image, ImageChops, _, _, ImageStat = load_image_tools()
    with Image.open(old_path) as old_img, Image.open(new_path) as new_img:
        old_rgb = old_img.convert("RGB")
        new_rgb = new_img.convert("RGB")

        if old_rgb.size != new_rgb.size:
            new_rgb = new_rgb.resize(old_rgb.size, Image.Resampling.LANCZOS)

        old_y = old_rgb.convert("YCbCr").split()[0]
        new_y = new_rgb.convert("YCbCr").split()[0]
        old_stat = ImageStat.Stat(old_rgb)
        new_stat = ImageStat.Stat(new_rgb)
        old_y_stat = ImageStat.Stat(old_y)
        new_y_stat = ImageStat.Stat(new_y)

        diff = ImageChops.difference(old_rgb, new_rgb)
        diff_stat = ImageStat.Stat(diff)
        mae = sum(diff_stat.mean) / 3.0
        rmse = math.sqrt(sum(value ** 2 for value in diff_stat.rms) / 3.0)

        return {
            "old_size": f"{old_rgb.width}x{old_rgb.height}",
            "new_size": f"{new_rgb.width}x{new_rgb.height}",
            "old_mean_luma": round(old_y_stat.mean[0], 2),
            "new_mean_luma": round(new_y_stat.mean[0], 2),
            "luma_delta": round(new_y_stat.mean[0] - old_y_stat.mean[0], 2),
            "old_luma_stddev": round(old_y_stat.stddev[0], 2),
            "new_luma_stddev": round(new_y_stat.stddev[0], 2),
            "luma_stddev_delta": round(new_y_stat.stddev[0] - old_y_stat.stddev[0], 2),
            "old_rgb_mean": tuple(round(value, 2) for value in old_stat.mean),
            "new_rgb_mean": tuple(round(value, 2) for value in new_stat.mean),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
        }


def make_pair_preview(old_path, new_path, output_path, label, thumb_size):
    Image, _, ImageDraw, _, _ = load_image_tools()
    label_height = 34
    gutter = 12
    width = thumb_size[0] * 2 + gutter
    height = thumb_size[1] + label_height

    with Image.open(old_path) as old_img, Image.open(new_path) as new_img:
        old_thumb = fit_image(old_img, thumb_size)
        new_thumb = fit_image(new_img, thumb_size)

    preview = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(preview)
    draw.text((8, 8), f"{label} | OLD", fill=(30, 30, 30))
    draw.text((thumb_size[0] + gutter + 8, 8), "NEW", fill=(30, 30, 30))
    preview.paste(old_thumb, (0, label_height))
    preview.paste(new_thumb, (thumb_size[0] + gutter, label_height))
    preview.save(output_path, quality=92)


def make_contact_sheet(pair_previews, output_path):
    if not pair_previews:
        return

    Image, _, _, _, _ = load_image_tools()
    previews = [Image.open(path).convert("RGB") for path in pair_previews]
    width = max(img.width for img in previews)
    height = sum(img.height for img in previews)
    sheet = Image.new("RGB", (width, height), "white")

    top = 0
    for img in previews:
        sheet.paste(img, (0, top))
        top += img.height

    sheet.save(output_path, quality=92)

    for img in previews:
        img.close()


def write_csv(rows, output_path):
    fieldnames = [
        "filename",
        "old_size",
        "new_size",
        "old_mean_luma",
        "new_mean_luma",
        "luma_delta",
        "old_luma_stddev",
        "new_luma_stddev",
        "luma_stddev_delta",
        "old_rgb_mean",
        "new_rgb_mean",
        "mae",
        "rmse",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, old_only, new_only, output_path):
    lines = [
        "# Compressed Image Comparison",
        "",
        "| Filename | Luma Delta | Contrast Delta | MAE | RMSE | Old RGB Mean | New RGB Mean |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    for row in rows:
        lines.append(
            f"| {row['filename']} | {row['luma_delta']} | {row['luma_stddev_delta']} | "
            f"{row['mae']} | {row['rmse']} | {row['old_rgb_mean']} | {row['new_rgb_mean']} |"
        )

    if old_only:
        lines.extend(["", "## Only In Old Folder", ""])
        lines.extend(f"- {name}" for name in old_only)

    if new_only:
        lines.extend(["", "## Only In New Folder", ""])
        lines.extend(f"- {name}" for name in new_only)

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compare_folders(old_dir, new_dir, output_dir, thumb_width):
    old_images = list_images(old_dir)
    new_images = list_images(new_dir)

    natsorted = load_natsorted()
    common_names = natsorted(set(old_images) & set(new_images))
    old_only = natsorted(set(old_images) - set(new_images))
    new_only = natsorted(set(new_images) - set(old_images))

    output_dir = Path(output_dir).expanduser()
    previews_dir = output_dir / "pair-previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    pair_previews = []
    thumb_size = (thumb_width, int(thumb_width * 2 / 3))

    for filename in common_names:
        old_path = old_images[filename]
        new_path = new_images[filename]
        row = {"filename": filename}
        row.update(image_metrics(old_path, new_path))
        rows.append(row)

        preview_path = previews_dir / f"{Path(filename).stem}_compare.jpg"
        make_pair_preview(old_path, new_path, preview_path, filename, thumb_size)
        pair_previews.append(preview_path)

    write_csv(rows, output_dir / "comparison_metrics.csv")
    write_markdown(rows, old_only, new_only, output_dir / "comparison_report.md")
    make_contact_sheet(pair_previews, output_dir / "comparison_contact_sheet.jpg")

    print(f"Compared {len(common_names)} matching image(s).")
    print(f"Report: {output_dir / 'comparison_report.md'}")
    print(f"Metrics: {output_dir / 'comparison_metrics.csv'}")
    print(f"Contact sheet: {output_dir / 'comparison_contact_sheet.jpg'}")
    if old_only:
        print(f"Only in old folder: {len(old_only)}")
    if new_only:
        print(f"Only in new folder: {len(new_only)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Compare old and new compressed image folders.")
    parser.add_argument("--old", default=DEFAULT_OLD_DIR, help="Folder with old compressed images.")
    parser.add_argument("--new", default=DEFAULT_NEW_DIR, help="Folder with new compressed images.")
    parser.add_argument(
        "--output",
        default="image-comparison",
        help="Output folder for reports and side-by-side previews.",
    )
    parser.add_argument("--thumb-width", type=int, default=520, help="Preview thumbnail width.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    compare_folders(args.old, args.new, args.output, args.thumb_width)
