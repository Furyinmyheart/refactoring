from rest_framework.generics import RetrieveUpdateAPIView

from alert_messages.models import Message
from alert_messages.serializers import MessageReadSerializer


class MessageReadView(RetrieveUpdateAPIView):
    serializer_class = MessageReadSerializer

    def get_queryset(self):
        return Message.objects.filter(to_user_id=self.request.user.pk)
