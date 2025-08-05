from django.contrib import admin
from .models import Yatak, IslemTuru, Misafir, Islem, SosyalGuvence,Kurum # SosyalGuvence'yi import ettik
from .models import YoklamaDurumu, YoklamaKaydi,GiyimUrunu, UrunAdi
from .forms import YatakForm # YatakForm'unuzu import edin
from import_export.admin import ImportExportModelAdmin



@admin.register(Kurum)
class KurumAdmin(admin.ModelAdmin):
    list_display = ['kurum_adi']
    search_fields = ['kurum_adi']


# Yatak modelini admin panelinde özelleştirme
@admin.register(Yatak)
class YatakAdmin(admin.ModelAdmin):
    form = YatakForm # Özel YatakForm'umuzu burada belirtiyoruz
    list_display = ('yatak_numarasi', 'dolu_mu') 
    list_filter = ('dolu_mu',)
    search_fields = ('yatak_numarasi',) 

# IslemTuru modelini admin panelinde özelleştirme
@admin.register(IslemTuru)
class IslemTuruAdmin(admin.ModelAdmin):
    list_display = ('ad', 'durum_degistirir_mi', 'yeni_durum')
    search_fields = ('ad',)
    list_filter = ('durum_degistirir_mi', 'yeni_durum')

# SosyalGuvence modelini admin panelinde kaydetme
@admin.register(SosyalGuvence)
class SosyalGuvenceAdmin(admin.ModelAdmin):
    list_display = ('ad',)
    search_fields = ('ad',)

# Misafir modelini admin panelinde özelleştirme
@admin.register(Misafir)
class MisafirAdmin(ImportExportModelAdmin):
    list_display = (
        'dosya_no', 'ad', 'soyad', 'tc_kimlik_no', 'durum', 
        'yatak_no', 'giris_tarihi', 'cikis_tarihi', 
        'cikis_nedeni', # <-- BURAYA EKLENDİ
        'sosyal_guvence'
    )
    search_fields = ('dosya_no', 'ad', 'soyad', 'tc_kimlik_no')
    list_filter = ('durum', 'yatak_no', 'sosyal_guvence')
    readonly_fields = ('dosya_no',)
    fieldsets = (
        ('Kişisel Bilgiler', {
            'fields': ('ad', 'soyad', 'tc_kimlik_no', 'dogum_tarihi', 'dogum_yeri', 'fotograf')
        }),
        ('İletişim Bilgileri', {
            'fields': ('telefon', 'adres', 'sosyal_guvence')
        }),
        ('Konaklama Bilgileri', {
            'fields': ('yatak_no', 'durum', 'giris_tarihi', 'cikis_tarihi', 'cikis_nedeni') # <-- BURAYA EKLENDİ
        }),
        ('Diğer Bilgiler', { 
            'fields': ('beyan',) 
        }),
        ('Sistem Bilgileri', {
            'fields': ('dosya_no',),
            'classes': ('collapse',)
        }),
    )

# Islem modelini admin panelinde özelleştirme
@admin.register(Islem)
class IslemAdmin(admin.ModelAdmin):
    list_display = ('islem_no', 'misafir', 'islem_turu', 'tutar', 'islem_zamani', 'aciklama',"kurum") # 'tutar' eklendi
    search_fields = ('islem_no', 'misafir__ad', 'misafir__soyad', 'islem_turu__ad')
    list_filter = ('islem_turu', 'islem_zamani',"kurum")
    raw_id_fields = ('misafir',)
    readonly_fields = ('islem_no',)
    fieldsets = ( # Yeni fieldsets tanımı eklendi
        (None, {
            'fields': ('misafir', 'islem_turu','islem_zamani', 'tutar', 'aciklama',"kurum") # 'tutar' eklendi
        }),
    )


admin.site.register(YoklamaDurumu)

class YoklamaKaydiAdmin(admin.ModelAdmin):
    list_display = ('kisi', 'tarih', 'durum')
    list_filter = ('tarih', 'durum')
    search_fields = ('kisi__ad', 'kisi__soyad', 'kisi__tc_kimlik_no')
    date_hierarchy = 'tarih'

admin.site.register(YoklamaKaydi, YoklamaKaydiAdmin)

# UrunAdi modelini admin panelinde görünür yapın
@admin.register(UrunAdi)
class UrunAdiAdmin(admin.ModelAdmin):
    search_fields = ['isim'] # UrunAdi listesinde arama yapmayı sağlar

# GiyimUrunu modelini admin panelinde yapılandırın
@admin.register(GiyimUrunu)
class GiyimUrunuAdmin(admin.ModelAdmin):
    # 'ad' alanı için otomatik tamamlama özelliğini etkinleştirir
    autocomplete_fields = ['ad']
    list_display = ('ad', 'kategori', 'mevcut_adet') # Admin listesinde hangi sütunların görüneceğini ayarlar
    list_filter = ('kategori',) # Kategoriye göre filtreleme ekler
    search_fields = ('ad__isim', 'kategori') # Ürün adı ve kategoriye göre arama yapmayı sağlar