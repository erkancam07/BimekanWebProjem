from django import template
from django.utils import timezone
from datetime import datetime, date

register = template.Library()

@register.filter
def make_datetime(value):
    """
    Verilen değeri timezone-aware bir datetime objesine dönüştürür.
    """
    # DEBUG: make_datetime filtresine gelen değeri ve tipini yazdır
 

    if isinstance(value, datetime):
        if timezone.is_aware(value):
 
            return value
        else:
            aware_value = timezone.make_aware(value)
            print(f"DEBUG (make_datetime): Value naive datetime, aware yapıldı: {aware_value}")
            return aware_value
    elif isinstance(value, date):
        # Date objesini o günün 00:00:00 olarak datetime objesine çevir ve timezone-aware yap
        dt_obj = timezone.make_aware(datetime.combine(value, datetime.min.time()))
 
        return dt_obj
    elif isinstance(value, str):
        try:
            # Tam datetime formatını dene
            dt_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            aware_dt_obj = timezone.make_aware(dt_obj)
 
            return aware_dt_obj
        except ValueError:
            try:
                # Sadece tarih formatını dene
                dt_obj = datetime.strptime(value, '%Y-%m-%d')
                aware_dt_obj = timezone.make_aware(datetime.combine(dt_obj.date(), datetime.min.time()))
    
                return aware_dt_obj
            except (ValueError, TypeError):
    
                return None
    
    return None


@register.filter
def timesince_short(value, arg):
    """
    Belirtilen iki timezone-aware datetime objesi arasındaki kısa süreyi döndürür.
    """


    # Gelen değerleri make_datetime filtresinden geçirerek timezone-aware datetime objesi olduğundan emin ol
    dt1 = make_datetime(value) # Bu çağrı da kendi debug çıktılarını verecektir.
    dt2 = make_datetime(arg)   # Bu çağrı da kendi debug çıktılarını verecektir.

    
    

    if not dt1 or not dt2:
        
        return "-" # Herhangi biri datetime objesine çevrilemezse "-" dön

    # Tarihlerin doğru sırada olduğundan emin ol (büyükten küçüğe)
    if dt1 < dt2:
        dt1, dt2 = dt2, dt1 # Swap them if dt1 is earlier than dt2
    


    diff = dt1 - dt2
    total_seconds = int(diff.total_seconds())
    days = diff.days

    

    result = ""
    if days > 0:
        if days >= 365:
            years = days // 365
            result = f"{years} yıl"
        elif days >= 30:
            months = days // 30
            result = f"{months} ay"
        else:
            result = f"{days} gün"
    elif total_seconds >= 3600:
        hours = total_seconds // 3600
        result = f"{hours} saat"
    elif total_seconds >= 60:
        minutes = total_seconds // 60
        result = f"{minutes} dakika"
    else:
        result = f"{total_seconds} saniye" if total_seconds > 0 else "birkaç saniye"
    
    
    return result

@register.filter(name='add_class')
def add_class(value, arg):
    # Bu filtre, form alanı widget'ına CSS sınıfı ekler.
    # Bu, widget'ın as_widget() metodunu çağırarak yapılır.
    # attrs sözlüğü, widget'ın HTML niteliklerini belirler.
    return value.as_widget(attrs={'class': arg})