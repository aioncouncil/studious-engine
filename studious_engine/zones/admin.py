# studious_engine/zones/admin.py
from django.contrib import admin
from .models import Sector, Zone, ZoneHappiness, PlayerZoneContribution

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    show_change_link = True
    fields = ('zone_number', 'zone_type', 'area', 'rank')
    ordering = ('zone_number',)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'number')
    search_fields = ('name',)
    inlines = [ZoneInline]

class ZoneHappinessInline(admin.StackedInline):
    model = ZoneHappiness
    can_delete = False
    verbose_name_plural = 'Zone Happiness'
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

class PlayerContributionInline(admin.TabularInline):
    model = PlayerZoneContribution
    extra = 0
    fields = ('player', 'think_tank_contributions', 'production_tank_contributions', 
              'overall_influence', 'is_zone_leader')
    readonly_fields = ('player',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_type', 'area', 'city', 'country', 'sector', 'rank', 'is_active')
    list_filter = ('area', 'is_active', 'rank', 'sector')
    search_fields = ('zone_type', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ZoneHappinessInline, PlayerContributionInline]
    fieldsets = (
        (None, {
            'fields': ('zone_type', 'area', 'sector', 'rank')
        }),
        ('Location', {
            'fields': ('city', 'country', 'city_latitude', 'city_longitude', 'country_latitude', 'country_longitude')
        }),
        ('Moderation', {
            'fields': ('is_active', 'description', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_zones', 'reject_zones']
    
    def approve_zones(self, request, queryset):
        """Approve the selected zones."""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} zone(s) approved successfully.')
    approve_zones.short_description = "Approve selected zones"
    
    def reject_zones(self, request, queryset):
        """Reject the selected zones."""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} zone(s) rejected successfully.')
    reject_zones.short_description = "Reject selected zones"

@admin.register(PlayerZoneContribution)
class PlayerZoneContributionAdmin(admin.ModelAdmin):
    list_display = ('player', 'zone', 'overall_influence', 'is_zone_leader')
    list_filter = ('is_zone_leader', 'zone__sector')
    search_fields = ('player__user__username', 'zone__zone_type')