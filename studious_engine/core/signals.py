# studious_engine/core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core.models import PlayerProfile, PlayerHappiness

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create a PlayerProfile and associated PlayerHappiness when a User is created."""
    if created:
        player_profile = PlayerProfile.objects.create(user=instance)
        PlayerHappiness.objects.create(player=player_profile)


@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    """Ensure the PlayerProfile is saved when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()