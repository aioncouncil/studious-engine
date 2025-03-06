# studious_engine/core/admin.py
from django.contrib import admin
from .models import PlayerProfile, PlayerHappiness

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class PlayerHappinessInline(admin.StackedInline):
    model = PlayerHappiness
    can_delete = False
    verbose_name_plural = 'Happiness Metrics'
    fieldsets = (
        ('Soul', {
            'fields': ('wisdom', 'courage', 'temperance', 'justice')
        }),
        ('Body', {
            'fields': ('strength', 'wealth', 'beauty', 'health')
        }),
        ('Environment', {
            'fields': ('resources', 'friendships', 'honors', 'glory')
        }),
    )

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'experience_points', 'created_at')
    list_filter = ('rank', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'rank', 'experience_points')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'last_location_update')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [PlayerHappinessInline]