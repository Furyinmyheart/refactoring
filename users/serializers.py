
from rest_framework import serializers

from .models import UserComment, MyUser


class UserCommentSerializer(serializers.ModelSerializer):

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if request_user.is_superuser:
            queryset = MyUser.objects.all().prefetch_related('groups')
        elif request_user.has_perm('users.can_crud_all_child'):
            queryset = request_user.get_descendants(include_self=include_self).prefetch_related('groups')
        elif request_user.has_perm('users.can_crud_child'):
            queryset = request_user.get_children().prefetch_related('groups')
        else:
            queryset = MyUser.objects.none()

        self.fields['user'].queryset = queryset

    class Meta:
        model = UserComment
        fields = ('comment', 'user', )
