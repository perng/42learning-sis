from django import template

register = template.Library()


@register.simple_tag
def static_path():
  try:
    from sis.site_config import *
    return site_static_path
  except:
    pass
  return ''
