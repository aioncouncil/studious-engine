# studious_engine/core/admin.py
from django.contrib import admin
from .models import PlayerProfile, PlayerHappiness

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