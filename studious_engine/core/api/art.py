from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.http import Http404
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

from core.models import (
    Art, 
    ArtParts, 
    ArtStage, 
    ArtTaxonomy,
    TechTree,
    ArtMastery,
    UserArtStageProgress,
    UserTechTreeProgress,
    PlayerProfile
)

from core.serializers.art.art_serializers import (
    ArtSerializer,
    ArtDetailSerializer,
    ArtPartSerializer,
    ArtStageSerializer,
    ArtTaxonomySerializer,
)

from core.serializers.art.progress_serializers import (
    ArtMasterySerializer,
    UserArtStageProgressSerializer,
    TechTreeSerializer,
    UserTechTreeProgressSerializer,
    PracticeSessionSerializer,
    ValidatePracticeSerializer
)

from core.services.art.art_service import ArtService
from core.services.art.mastery_service import MasteryService
from core.services.art.practice_service import PracticeService
from core.services.art.tech_tree_service import TechTreeService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()


class ArtViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for Arts collection (Pokédex)."""
    queryset = Art.objects.all()
    serializer_class = ArtSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter arts based on query parameters."""
        queryset = Art.objects.all()
        
        # Filter by difficulty level
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            try:
                difficulty_level = int(difficulty)
                queryset = queryset.filter(difficulty_level=difficulty_level)
            except ValueError:
                pass
        
        # Filter by taxonomy
        taxonomy_id = self.request.query_params.get('taxonomy')
        if taxonomy_id:
            queryset = queryset.filter(taxonomy_id=taxonomy_id)
        
        # Filter by economic layer
        economic_layer = self.request.query_params.get('economic_layer')
        if economic_layer:
            queryset = queryset.filter(economic_layer_required=economic_layer)
        
        # Filter by rank
        rank = self.request.query_params.get('rank')
        if rank:
            try:
                rank_level = int(rank)
                queryset = queryset.filter(rank_required__lte=rank_level)
            except ValueError:
                pass
        
        # Check if we should only include available arts for the user
        available_only = self.request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            try:
                profile = PlayerProfile.objects.get(user=self.request.user)
                available_arts = ArtService.get_available_arts(
                    self.request.user,
                    include_unlocked=True,
                    economic_filter=True,
                    rank_filter=True
                )
                queryset = queryset.filter(id__in=[art.id for art in available_arts])
            except PlayerProfile.DoesNotExist:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions."""
        if self.action == 'retrieve':
            return ArtDetailSerializer
        return ArtSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured arts."""
        count = request.query_params.get('count', 6)
        try:
            count = int(count)
        except ValueError:
            count = 6
        
        featured_arts = ArtService.get_featured_arts(limit=count)
        serializer = self.get_serializer(featured_arts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_virtue(self, request):
        """Get arts that improve a specific virtue."""
        virtue = request.query_params.get('virtue')
        if not virtue:
            return Response(
                {"error": "Please specify a virtue parameter."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = request.query_params.get('count', 10)
        try:
            count = int(count)
        except ValueError:
            count = 10
        
        arts = ArtService.get_arts_by_virtue(virtue, limit=count)
        serializer = self.get_serializer(arts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def discover(self, request, pk=None):
        """Discover/start mastering an art."""
        art = self.get_object()
        
        # Check if user has already discovered this art
        existing_mastery = ArtMastery.objects.filter(user=request.user, art=art).first()
        if existing_mastery:
            serializer = ArtMasterySerializer(existing_mastery)
            return Response(serializer.data)
        
        # Discover the art and create mastery record
        mastery = ArtService.discover_art(request.user, art)
        serializer = ArtMasterySerializer(mastery)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArtTaxonomyViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for Art Taxonomy."""
    queryset = ArtTaxonomy.objects.all()
    serializer_class = ArtTaxonomySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter taxonomies based on query parameters."""
        queryset = ArtTaxonomy.objects.all()
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            try:
                level_val = int(level)
                queryset = queryset.filter(level=level_val)
            except ValueError:
                pass
        
        # Filter by parent
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            if parent_id.lower() == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def arts(self, request, pk=None):
        """Get arts in this taxonomy category."""
        taxonomy = self.get_object()
        arts = Art.objects.filter(taxonomy=taxonomy)
        
        # Optional filtering
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            try:
                profile = PlayerProfile.objects.get(user=request.user)
                arts = arts.filter(
                    rank_required__lte=profile.rank,
                    economic_layer_required=profile.economic_layer
                )
            except PlayerProfile.DoesNotExist:
                pass
        
        page = self.paginate_queryset(arts)
        if page is not None:
            serializer = ArtSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ArtSerializer(arts, many=True)
        return Response(serializer.data)


class ArtMasteryViewSet(viewsets.ModelViewSet):
    """API endpoint for user's art mastery."""
    serializer_class = ArtMasterySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get masteries for the current user."""
        return ArtMastery.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Ensure mastery is created for the current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def practice(self, request, pk=None):
        """Log a practice session for this art."""
        mastery = self.get_object()
        serializer = PracticeSessionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if the art_id in the request matches the mastery object
            if str(mastery.art.id) != str(serializer.validated_data['art_id']):
                return Response(
                    {"error": "Art ID in request doesn't match the mastery record."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log practice
            session = PracticeService.log_practice(
                user=request.user,
                art=mastery.art,
                part=serializer.validated_data.get('part_id'),
                duration_minutes=serializer.validated_data.get('duration_minutes', 30),
                notes=serializer.validated_data.get('notes'),
                validated=False
            )
            
            # Re-fetch mastery to get updated data
            mastery.refresh_from_db()
            mastery_serializer = ArtMasterySerializer(mastery)
            return Response({
                'mastery': mastery_serializer.data,
                'session': session
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate practice for this art."""
        mastery = self.get_object()
        serializer = ValidatePracticeSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if the art_id in the request matches the mastery object
            if str(mastery.art.id) != str(serializer.validated_data['art_id']):
                return Response(
                    {"error": "Art ID in request doesn't match the mastery record."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate practice
            practice_data = None
            if 'validator' in serializer.validated_data:
                practice_data = {'validator': serializer.validated_data['validator']}
                
            validated = PracticeService.validate_practice(
                user=request.user,
                art=mastery.art,
                part=serializer.validated_data.get('part_id'),
                practice_data=practice_data
            )
            
            # Re-fetch mastery to get updated data
            mastery.refresh_from_db()
            mastery_serializer = ArtMasterySerializer(mastery)
            return Response({
                'mastery': mastery_serializer.data,
                'validated': validated
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get practice statistics for the user."""
        art_id = request.query_params.get('art_id')
        art = None
        if art_id:
            art = get_object_or_404(Art, id=art_id)
            
        days = request.query_params.get('days', 30)
        try:
            days = int(days)
        except ValueError:
            days = 30
            
        stats = PracticeService.get_practice_stats(
            user=request.user,
            art=art,
            days=days
        )
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of the user's mastery across all arts."""
        summary = MasteryService.get_mastery_summary(request.user)
        return Response(summary)


class TechTreeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for Tech Trees."""
    queryset = TechTree.objects.all()
    serializer_class = TechTreeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tech trees based on query parameters."""
        queryset = TechTree.objects.all()
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            try:
                level_val = int(level)
                queryset = queryset.filter(level=level_val)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get tech trees available to the user."""
        available_trees = TechTreeService.get_available_tech_trees(request.user)
        return Response(available_trees)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get recommended tech trees for the user."""
        count = request.query_params.get('count', 3)
        try:
            count = int(count)
        except ValueError:
            count = 3
            
        recommended = TechTreeService.get_recommended_tech_trees(request.user, count=count)
        return Response(recommended)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get the user's progress for this tech tree."""
        tech_tree = self.get_object()
        progress = TechTreeService.get_user_progress(request.user, tech_tree)
        serializer = UserTechTreeProgressSerializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update the user's progress for this tech tree."""
        tech_tree = self.get_object()
        progress = TechTreeService.update_progress(request.user, tech_tree)
        serializer = UserTechTreeProgressSerializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def prerequisites(self, request, pk=None):
        """Check if the user has met prerequisites for this tech tree."""
        tech_tree = self.get_object()
        prerequisites_met, prerequisites = TechTreeService.check_prerequisites(request.user, tech_tree)
        return Response({
            'prerequisites_met': prerequisites_met,
            'prerequisites': prerequisites
        }) 