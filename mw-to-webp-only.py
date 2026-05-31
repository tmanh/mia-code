import os
import os.path as osp
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

folder_path= '/Volumes/ME/MEO/Blogging/keepupcooking/main-keepupcooking/articles_keepupcooking/00-rhubarb tea'
# Replace with the path to your folder


#change format of the file
# Enable HEIC/HEIF support
register_heif_opener()

# Pillow's default decompression-bomb limit can reject very large camera images
# before we get a chance to resize them. This script is for trusted local files,
# so allow larger images while still blocking wildly oversized inputs.
Image.MAX_IMAGE_PIXELS = 500_000_000


def list_image_files(folder_path):
    image_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.heic', '.heif', '.webp')):
            if filename.startswith("._") or filename.startswith("."):
                continue
            image_files.append(filename)
    return image_files


def convert_to_webp(image_path, out_path, quality, resize_percentage):
    try:
        with Image.open(image_path) as img:
            icc_profile = img.info.get("icc_profile")
            img = ImageOps.exif_transpose(img)
            width, height = img.size
            img = img.resize(
                (int(width * resize_percentage / 100.0), int(height * resize_percentage / 100.0)),
                resample=Image.Resampling.LANCZOS,
            )

            try:
                img.save(out_path, "WEBP", quality=quality, method=6, icc_profile=icc_profile)
            except OSError:
                img.save(out_path, "WEBP", quality=quality, method=6)
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        print(f"Skipping {image_path}: {error}")


def convert_all_images(ifiles, ofiles, quality, resize_percentage):
    for ifile, ofile in zip(ifiles, ofiles):
        print(ifile, osp.exists(ifile))
        if not osp.exists(ifile):
            continue

        _, ext = osp.splitext(ifile)
        ofile = ofile.replace(ext, '.webp')
        if not osp.exists(ofile):
            print("Converting:", ifile)
            convert_to_webp(ifile, ofile, quality, resize_percentage)


def main(in_dir, quality, resize_percentage):
    filenames = list_image_files(in_dir)

    out_dir = osp.join(in_dir, 'compress')
    if not osp.exists(out_dir):
        os.mkdir(out_dir)

    inames = [osp.join(in_dir, f) for f in filenames]
    onames = [osp.join(out_dir, f) for f in filenames]

    convert_all_images(inames, onames, quality, resize_percentage)

if __name__ == '__main__':
    quality = 70
    resize_percentage = 70
    main(folder_path, quality, resize_percentage)
