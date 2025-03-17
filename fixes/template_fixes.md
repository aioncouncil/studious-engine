# Django Template Fixes

## Issue
Several Django templates had the `{% extends %}` tag not as the first tag in the template. According to Django's template system, the `{% extends %}` tag must be the first tag in a template (except for comments).

This issue caused TemplateSyntaxError exceptions like:
```
<ExtendsNode: extends "base.html"> must be the first tag in the template.
```

## Fixed Templates
The following templates were fixed by moving the `{% extends %}` tag to be the first line in the file, before any comment blocks:

1. `studious_engine/core/templates/core/arts/art_detail.html`
2. `studious_engine/core/templates/core/arts/mastery_dashboard.html`
3. `studious_engine/core/templates/core/arts/mastery_stats.html`
4. `studious_engine/core/templates/core/arts/tech_tree_detail.html`
5. `studious_engine/core/templates/core/arts/tech_tree.html`
6. `studious_engine/core/templates/core/arts/pokedex.html`
7. `studious_engine/core/templates/core/dashboard.html`
8. `studious_engine/core/templates/core/virtues.html`
9. `studious_engine/zones/templates/zones/sector_list.html`
10. `studious_engine/zones/templates/zones/sector_detail.html`
11. `studious_engine/zones/templates/zones/zone_detail.html`
12. `studious_engine/experiences/templates/experiences/experience_instance_list.html`
13. `studious_engine/experiences/templates/experiences/experience_list.html`
14. `studious_engine/experiences/templates/experiences/experience_instance_detail.html`
15. `studious_engine/templates/core/store.html`

## Example Fix
Original:
```html
{% comment %}
[CLAUDE:OPTIMIZATION_LAYER:START]
This template is part of the core_user_system component
See .claude/README.md for more information
[CLAUDE:OPTIMIZATION_LAYER:END]
{% endcomment %}

{% extends "base.html" %}
{% load static %}
```

Fixed:
```html
{% extends "base.html" %}
{% comment %}
[CLAUDE:OPTIMIZATION_LAYER:START]
This template is part of the core_user_system component
See .claude/README.md for more information
[CLAUDE:OPTIMIZATION_LAYER:END]
{% endcomment %}

{% load static %}
```

## Outcome
After applying these fixes, all the templates now render correctly without TemplateSyntaxError exceptions.
