from rest_framework import serializers
from core.models import MarketItem, Wishlist

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class MarketItemSerializer(serializers.ModelSerializer):
    """Serializer for the MarketItem model."""
    economic_layer_display = serializers.CharField(source='get_economic_layer_display', read_only=True)
    price_type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    seller_type_display = serializers.CharField(source='get_seller_type_display', read_only=True)
    
    class Meta:
        model = MarketItem
        fields = [
            'id', 'name', 'description', 'image', 
            'economic_layer', 'economic_layer_display',
            'price', 'price_type', 'price_type_display',
            'category', 'category_display',
            'is_available', 'quantity', 'available_until',
            'min_rank_required', 'created_at', 'updated_at',
            'is_featured', 'recommendation_score',
            'seller_id', 'seller_type', 'seller_type_display',
            'reference_id'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'economic_layer_display', 'price_type_display',
            'category_display', 'seller_type_display'
        ]

class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for the Wishlist model."""
    item_details = MarketItemSerializer(source='item', read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'item', 'item_details', 'added_at']
        read_only_fields = ['id', 'added_at'] 