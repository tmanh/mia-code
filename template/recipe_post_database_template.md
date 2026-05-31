# Recipe Post Database Template

This is the database-level equivalent of the information shown in the viewer:

```text
Homemade Pumpkin Spice Latte
ID 14789 · slug: homemade-pumpkin-spice-latte · post · publish · 2025-10-21 22:20:34
```

Those values come from the WordPress posts table:

```text
20061_posts
```

## Field Mapping

| Viewer label | Database column | Example value |
| --- | --- | --- |
| Title | `post_title` | `Homemade Pumpkin Spice Latte` |
| ID | `ID` | `14789` |
| slug | `post_name` | `homemade-pumpkin-spice-latte` |
| content type | `post_type` | `post` |
| status | `post_status` | `publish` |
| date | `post_date` | `2025-10-21 22:20:34` |
| body content | `post_content` | Gutenberg block HTML |
| excerpt | `post_excerpt` | Usually empty or short summary |
| author | `post_author` | User ID from `20061_users.ID` |
| parent | `post_parent` | `0` for normal posts |
| menu order | `menu_order` | Usually `0` |
| comment status | `comment_status` | Usually `open` or `closed` |
| ping status | `ping_status` | Usually `open` or `closed` |
| canonical URL path | `post_name` plus permalink settings | slug-based URL |

## SQL Shape

Use this query to inspect the full database row for a recipe post:

```sql
SELECT
  ID,
  post_author,
  post_date,
  post_date_gmt,
  post_content,
  post_title,
  post_excerpt,
  post_status,
  comment_status,
  ping_status,
  post_password,
  post_name,
  to_ping,
  pinged,
  post_modified,
  post_modified_gmt,
  post_content_filtered,
  post_parent,
  guid,
  menu_order,
  post_type,
  post_mime_type,
  comment_count
FROM `20061_posts`
WHERE ID = 14789;
```

## Insert Template

This is a simplified row template for creating a new recipe post directly in SQL.

Important: WordPress normally creates posts through the admin/editor so it can also manage revisions, taxonomy relationships, featured images, plugin data, and recipe cards. Use direct SQL carefully.

```sql
INSERT INTO `20061_posts` (
  post_author,
  post_date,
  post_date_gmt,
  post_content,
  post_title,
  post_excerpt,
  post_status,
  comment_status,
  ping_status,
  post_password,
  post_name,
  to_ping,
  pinged,
  post_modified,
  post_modified_gmt,
  post_content_filtered,
  post_parent,
  guid,
  menu_order,
  post_type,
  post_mime_type,
  comment_count
) VALUES (
  [AUTHOR_ID],
  '[LOCAL_POST_DATE]',
  '[GMT_POST_DATE]',
  '[GUTENBERG_BLOCK_HTML]',
  '[RECIPE_TITLE]',
  '[OPTIONAL_EXCERPT]',
  'publish',
  'open',
  'open',
  '',
  '[recipe-slug]',
  '',
  '',
  '[LOCAL_MODIFIED_DATE]',
  '[GMT_MODIFIED_DATE]',
  '',
  0,
  '[FULL_GUID_OR_URL]',
  0,
  'post',
  '',
  0
);
```

## Example From The Database

```sql
SELECT
  ID,
  post_title,
  post_name AS slug,
  post_type,
  post_status,
  post_date
FROM `20061_posts`
WHERE post_title = 'Homemade Pumpkin Spice Latte'
  AND post_type = 'post';
```

Result:

```text
ID: 14789
post_title: Homemade Pumpkin Spice Latte
slug/post_name: homemade-pumpkin-spice-latte
post_type: post
post_status: publish
post_date: 2025-10-21 22:20:34
```

## Related Data Outside `20061_posts`

Some important recipe-post information is stored in other tables:

- Categories and tags: `20061_terms`, `20061_term_taxonomy`, `20061_term_relationships`
- Featured image: `20061_postmeta` with key `_thumbnail_id`
- SEO/plugin fields: `20061_postmeta`
- WP Recipe Maker cards: plugin tables and/or `wp-recipe-maker` blocks in `post_content`
- Author details: `20061_users` and `20061_usermeta`
