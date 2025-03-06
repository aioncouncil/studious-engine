from django import template
from django.utils.html import format_html
from experiences.models import Experience, PlayerExperience

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get(dictionary, key):
    """Get an item from a dictionary"""
    return dictionary.get(key)

@register.filter
def attr(obj, attr_name):
    """Get an attribute from an object"""
    return getattr(obj, attr_name, None)

@register.simple_tag
def progress_bar_class(progress):
    """Return Bootstrap classes for progress bars based on completion percentage."""
    if progress < 25:
        return "progress-bar bg-danger"
    elif progress < 50:
        return "progress-bar bg-warning"
    elif progress < 75:
        return "progress-bar bg-info"
    else:
        return "progress-bar bg-success"

@register.simple_tag
def experience_type_badge(experience_type):
    """Return HTML for a styled badge based on experience type."""
    badge_classes = {
        'quest': 'bg-primary',
        'challenge': 'bg-success',
        'collaboration': 'bg-info',
        'innovation': 'bg-warning',
        'reflection': 'bg-secondary',
    }
    
    badge_class = badge_classes.get(experience_type, 'bg-secondary')
    
    return format_html('<span class="badge {}">{}</span>',
                      badge_class,
                      dict(Experience.TYPE_CHOICES).get(experience_type, 'Unknown'))

@register.filter
def experience_reward_text(points):
    """Format experience reward points with appropriate text."""
    if points < 100:
        return f"{points} XP (Small)"
    elif points < 250:
        return f"{points} XP (Medium)"
    elif points < 500:
        return f"{points} XP (Large)"
    else:
        return f"{points} XP (Huge)" 