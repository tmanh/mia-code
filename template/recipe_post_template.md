# Recipe Post Template

Extracted from these published WordPress posts in `20061_posts`:

- `Simple Rhubarb Syrup Recipe`
- `How to Brew Vietnamese Black Coffee with Phin Filter`
- `Homemade Pumpkin Spice Latte`

The post has two layers:

- Row metadata in `20061_posts`: `ID`, `post_title`, `post_name`, `post_type`, `post_status`, `post_date`, etc.
- Body content in `20061_posts.post_content`: the Gutenberg block HTML used by `recipe_post_template.html`.

So this file describes the writing/content structure. For the database row fields like `ID 14789 · slug: homemade-pumpkin-spice-latte · post · publish · 2025-10-21 22:20:34`, see `recipe_post_database_template.md`.

## Recommended Structure

1. SEO intro / hook
   - Use a Gutenberg paragraph block:
     `<p>Easy [recipe keyword] with [main benefit/flavor].</p>`
   - The first paragraph should clearly name the recipe and main benefit.

2. Hero image
   - Use the exact WordPress image block format:

   ```html
   <!-- wp:image {"id":17786,"sizeSlug":"full","linkDestination":"none"} -->
   <figure class="wp-block-image size-full"><img src="https://keepupcooking.com/wp-content/uploads/YYYY/MM/image.webp" alt="recipe keyword" class="wp-image-17786"/></figure>
   <!-- /wp:image -->
   ```

   - `id` and `wp-image-ID` must match the WordPress media attachment ID.
   - `sizeSlug` is usually `full` for hero/final images and `large` for process images.
   - `alt` should naturally match the recipe keyword.

3. Optional table of contents
   - `Homemade Pumpkin Spice Latte` includes a Rank Math TOC block.
   - The other two examples do not, so this is optional.

4. Context or "why you'll love this"
   - Common headings:
     - `Why You’ll Love This [Recipe]`
     - `What is [Dish/Drink]?`
     - `[Main Tool/Ingredient]`
   - Use this section to explain why the recipe works and when to make it.

5. Ingredients and equipment
   - Common headings:
     - `Ingredients`
     - `Ingredients & Equipment`
   - Usually written as a WordPress list block.
   - Include amounts when useful.

   ```html
   <!-- wp:list -->
   <ul class="wp-block-list"><!-- wp:list-item -->
   <li>1 cup water</li>
   <!-- /wp:list-item --></ul>
   <!-- /wp:list -->
   ```

6. Step-by-step method
   - Common headings:
     - `How to Make [Recipe]`
     - `Step-by-Step [Method] Guide`
   - Use `h3` step headings:

   ```html
   <!-- wp:heading {"level":3} -->
   <h3 class="wp-block-heading">Step 1: Simmer the Rhubarb</h3>
   <!-- /wp:heading -->
   ```

   - Add one or more paragraph blocks after each step heading.
   - Add process images between steps when available.

7. Tips, variations, or usage ideas
   - Common headings:
     - `Tips for the Best [Recipe]`
     - `Tips & Variations`
     - `How to Use [Recipe]`
     - `Iced [Recipe] Version`
   - Include troubleshooting, substitutions, serving ideas, storage, and flavor adjustments.

8. Recipe card
   - Two examples use WP Recipe Maker:
     - `<!-- wp:wp-recipe-maker/recipe {"id":...} -->`
   - One example does not include a recipe card.
   - Use this when the post should have ratings, print button, ingredients, time, servings, and nutrition.
   - The pasted post does not include a recipe card, but the coffee/latte examples show the format:

   ```html
   <!-- wp:wp-recipe-maker/recipe {"id":17750} -->
   <!--WPRM Recipe 17750-->
   <div class="wprm-fallback-recipe">
     <h2 class="wprm-fallback-recipe-name">Recipe Card Title</h2>
     ...
   </div>
   <!--End WPRM Recipe-->
   <!-- /wp:wp-recipe-maker/recipe -->
   ```

   - Best workflow: create the recipe card in WP Recipe Maker first, then insert its generated block. The fallback HTML can be long and plugin-specific.

9. FAQ section
   - The pasted post uses a FAQ-like section with normal heading blocks, not a special FAQ schema block:

   ```html
   <!-- wp:heading -->
   <h2 class="wp-block-heading">Frequently Asked Questions</h2>
   <!-- /wp:heading -->

   <!-- wp:heading {"level":3} -->
   <h3 class="wp-block-heading">What does rhubarb tea taste like?</h3>
   <!-- /wp:heading -->

   <!-- wp:paragraph -->
   <p>Answer text.</p>
   <!-- /wp:paragraph -->
   ```

10. Social CTA
   - Repeated text in all three examples:

   ```html
   <p>Do you like this recipe? Brighten my day by rating the recipe and clicking the “save” button to have this recipe right on your&nbsp;<a href="https://www.pinterest.com/keepupcookingblog/">Pinterest</a>&nbsp;board. Also, let’s be friends on&nbsp;<a href="https://www.youtube.com/@keepupcookingblog?sub_confirmation=1">YouTube</a>,&nbsp;<a href="https://www.instagram.com/keepupcooking/">Instagram</a>,&nbsp;<a href="https://www.facebook.com/keepupcooking/">Facebook</a>&nbsp;and&nbsp;<a href="https://www.tiktok.com/@keepupcooking">TikTok</a>!</p>
   ```

11. Related recipes
    - Common headings:
      - `More [Topic] Recipes`
      - `Other [Topic] Recipes`
      - `Similar Recipes`
    - Use a bullet list of internal links.

## Fill-In Outline

```markdown
# [Recipe Title]

[Short SEO intro: what it is, main flavor/benefit, and why readers should make it.]

[Personal/context paragraph: season, culture, memory, or why this recipe matters.]

[Hero image: finished recipe]

## Why You’ll Love This [Recipe]

[2-4 short paragraphs or bullets about ease, flavor, texture, flexibility, ingredients, and result.]

## Ingredients

[Short lead-in sentence.]

- [Ingredient 1 + amount]
- [Ingredient 2 + amount]
- [Ingredient 3 + amount]
- [Optional ingredient]

## How to Make [Recipe]

### Step 1: [Action]

[Instruction paragraph.]

[Optional process image]

### Step 2: [Action]

[Instruction paragraph.]

[Optional process image]

### Step 3: [Action]

[Instruction paragraph.]

## Tips for the Best [Recipe]

[Tip 1.]

[Tip 2.]

[Tip 3.]

## How to Serve or Use [Recipe]

[Serving ideas, pairing ideas, drink/dessert use, storage, or variations.]

[WP Recipe Maker recipe card, if used]

[Social CTA paragraph]

## More [Topic] Recipes

- [Internal link 1]
- [Internal link 2]
- [Internal link 3]
```
