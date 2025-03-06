from django.contrib import admin
from .models import PhysicsSimulation, PhysicsInteraction

@admin.register(PhysicsSimulation)
class PhysicsSimulationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'iteration_rate', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'type')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'type')
        }),
        ('Simulation Parameters', {
            'fields': ('iteration_rate',),
            'classes': ('collapse',)
        }),
        ('Physics Components', {
            'fields': ('entities', 'forces', 'constraints'),
            'classes': ('collapse',)
        }),
        ('Visual Effects', {
            'fields': ('visual_effects',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PhysicsInteraction)
class PhysicsInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'simulation', 'session_duration', 'started_at', 'ended_at')
    list_filter = ('started_at', 'ended_at')
    search_fields = ('user__user__username', 'simulation__name')
    readonly_fields = ('id', 'started_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'simulation')
        }),
        ('Session Information', {
            'fields': ('session_duration', 'started_at', 'ended_at')
        }),
        ('Interaction Data', {
            'fields': ('interaction_data',),
            'classes': ('collapse',)
        }),
        ('Learning Outcomes', {
            'fields': ('learning_objectives', 'objectives_achieved'),
            'classes': ('collapse',)
        }),
    )
