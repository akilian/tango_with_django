from django import template
from rango.models import Category

register = template.Library()


@register.inclusion_tag('rango/cats.html')
def get_category_list(cat=None):
    helper_context = {'cats': Category.objects.order_by('-views'), 'act_cat': cat}
    return helper_context
