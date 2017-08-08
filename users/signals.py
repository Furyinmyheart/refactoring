
def reset_limits(sender, instance, **kwargs):
    if instance.pk:
        from users.models import MyUser
        old_user = MyUser.objects.get(pk=instance.pk)

        # only if limit_per_day_changed
        if instance.limit_per_day != old_user.limit_per_day:
            if instance.limit_per_day:
                instance.requests_available = instance.limit_per_day - (old_user.limit_per_day - old_user.requests_available)
                if instance.requests_available < 0:
                    instance.requests_available = 0
            else:
                instance.requests_available = 0
            MyUser.objects.filter(pk=instance.pk).update(requests_available=instance.requests_available)


def archive_handler(sender, instance, **kwargs):
    if instance.is_archive and instance.is_active:
        instance.is_active = False