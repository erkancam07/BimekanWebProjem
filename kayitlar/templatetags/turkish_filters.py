from django import template

register = template.Library()

@register.filter
def turkish_currency(value):
    try:
        value = float(value)
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " ₺"
    except:
        return "0,00 ₺"