from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import (
    Power, PlayerPower, Experience, PlayerExperience,
    ExperienceInstance, ExperienceParticipation
)
from .serializers import (
    PowerListSerializer, PowerDetailSerializer,
    PlayerPowerSerializer,
    ExperienceListSerializer, ExperienceDetailSerializer,
    PlayerExperienceSerializer,
    ExperienceInstanceListSerializer, ExperienceInstanceDetailSerializer,
    ExperienceParticipationListSerializer, ExperienceParticipationDetailSerializer
)
from core.models import PlayerProfile as Player

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class PowerViewSet(viewsets.ModelViewSet):
    """API endpoint for Power objects"""
    queryset = Power.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PowerListSerializer
        return PowerDetailSerializer
    
    def get_queryset(self):
        queryset = Power.objects.all()
        
        # Filter by power_type if provided
        power_type = self.request.query_params.get('power_type', None)
        if power_type:
            queryset = queryset.filter(power_type=power_type)
            
        # Filter by sector if provided
        sector = self.request.query_params.get('sector', None)
        if sector:
            queryset = queryset.filter(sector=sector)
            
        # Filter by rarity if provided
        rarity = self.request.query_params.get('rarity', None)
        if rarity:
            queryset = queryset.filter(rarity=rarity)
            
        # Filter by public status
        is_public = self.request.query_params.get('is_public', None)
        if is_public is not None:
            is_public = is_public.lower() == 'true'
            queryset = queryset.filter(is_public=is_public)
            
        return queryset


class PlayerPowerViewSet(viewsets.ModelViewSet):
    """API endpoint for PlayerPower objects"""
    queryset = PlayerPower.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlayerPowerSerializer
    
    def get_queryset(self):
        queryset = PlayerPower.objects.all()
        
        # Filter by player if provided
        player_id = self.request.query_params.get('player_id', None)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
            
        # Filter by power if provided
        power_id = self.request.query_params.get('power_id', None)
        if power_id:
            queryset = queryset.filter(power_id=power_id)
            
        # Filter by level if provided
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)
            
        return queryset
    
    def perform_create(self, serializer):
        # Set the player to the current user's player if not specified
        if 'player' not in serializer.validated_data:
            player = get_object_or_404(Player, user=self.request.user)
            serializer.save(player=player)
        else:
            serializer.save()


class ExperienceViewSet(viewsets.ModelViewSet):
    """API endpoint for Experience objects"""
    queryset = Experience.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExperienceListSerializer
        return ExperienceDetailSerializer
    
    def get_queryset(self):
        queryset = Experience.objects.all()
        
        # Filter by experience_type if provided
        experience_type = self.request.query_params.get('experience_type', None)
        if experience_type:
            queryset = queryset.filter(experience_type=experience_type)
            
        # Filter by matrix_position if provided
        matrix_position = self.request.query_params.get('matrix_position', None)
        if matrix_position:
            queryset = queryset.filter(matrix_position=matrix_position)
            
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        # Filter by difficulty range
        min_difficulty = self.request.query_params.get('min_difficulty', None)
        if min_difficulty:
            queryset = queryset.filter(difficulty__gte=min_difficulty)
            
        max_difficulty = self.request.query_params.get('max_difficulty', None)
        if max_difficulty:
            queryset = queryset.filter(difficulty__lte=max_difficulty)
            
        return queryset


class PlayerExperienceViewSet(viewsets.ModelViewSet):
    """API endpoint for PlayerExperience objects"""
    queryset = PlayerExperience.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlayerExperienceSerializer
    
    def get_queryset(self):
        queryset = PlayerExperience.objects.all()
        
        # Filter by player if provided
        player_id = self.request.query_params.get('player_id', None)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
            
        # Filter by experience if provided
        experience_id = self.request.query_params.get('experience_id', None)
        if experience_id:
            queryset = queryset.filter(experience_id=experience_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def perform_create(self, serializer):
        # Set the player to the current user's player if not specified
        if 'player' not in serializer.validated_data:
            player = get_object_or_404(Player, user=self.request.user)
            serializer.save(player=player, started_at=timezone.now())
        else:
            serializer.save(started_at=timezone.now())


class ExperienceInstanceViewSet(viewsets.ModelViewSet):
    """API endpoint for ExperienceInstance objects"""
    queryset = ExperienceInstance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExperienceInstanceListSerializer
        return ExperienceInstanceDetailSerializer
    
    def get_queryset(self):
        queryset = ExperienceInstance.objects.all()
        
        # Filter by host if provided
        host_id = self.request.query_params.get('host_id', None)
        if host_id:
            queryset = queryset.filter(host_id=host_id)
            
        # Filter by experience if provided
        experience_id = self.request.query_params.get('experience_id', None)
        if experience_id:
            queryset = queryset.filter(experience_id=experience_id)
            
        # Filter by zone if provided
        zone_id = self.request.query_params.get('zone_id', None)
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by public status
        is_public = self.request.query_params.get('is_public', None)
        if is_public is not None:
            is_public = is_public.lower() == 'true'
            queryset = queryset.filter(is_public=is_public)
            
        # Filter by start_time range
        start_after = self.request.query_params.get('start_after', None)
        if start_after:
            queryset = queryset.filter(start_time__gte=start_after)
            
        start_before = self.request.query_params.get('start_before', None)
        if start_before:
            queryset = queryset.filter(start_time__lte=start_before)
            
        # Filter active instances
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            if is_active:
                queryset = queryset.filter(
                    status='active',
                    start_time__lte=timezone.now(),
                    end_time__gte=timezone.now()
                )
            
        return queryset
    
    def perform_create(self, serializer):
        # Set the host to the current user's player if not specified
        if 'host' not in serializer.validated_data:
            host = get_object_or_404(Player, user=self.request.user)
            serializer.save(host=host)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """API endpoint to join an experience instance"""
        instance = self.get_object()
        player = get_object_or_404(Player, user=request.user)
        
        # Check if the player is already participating
        existing = ExperienceParticipation.objects.filter(
            instance=instance,
            player=player
        ).first()
        
        if existing:
            if existing.status == 'withdrawn':
                # Rejoin if previously withdrawn
                existing.status = 'joined'
                existing.withdrawn_at = None
                existing.save()
                return Response({
                    'message': 'Successfully rejoined the experience instance',
                    'participation': ExperienceParticipationDetailSerializer(existing).data
                })
            else:
                return Response({
                    'error': 'You are already participating in this experience instance'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the instance is full
        if instance.is_full:
            return Response({
                'error': 'This experience instance is already full'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the instance has started and not accepting new participants
        if instance.status not in ['planned', 'active']:
            return Response({
                'error': 'This experience instance is not accepting new participants'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the participation
        with transaction.atomic():
            participation = ExperienceParticipation.objects.create(
                instance=instance,
                player=player,
                status='joined',
                joined_at=timezone.now()
            )
            
            # Update the current participants count
            instance.current_participants += 1
            instance.save()
        
        return Response({
            'message': 'Successfully joined the experience instance',
            'participation': ExperienceParticipationDetailSerializer(participation).data
        })
    
    @action(detail=True, methods=['post'])
    def advance_phase(self, request, pk=None):
        """API endpoint to advance the matrix phase of an experience instance"""
        instance = self.get_object()
        
        # Check if the user is the host
        if instance.host.user != request.user:
            return Response({
                'error': 'Only the host can advance the matrix phase'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the instance is active
        if instance.status != 'active':
            return Response({
                'error': 'Can only advance phase for active experience instances'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Advance the phase
        instance.advance_matrix_phase()
        
        return Response({
            'message': 'Successfully advanced the matrix phase',
            'current_phase': instance.current_matrix_phase,
            'instance': ExperienceInstanceDetailSerializer(instance).data
        })


class ExperienceParticipationViewSet(viewsets.ModelViewSet):
    """API endpoint for ExperienceParticipation objects"""
    queryset = ExperienceParticipation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExperienceParticipationListSerializer
        return ExperienceParticipationDetailSerializer
    
    def get_queryset(self):
        queryset = ExperienceParticipation.objects.all()
        
        # Filter by player if provided
        player_id = self.request.query_params.get('player_id', None)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
            
        # Filter by instance if provided
        instance_id = self.request.query_params.get('instance_id', None)
        if instance_id:
            queryset = queryset.filter(instance_id=instance_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # If user is not staff, only show their own participations
        if not self.request.user.is_staff:
            player = get_object_or_404(Player, user=self.request.user)
            queryset = queryset.filter(player=player)
            
        return queryset
    
    def perform_create(self, serializer):
        # Set the player to the current user's player if not specified
        if 'player' not in serializer.validated_data:
            player = get_object_or_404(Player, user=self.request.user)
            serializer.save(player=player, joined_at=timezone.now())
        else:
            serializer.save(joined_at=timezone.now())
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """API endpoint to withdraw from an experience instance"""
        participation = self.get_object()
        
        # Check if the user is the participant
        if participation.player.user != request.user:
            return Response({
                'error': 'You can only withdraw yourself from an experience'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already withdrawn
        if participation.status == 'withdrawn':
            return Response({
                'error': 'You have already withdrawn from this experience'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already completed
        if participation.status == 'completed':
            return Response({
                'error': 'Cannot withdraw from a completed experience'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the participation
        with transaction.atomic():
            participation.status = 'withdrawn'
            participation.withdrawn_at = timezone.now()
            participation.save()
            
            # Update the current participants count
            instance = participation.instance
            instance.current_participants -= 1
            instance.save()
        
        return Response({
            'message': 'Successfully withdrawn from the experience instance',
            'participation': ExperienceParticipationDetailSerializer(participation).data
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """API endpoint to mark participation as complete"""
        participation = self.get_object()
        instance = participation.instance
        
        # Check if the user is the host or the participant
        is_host = instance.host.user == request.user
        is_participant = participation.player.user == request.user
        
        if not (is_host or is_participant):
            return Response({
                'error': 'Only the host or the participant can mark completion'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already completed
        if participation.status == 'completed':
            return Response({
                'error': 'This participation is already marked as completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if withdrawn
        if participation.status == 'withdrawn':
            return Response({
                'error': 'Cannot complete a withdrawn participation'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get feedback and satisfaction rating if provided
        feedback = request.data.get('feedback', '')
        satisfaction_rating = request.data.get('satisfaction_rating', None)
        
        # Update the participation
        participation.status = 'completed'
        participation.completed_at = timezone.now()
        
        if feedback:
            participation.feedback = feedback
            
        if satisfaction_rating is not None:
            participation.satisfaction_rating = int(satisfaction_rating)
            
        participation.save()
        
        return Response({
            'message': 'Successfully completed the experience participation',
            'participation': ExperienceParticipationDetailSerializer(participation).data
        }) 