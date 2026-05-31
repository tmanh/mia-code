# Prompt Template: Write A WordPress Recipe Post From Minimal Inputs

Use this prompt when the user wants Codex to write a full Keep Up Cooking WordPress/Gutenberg recipe post without manually choosing image URLs, slugs, keywords, FAQ, or image placement.

## Everyday Prompt

```text
Write a complete Keep Up Cooking WordPress recipe post as Gutenberg HTML.

Use these local references:
- template/direct_upload_recipe_post_template.html
- template/wordpress_image_url_guideline.md
- template/recipe_post_reference_rhubarb_tea.html
- template/recipe_post_template.md

I will provide only the basics:

- Title: [RECIPE TITLE]
- Image folder: [ABSOLUTE LOCAL IMAGE FOLDER PATH]
- Ingredients:
  - [ingredient 1 + amount]
  - [ingredient 2 + amount]
  - [ingredient 3 + amount]
- Steps:
  1. [brief step 1]
  2. [brief step 2]
  3. [brief step 3]
- Optional keyword: [KEYWORD, or leave blank]

Your job:

1. Infer the slug from the title.
2. Infer the main keyword if I do not provide one.
3. Infer the upload year/month from the image folder path when possible.
4. Read the image folder and choose the best images for:
   - hero image
   - ingredients/process image
   - step images
   - final/serving image
5. Ignore macOS `._*` files and tiny thumbnail variants unless a thumbnail is specifically needed.
6. Build exact public URLs using:
   https://keepupcooking.com/wp-content/uploads/[YYYY]/[MM]/[filename]
7. Use direct-upload Gutenberg image blocks without WordPress Media Library IDs:
   - no `"id"`
   - no `wp-image-ID`
8. Expand my brief ingredients and steps into a polished Keep Up Cooking recipe post.
9. Add helpful sections when appropriate:
   - Why You'll Love This [Recipe]
   - Ingredients
   - How to Make [Recipe]
   - Tips
   - Frequently Asked Questions
   - More [Topic] Recipes
10. Include the standard Keep Up Cooking social CTA.
11. Save the finished HTML as:
   template/generated_[slug]_post.html
12. Also save a short image mapping file as:
   template/generated_[slug]_image_map.md

Only ask me a clarification question if:
- the image folder path does not reveal the upload year/month,
- the folder has no usable images,
- the recipe steps are too vague to safely complete,
- or there are multiple unrelated recipe image sets in the folder and the correct set is unclear.
```

## Minimum User Input

The user should only need to provide:

```text
Title:
Image folder:
Ingredients:
Steps:
Optional keyword:
```

Everything else should be inferred where safe.

## Codex Workflow

When executing the prompt:

1. Read the local references listed above.
2. Inspect the image folder with `find` or `rg --files`.
3. Ignore:
   - files beginning with `._`
   - obvious thumbnails such as `-150x150`
   - very small variants unless no larger option exists
4. Group image variants by base image name.
5. Prefer original, `-scaled`, or `1024x...` images for post body.
6. Infer upload year/month from path segments like `/2026/05/`.
7. Build URLs with:

   ```text
   https://keepupcooking.com/wp-content/uploads/YYYY/MM/filename.webp
   ```

8. Choose image placement:
   - strongest/final image near the top as hero
   - ingredient/table/process images near Ingredients
   - process images after matching step sections
   - beauty/final serving image near the end or before FAQ
9. If filenames are numbered, keep a natural visual sequence unless the filename clearly indicates final/hero.
10. Write complete Gutenberg block HTML, not Markdown.
11. Save the generated post and image map.

## Defaults

- Post type: `post`
- Post status: `draft`
- Image workflow: direct upload
- Image block style: no Media Library IDs
- Main keyword: title normalized into a natural search phrase
- Slug: lowercase title converted to hyphenated ASCII where possible
- Hero image `sizeSlug`: `full`
- Process image `sizeSlug`: `large` if using a `1024x...` file, otherwise `full`
- WP Recipe Maker block: omit unless user provides recipe card details or a WPRM ID
- Related links: include placeholders if the user did not provide real internal links

## Direct-Upload Image Block

Use this when the user will upload files directly to Hostinger / `wp-content/uploads/YYYY/MM/`:

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/YYYY/MM/filename.webp" alt="recipe keyword"/></figure>
<!-- /wp:image -->
```

Do not use this unless the user gives real Media Library IDs:

```html
<!-- wp:image {"id":123,"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/YYYY/MM/filename.webp" alt="recipe keyword" class="wp-image-123"/></figure>
<!-- /wp:image -->
```

## Output Files

For a title like `Simple Rhubarb Tea Recipe`, save:

```text
template/generated_simple-rhubarb-tea-recipe_post.html
template/generated_simple-rhubarb-tea-recipe_image_map.md
```

The image map should list:

```text
# Image Map: [Recipe Title]

- Hero: filename.webp -> https://keepupcooking.com/wp-content/uploads/YYYY/MM/filename.webp
- Ingredients/process: filename.webp -> URL
- Step 1: filename.webp -> URL
- Step 2: filename.webp -> URL
- Final: filename.webp -> URL
```

## Final Response To User

Keep the final response short:

- generated post file path
- image map file path
- any assumptions
- any missing items to check in WordPress
