from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def percentage_badge(value):
    """Return a colored badge based on percentage value"""
    if value == 100:
        return mark_safe(f'<span class="badge bg-success">{value}%</span>')
    elif value > 100:
        return mark_safe(f'<span class="badge bg-danger">{value}%</span>')
    else:
        return mark_safe(f'<span class="badge bg-warning">{value}%</span>')

@register.filter
def party_color(party):
    """Return color class for party"""
    colors = {
        'APC': 'success',
        'LP': 'danger',
        'PDP': 'primary',
        'AA': 'info',
        'AD': 'warning',
        'ADC': 'secondary'
    }
    return colors.get(party, 'dark')