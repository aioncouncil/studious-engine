# studious_engine/experiences/admin.py
from django.contrib import admin
from .models import Power, PlayerPower, Experience, PlayerExperience

@admin.register(Power)
class PowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'power_type', 'rarity', 'complexity', 'sector', 'is_public')
    list_filter = ('power_type', 'rarity', 'sector', 'is_public')
    search_fields = ('name', 'description')
    filter_horizontal = ('prerequisites',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'power_type')
        }),
        ('Attributes', {
            'fields': ('rarity', 'complexity', 'sector')
        }),
        ('Availability', {
            'fields': ('is_public', 'prerequisites')
        }),
    )

@admin.register(PlayerPower)
class PlayerPowerAdmin(admin.ModelAdmin):
    list_display = ('player', 'power', 'level', 'experience', 'acquired_at', 'last_used_at')
    list_filter = ('level', 'acquired_at')
    search_fields = ('player__user__username', 'power__name')
    raw_id_fields = ('player', 'power')

class PlayerExperienceInline(admin.TabularInline):
    model = PlayerExperience
    extra = 0
    fields = ('player', 'status', 'progress', 'started_at', 'completed_at')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience_type', 'matrix_position', 'art_type', 
                    'good_type', 'difficulty', 'minimum_rank', 'is_active')
    list_filter = ('experience_type', 'matrix_position', 'art_type', 'good_type', 
                   'difficulty', 'minimum_rank', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ('required_powers', 'associated_zones', 'prerequisite_experiences')
    inlines = [PlayerExperienceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Categorization', {
            'fields': ('experience_type', 'matrix_position', 'art_type', 'good_type')
        }),
        ('Difficulty & Rewards', {
            'fields': ('difficulty', 'duration_minutes', 'happiness_reward', 'experience_reward')
        }),
        ('References', {
            'fields': ('required_powers', 'associated_zones', 'prerequisite_experiences'),
            'classes': ('collapse',)
        }),
        ('Five Parts of Art', {
            'fields': ('definition', 'end', 'parts', 'matter', 'instrument'),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_active', 'minimum_rank', 'start_date', 'end_date')
        }),
    )

@admin.register(PlayerExperience)
class PlayerExperienceAdmin(admin.ModelAdmin):
    list_display = ('player', 'experience', 'status', 'progress', 'happiness_gained', 
                    'experience_gained', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('player__user__username', 'experience__name', 'reflection_notes')
    readonly_fields = ('started_at', 'completed_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('player', 'experience')
        }),
        ('Progress', {
            'fields': ('status', 'progress', 'reflection_notes')
        }),
        ('Resources', {
            'fields': ('resources_committed',),
            'classes': ('collapse',)
        }),
        ('Rewards', {
            'fields': ('happiness_gained', 'experience_gained')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )