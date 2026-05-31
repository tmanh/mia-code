# WordPress Image URL Guideline For Future Posts

Use this when generating a new WordPress post locally with image URLs already inserted.

## Goal

Prepare a complete Gutenberg post HTML file where image blocks already contain the final public image URLs, so the workflow is:

1. Upload image files to the correct Hostinger/WordPress uploads folder.
2. Paste or upload the prepared Gutenberg HTML post.
3. Check the post visually in WordPress.

This avoids manually inserting each image through the WordPress editor.

## Uploads Path Rule

The backup folder mirrors the WordPress uploads URL structure.

Local backup folder:

```text
/Volumes/ME/MEO/Blogging/keepupcooking/main-keepupcooking/full backup 260528/backup 2nd part 2025 2026/2026/05
```

Equivalent public URL folder:

```text
https://keepupcooking.com/wp-content/uploads/2026/05/
```

Example:

```text
Local file:
/Volumes/.../2026/05/rhubarb-syrup-recipe-6.webp

Public URL:
https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-syrup-recipe-6.webp
```

## Important: Media Library ID vs Direct File URL

There are two different image workflows.

## Workflow A: Images Uploaded Through WordPress Media Library

If the image is uploaded through WordPress Media Library, WordPress creates an attachment post in `20061_posts`. Then the image has a real media ID.

Use this block format:

```html
<!-- wp:image {"id":17786,"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-tea-recipe-10.webp" alt="rhubarb tea recipe" class="wp-image-17786"/></figure>
<!-- /wp:image -->
```

Rules:

- The JSON `id` must be the real WordPress attachment ID.
- The CSS class `wp-image-17786` must match the same real ID.
- Use this only when the ID is known.

## Workflow B: Images Uploaded By Hostinger File Manager, FTP, Or SFTP

If the image file is uploaded directly to:

```text
wp-content/uploads/YYYY/MM/
```

but not imported into the WordPress Media Library, there may be no real attachment ID.

Use this safer block format without `id`:

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-tea-recipe-10.webp" alt="rhubarb tea recipe"/></figure>
<!-- /wp:image -->
```

Rules:

- Do not invent `id`.
- Do not invent `wp-image-ID`.
- The image will still display because the `src` points to the public file URL.
- WordPress may treat it as an external/direct image rather than a Media Library item.

For this user workflow, default to **Workflow B** unless the user gives actual Media Library IDs.

## Which Image Size To Use

WordPress backup folders contain many generated sizes:

```text
recipe-name-1.webp
recipe-name-1-1024x683.webp
recipe-name-1-150x150.webp
recipe-name-1-500x375.webp
recipe-name-1-800x530.webp
recipe-name-1-scaled.webp
```

Default choices:

- Hero image: use the original `.webp` or `-scaled.webp` if the original is very large.
- Process images inside steps: use `-1024x683.webp`, `-1024x768.webp`, or `-1024x1536.webp` when available.
- Recipe card thumbnail: use `-150x150.webp`.
- Avoid tiny sizes like `150x150`, `300x200`, or `480x270` in the article body unless intentionally using a thumbnail.

For Gutenberg blocks:

- Use `sizeSlug:"full"` when using the original/full URL.
- Use `sizeSlug:"large"` when using a `1024x...` URL.

## Image Naming Pattern

For new posts, use predictable filenames before uploading:

```text
[recipe-slug]-1.webp
[recipe-slug]-2.webp
[recipe-slug]-3.webp
[recipe-slug]-4.webp
[recipe-slug]-5.webp
```

Example:

```text
rhubarb-tea-recipe-1.webp
rhubarb-tea-recipe-2.webp
rhubarb-tea-recipe-3.webp
```

Then the public URLs are predictable:

```text
https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-tea-recipe-1.webp
https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-tea-recipe-2.webp
https://keepupcooking.com/wp-content/uploads/2026/05/rhubarb-tea-recipe-3.webp
```

## Future Codex Workflow

When asked to create a post with images:

1. Ask for or infer:
   - recipe title
   - recipe slug
   - upload year/month
   - image filenames
   - whether images were uploaded through Media Library or direct file upload

2. If direct upload, generate image URLs like:

   ```text
   https://keepupcooking.com/wp-content/uploads/[YYYY]/[MM]/[filename]
   ```

3. Use image blocks without IDs:

   ```html
   <!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
   <figure class="wp-block-image size-full"><img src="[PUBLIC_IMAGE_URL]" alt="[recipe keyword]"/></figure>
   <!-- /wp:image -->
   ```

4. If the user provides real Media Library IDs, use image blocks with IDs:

   ```html
   <!-- wp:image {"id":[IMAGE_ID],"sizeSlug":"full","linkDestination":"none"} -->
   <figure class="wp-block-image size-full"><img src="[PUBLIC_IMAGE_URL]" alt="[recipe keyword]" class="wp-image-[IMAGE_ID]"/></figure>
   <!-- /wp:image -->
   ```

5. For every image, include:
   - final public URL
   - meaningful alt text
   - correct `sizeSlug`
   - no fake IDs

6. Produce a final post HTML file that can be pasted into WordPress Code Editor.

## Reusable Direct-Upload Image Blocks

Hero/full image:

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/[YYYY]/[MM]/[recipe-slug]-1.webp" alt="[recipe keyword]"/></figure>
<!-- /wp:image -->
```

Large process image:

```html
<!-- wp:image {"sizeSlug":"large","linkDestination":"none"} -->
<figure class="wp-block-image size-large"><img src="https://keepupcooking.com/wp-content/uploads/[YYYY]/[MM]/[recipe-slug]-2-1024x683.webp" alt="[recipe keyword]"/></figure>
<!-- /wp:image -->
```

Final image:

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/[YYYY]/[MM]/[recipe-slug]-final.webp" alt="[recipe keyword]"/></figure>
<!-- /wp:image -->
```

## Checklist Before Posting

- Image files have been uploaded to `wp-content/uploads/YYYY/MM/`.
- Each image URL opens in the browser.
- Gutenberg image blocks do not contain fake IDs.
- Hero image appears near the top of the post.
- Process images appear after the relevant steps.
- Alt text uses the recipe keyword naturally.
- Related links and CTA are included.
