# studious_engine/innovations/admin.py
from django.contrib import admin
from .models import Innovation, InnovationContribution, TechTreeNode

class InnovationContributionInline(admin.TabularInline):
    model = InnovationContribution
    extra = 0
    fields = ('player', 'stage', 'impact_level', 'experience_reward', 'happiness_reward', 'contributed_at')
    readonly_fields = ('contributed_at',)

@admin.register(Innovation)
class InnovationAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'current_stage', 'progress', 'is_approved', 'implementation_date')
    list_filter = ('current_stage', 'is_approved', 'sector', 'affects_tech_tree')
    search_fields = ('name', 'description')
    filter_horizontal = ('zones',)
    inlines = [InnovationContributionInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'sector', 'zones')
        }),
        ('Status', {
            'fields': ('current_stage', 'progress', 'is_approved', 'implementation_date')
        }),
        ('Order (Taxis)', {
            'fields': ('order_components', 'order_metrics'),
            'classes': ('collapse',)
        }),
        ('Arrangement (Diathesis)', {
            'fields': ('arrangement_ground_plan', 'arrangement_elevation', 'arrangement_perspective'),
            'classes': ('collapse',)
        }),
        ('Eurythmy', {
            'fields': ('eurythmy_components',),
            'classes': ('collapse',)
        }),
        ('Symmetry', {
            'fields': ('symmetry_standard', 'symmetry_relations'),
            'classes': ('collapse',)
        }),
        ('Propriety', {
            'fields': ('propriety_principles', 'propriety_justification'),
            'classes': ('collapse',)
        }),
        ('Economy', {
            'fields': ('economy_resources', 'economy_implementation'),
            'classes': ('collapse',)
        }),
        ('Impact', {
            'fields': ('expected_impact', 'actual_impact')
        }),
        ('Tech Tree', {
            'fields': ('affects_tech_tree', 'tech_tree_node')
        }),
    )

@admin.register(InnovationContribution)
class InnovationContributionAdmin(admin.ModelAdmin):
    list_display = ('player', 'innovation', 'stage', 'impact_level', 'contributed_at')
    list_filter = ('stage', 'impact_level')
    search_fields = ('player__user__username', 'innovation__name', 'contribution_description')
    readonly_fields = ('contributed_at',)

@admin.register(TechTreeNode)
class TechTreeNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'level', 'is_unlocked', 'unlocked_at', 'unlocked_by_innovation')
    list_filter = ('sector', 'level', 'is_unlocked')
    search_fields = ('name', 'description')
    filter_horizontal = ('prerequisites', 'unlocked_experiences', 'unlocked_powers')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'sector', 'level')
        }),
        ('Relationships', {
            'fields': ('prerequisites', 'unlocked_experiences', 'unlocked_powers')
        }),
        ('Status', {
            'fields': ('is_unlocked', 'unlocked_at', 'unlocked_by_innovation')
        }),
        ('Visualization', {
            'fields': ('icon', 'position_x', 'position_y')
        }),
    )