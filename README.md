# mia-code

## Batch Photo Adjuster

Open `batch-photo-adjuster.html` in a browser to auto-adjust and export many
photos with one Canva-style control panel.

1. Click **Select photos** and choose multiple images.
2. The tool detects and auto-adjusts each photo separately.
3. Click any thumbnail to fine-tune that photo, crop, rotate, zoom, or use
   **Smart Crop** to center the subject.
4. Use **Apply current settings to all** when one look and crop should be shared
   by the whole batch.
5. Set the export general name, starting index, output format, size, and
   quality. Use **Original name + general name + number** when you want names
   like `IMG_1234-rhubarb-tea-1.webp`.
6. Click **Save adjusted batch** to save renamed, resized photos.

When exporting WebP, **Keep WebP exports under 1 MB** is enabled by default.
The tool starts with your selected size and quality, then automatically lowers
quality and dimensions only for files that are still larger than 1 MB.

Chrome and Edge can save the whole batch directly into a folder. Other browsers
may download the adjusted photos one by one.

HEIC/HEIF files need browser-side conversion. The HTML tool loads `heic2any`
from jsDelivr and converts iPhone HEIC photos to temporary JPEG files before
editing starts, so open it with internet access if you want to import HEIC
directly.

For the most reliable HEIC workflow, prepare the batch locally first:

```bash
python3 prepare_photos_for_adjuster.py --folder "/path/to/photo folder"
```

This creates an `adjuster-ready` folder, converts HEIC/HEIF files to JPEG, and
copies the other image files. Upload photos from `adjuster-ready` into the Batch
Photo Adjuster to avoid browser HEIC failures.

## Python WebP Converter

`mw-to-webp.py` can rename and convert images, or only convert them.

- Set `DEFAULT_GENERAL_NAME = ""` or `DEFAULT_GENERAL_NAME = 0` to keep the
  original filenames and only create WebP files in the `compress` folder.
- Set `DEFAULT_GENERAL_NAME = "your-name"` to safely rename files before
  converting them.
