import datetime

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter
def format_date(value, empty='-'):
    """Normalise a date string to YYYY/MM/DD; `empty` is shown for blank values
    (use format_date:"" inside form inputs so a placeholder isn't saved as data)."""
    if not value:
        return empty
    value = str(value).strip()
    date_formats = [
        '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%d-%m-%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
    ]
    for fmt in date_formats:
        try:
            dt = datetime.datetime.strptime(value, fmt)
            return dt.strftime('%Y/%m/%d')
        except ValueError:
            continue
    return value
