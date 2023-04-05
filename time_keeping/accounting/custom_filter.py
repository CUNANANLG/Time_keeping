from django import template
from datetime import date

register = template.Library()

@register.filter(name='days_between')
def days_between(start_date, end_date):
    delta = end_date - start_date
    return delta.days
