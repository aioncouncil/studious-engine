from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
import uuid

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class TechTree(models.Model):
    """
    Technology tree linking arts progression.
    """
    ZONE_TYPES = (
        ('ANY', _('Any Zone')),
        ('ACADEMIC', _('Academic')),
        ('CULTURAL', _('Cultural')), 
        ('NATURAL', _('Natural')),
        ('SOCIAL', _('Social')),
        ('ECONOMIC', _('Economic')),
        ('GOVERNANCE', _('Governance')),
        ('INNOVATION', _('Innovation')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    level = models.IntegerField(_('Level'), default=1)
    required_arts = ArrayField(
        models.UUIDField(),
        verbose_name=_('Required Arts'),
        blank=True,
        default=list,
        help_text=_('UUIDs of arts required to unlock this tech tree node')
    )
    unlocks_arts = ArrayField(
        models.UUIDField(),
        verbose_name=_('Unlocks Arts'),
        blank=True,
        default=list,
        help_text=_('UUIDs of arts unlocked by this tech tree node')
    )
    required_resources = models.JSONField(_('Required Resources'), default=dict, blank=True)
    required_zone_level = models.IntegerField(_('Required Zone Level'), default=1)
    zone_type_filter = models.CharField(
        _('Zone Type Filter'),
        max_length=20,
        choices=ZONE_TYPES,
        default='ANY'
    )
    parent_nodes = models.ManyToManyField(
        'self',
        verbose_name=_('Parent Nodes'),
        symmetrical=False,
        blank=True,
        related_name='child_nodes'
    )
    position_x = models.IntegerField(_('X Position'), default=0)
    position_y = models.IntegerField(_('Y Position'), default=0)
    icon = models.CharField(_('Icon Path'), max_length=255, blank=True)
    unlock_message = models.TextField(_('Unlock Message'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tech Tree')
        verbose_name_plural = _('Tech Trees')
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    @property
    def is_root_node(self):
        """Check if this is a root node (no parents)"""
        return self.parent_nodes.count() == 0
    
    @property
    def is_leaf_node(self):
        """Check if this is a leaf node (no children)"""
        return self.child_nodes.count() == 0
    
    def get_all_prerequisites(self):
        """Get all prerequisite nodes (recursively including ancestors)"""
        all_prereqs = set()
        
        def collect_parents(node):
            parents = node.parent_nodes.all()
            for parent in parents:
                if parent.id not in all_prereqs:
                    all_prereqs.add(parent.id)
                    collect_parents(parent)
        
        collect_parents(self)
        return TechTree.objects.filter(id__in=all_prereqs)
    
    def get_all_unlocks(self):
        """Get all nodes this one unlocks (recursively including descendants)"""
        all_unlocks = set()
        
        def collect_children(node):
            children = node.child_nodes.all()
            for child in children:
                if child.id not in all_unlocks:
                    all_unlocks.add(child.id)
                    collect_children(child)
        
        collect_children(self)
        return TechTree.objects.filter(id__in=all_unlocks) 