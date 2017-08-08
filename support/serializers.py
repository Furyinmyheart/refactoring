from django.db.models import Q
from rest_framework import serializers

from .models import Message, Chat


class MessageCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = Chat.objects.all()
        if request_user.has_perm('support.can_view_all'):
            pass
        elif request_user.has_perm('support.can_view_child'):
            queryset = queryset.filter(Q(to_user_id=request_user.pk) | Q(from_user_id=request_user.pk))
        else:
            queryset = queryset.filter(from_user_id=request_user.pk)

        self.fields['chat'].queryset = queryset

    class Meta:
        model = Message
        fields = ('message', 'chat',)
