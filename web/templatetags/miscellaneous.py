from django import template

register = template.Library()


def map(value, arg):
    """
    maps some iterable with complex objects or dictionaries,
    to a simple iterable of the attribute selected of every object
    """
    try:
        return [getattr(e, arg) if hasattr(e, arg) else e[arg] for e in value]
    except Exception as e:
        return ''


register.filter('map', map)
