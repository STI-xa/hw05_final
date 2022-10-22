from django.conf import settings
from django.core.paginator import Paginator


def paginator_function(posts, request):
    paginator = Paginator(posts, settings.NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
