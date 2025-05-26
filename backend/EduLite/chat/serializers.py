from rest_framework import serializers
from .models import ChatRoom, Message  # Use relative import for models
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Messages 
    - Displays sender as a string (username or __str__).
    - Accepts sender as a primary key for write operations.
    """

    # Display sender as a string (username or __str__ of User)
    sender = serializers.StringRelatedField(read_only=True)

    # Accept sender as a primary key for write operations
    sender_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.only('id'),
                                                   source='sender',
                                                   write_only=True,
                                                   required=False
                                                   )

    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'sender_id',
                  'content', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'sender']

    def create(self, validated_data):
        # Use sender from validated_data or context (e.g., request.user)
        if 'sender' not in validated_data and 'request' in self.context:
            validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatRoomSerializer(serializers.ModelSerializer):

    # Show participants as a list of user IDs
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.only('id'))

    # Nested messages (read-only)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'participants',
                  'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages']
