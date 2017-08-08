from rest_framework.generics import CreateAPIView

from .serializers import MessageCreateSerializer


class MessageCreateView(CreateAPIView):
    serializer_class = MessageCreateSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(*args, request_user=self.request.user, context=context, **kwargs)

    def perform_create(self, serializer):
        message = serializer.save()
        message.user_id = self.request.user.pk
        message.save()

