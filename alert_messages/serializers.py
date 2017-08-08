from rest_framework import serializers

from alert_messages.models import Message


class MessageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('is_read', )
