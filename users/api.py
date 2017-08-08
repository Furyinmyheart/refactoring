from django.db import transaction
from rest_framework.generics import CreateAPIView

from .models import UserComment
from .serializers import UserCommentSerializer


class UserCommentCreateView(CreateAPIView):

    serializer_class = UserCommentSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(*args, request_user=self.request.user, context=context, **kwargs)

    @transaction.atomic()
    def perform_create(self, serializer: UserCommentSerializer):
        # remove old comment
        UserComment.objects.filter(author_id=self.request.user.pk, user_id=serializer.validated_data['user']).delete()
        serializer.save(author_id=self.request.user.pk)