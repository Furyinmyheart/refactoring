
def theme(request):

    if request.META.get('HTTP_HOST') == 'tehosm.pro':
        domain_theme = 'coffie'
    else:
        domain_theme = 'blue'
    return {'theme': domain_theme}


def unread_messages(request):
    from support.models import Chat

    return {
        'unread_support_user': Chat.objects.unread_count_user(request.user),
        'unread_support_staff': Chat.objects.unread_count_support(request.user),
    }
