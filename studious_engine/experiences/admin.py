# studious_engine/experiences/admin.py
from django.contrib import admin
from .models import Power, PlayerPower, Experience, PlayerExperience, ExperienceInstance, ExperienceParticipation

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

@admin.register(Power)
class PowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'power_type', 'rarity', 'complexity', 'is_public')
    list_filter = ('power_type', 'rarity', 'is_public', 'sector')
    search_fields = ('name', 'description')
    filter_horizontal = ('prerequisites',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'power_type', 'sector')
        }),
        ('Attributes', {
            'fields': ('rarity', 'complexity')
        }),
        ('Availability', {
            'fields': ('is_public', 'prerequisites')
        }),
    )

@admin.register(PlayerPower)
class PlayerPowerAdmin(admin.ModelAdmin):
    list_display = ('player', 'power', 'level', 'experience', 'acquired_at', 'last_used_at')
    list_filter = ('level', 'acquired_at', 'power__power_type')
    search_fields = ('player__user__username', 'power__name')
    raw_id_fields = ('player', 'power')
    fieldsets = (
        (None, {
            'fields': ('player', 'power')
        }),
        ('Mastery', {
            'fields': ('level', 'experience')
        }),
        ('Timestamps', {
            'fields': ('acquired_at', 'last_used_at')
        }),
    )

class PlayerExperienceInline(admin.TabularInline):
    model = PlayerExperience
    extra = 0
    fields = ('player', 'status', 'progress', 'started_at', 'completed_at')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience_type', 'matrix_position', 'difficulty', 'duration_minutes', 'is_active')
    list_filter = ('experience_type', 'matrix_position', 'art_type', 'good_type', 'is_active', 'minimum_rank')
    search_fields = ('name', 'description')
    filter_horizontal = ('required_powers', 'associated_zones', 'prerequisite_experiences')
    inlines = [PlayerExperienceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Categorization', {
            'fields': ('experience_type', 'matrix_position', 'art_type', 'good_type')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Difficulty & Rewards', {
            'fields': ('difficulty', 'duration_minutes', 'happiness_reward', 'experience_reward')
        }),
        ('References', {
            'fields': ('required_powers', 'associated_zones', 'prerequisite_experiences')
        }),
        ('Structure', {
            'fields': ('definition', 'end', 'parts', 'matter', 'instrument')
        }),
        ('Availability', {
            'fields': ('minimum_rank', 'start_date', 'end_date')
        }),
    )

@admin.register(PlayerExperience)
class PlayerExperienceAdmin(admin.ModelAdmin):
    list_display = ('player', 'experience', 'status', 'progress', 'started_at', 'completed_at')
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

@admin.register(ExperienceInstance)
class ExperienceInstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience', 'host', 'zone', 'start_time', 'status', 'current_participants', 'capacity')
    list_filter = ('status', 'frequency', 'start_time', 'is_public')
    search_fields = ('name', 'experience__name', 'host__user__username', 'location_description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'experience', 'name', 'host', 'zone')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'frequency', 'recurrence_rule')
        }),
        ('Status', {
            'fields': ('status', 'capacity', 'current_participants', 'is_public')
        }),
        ('Location', {
            'fields': ('location_description', 'meeting_point')
        }),
        ('Matrix Flow', {
            'fields': ('current_matrix_phase', 'matrix_flow_data'),
            'classes': ('collapse',)
        }),
        ('Resources & Outcomes', {
            'fields': ('resources_provided', 'outcomes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('experience', 'host', 'zone')

@admin.register(ExperienceParticipation)
class ExperienceParticipationAdmin(admin.ModelAdmin):
    list_display = ('player', 'instance', 'status', 'joined_at', 'completed_at', 'satisfaction_rating')
    list_filter = ('status', 'joined_at', 'completed_at')
    search_fields = ('player__user__username', 'instance__name', 'feedback')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'instance', 'player')
        }),
        ('Status', {
            'fields': ('status', 'joined_at', 'completed_at', 'withdrawn_at')
        }),
        ('Contributions & Outcomes', {
            'fields': ('contributions', 'personal_outcomes')
        }),
        ('Feedback', {
            'fields': ('feedback', 'satisfaction_rating')
        }),
        ('Rewards', {
            'fields': ('happiness_gained', 'experience_gained', 'resources_gained')
        }),
        ('Matrix Flow', {
            'fields': ('individual_flow_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('instance', 'player')