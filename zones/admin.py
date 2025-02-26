# studious_engine/zones/admin.py
from django.contrib import admin
from .models import Sector, Zone, ZoneHappiness, PlayerZoneContribution

class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    show_change_link = True
    fields = ('zone_number', 'zone_type', 'area', 'rank')
    ordering = ('zone_number',)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'is_governing', 'governing_start_date')
    list_filter = ('is_governing',)
    search_fields = ('name', 'description')
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
    list_display = ('__str__', 'sector', 'zone_number', 'zone_type', 'area', 'rank')
    list_filter = ('sector', 'area', 'rank')
    search_fields = ('zone_type',)
    inlines = [ZoneHappinessInline, PlayerContributionInline]
    fieldsets = (
        (None, {
            'fields': ('sector', 'zone_number', 'zone_type', 'area', 'rank')
        }),
        ('Physical Location', {
            'fields': ('city_latitude', 'city_longitude', 'country_latitude', 'country_longitude'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlayerZoneContribution)
class PlayerZoneContributionAdmin(admin.ModelAdmin):
    list_display = ('player', 'zone', 'overall_influence', 'is_zone_leader')
    list_filter = ('is_zone_leader', 'zone__sector')
    search_fields = ('player__user__username', 'zone__zone_type')