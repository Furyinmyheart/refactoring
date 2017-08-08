from urllib.parse import urlencode

from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(request, **kwargs):
    query = request.GET.dict()
    query.update(kwargs)
    return urlencode(query)
