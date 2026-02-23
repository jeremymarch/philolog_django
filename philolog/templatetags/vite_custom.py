import json
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def vite_asset_custom(entry_name: str):
    from django.templatetags.static import static
    manifest_path = Path(settings.DJANGO_VITE_MANIFEST_PATH)
    if not manifest_path.exists():
        # Handle case where manifest doesn't exist, e.g., in development
        # This is a simplified example; a robust solution would handle dev server
        return mark_safe("<!-- manifest.json not found -->")

    with open(manifest_path) as f:
        manifest = json.load(f)

    entry = manifest.get(entry_name)
    if not entry:
        return mark_safe(f"<!-- entry {entry_name} not found in manifest.json -->")

    js_file = entry.get("file")
    css_files = entry.get("css", [])
    
    # We need to construct the path relative to the static directory root
    static_root = settings.BASE_DIR / "static"
    assets_dir_relative = Path(settings.DJANGO_VITE_ASSETS_PATH).relative_to(static_root)

    tags = []
    for css_file in css_files:
        path_for_static_tag = assets_dir_relative / css_file
        tags.append(f'<link rel="stylesheet" href="{static(str(path_for_static_tag))}">')

    if js_file:
        path_for_static_tag = assets_dir_relative / js_file
        tags.append(f'<script type="module" src="{static(str(path_for_static_tag))}"></script>')

    return mark_safe("\n".join(tags))
