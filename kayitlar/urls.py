# kayitlar/urls.py
from django.urls import path
from . import views
from .views import MisafirGuncelleView, MisafirSilView, IslemSilView, RegisterView # RegisterView'ı import ettik
from .views import (basvuru_formu_cikti_view,acikriza_formu_view, acikriza_soybis_view,)
    

urlpatterns = [
    # Anasayfa: Varsayılan olarak aktif misafirler listesini gösterir
    # path('', views.misafir_listeleri, {'liste_turu': 'aktifler'}, name='anasayfa'), 
    path('', views.misafir_kayit_ve_giris, name='misafir_kayit_giris'),
    # Yeni Misafir Kayıt ve Giriş Formu
    path('misafir/kayit/', views.misafir_kayit_ve_giris, name='misafir_kayit_giris'),
    
    # Misafir Listeleri (Tümü, Aktifler, Pasifler)
    # <str:liste_turu> dinamik olarak 'tumu', 'aktifler' veya 'pasifler' alabilir
    path('misafir/listesi/<str:liste_turu>/', views.misafir_listeleri, name='misafir_listesi'),
    
    # Misafir Detay Sayfası
    # <int:pk> misafirin birincil anahtarını (ID) alır
    path('misafir/<int:pk>/detay/', views.misafir_detay, name='misafir_detay'),
   
    # Misafir İçin Giriş/Çıkış İşlemi Yapma (Belirli bir misafir için)
    path('misafir/<int:pk>/islem/', views.misafir_islem_yap, name='misafir_islem_yap'),
    
    # İşlem Yapmak için kişi seçme sayfası (Arama ile)
    path('misafir/islem/sec/', views.misafir_islem_secim, name='misafir_islem_secim'),

    # Misafir Bilgilerini Düzenleme (Sınıf Tabanlı View)
    path('misafir/<int:pk>/duzenle/', MisafirGuncelleView.as_view(), name='misafir_duzenle'),
    
    # Misafir Kaydını Silme (Sınıf Tabanlı View)
    path('misafir/<int:pk>/sil/', MisafirSilView.as_view(), name='misafir_sil'),

    # Yeni: İşlem Kaydını Silme (Sınıf Tabanlı View)
    path('islem/<int:pk>/sil/', IslemSilView.as_view(), name='islem_sil'),
    
    # İleride eklenecekler için yer tutucular:
    # path('yoklama/', views.yoklama_al, name='yoklama_al'),
    # path('yoklama/listesi/', views.yoklama_listesi, name='yoklama_listesi'),
    path('accounts/register/', RegisterView.as_view(), name='register'), # Kayıt URL'si


    # path('ajax/tc-kontrol/', views.tc_kontrol_view, name='tc_kontrol'),
    path('ajax/tc-kontrol/', views.tc_kontrol_view, name='tc_kontrol'),

    path('gunluk-yoklama/', views.gunluk_yoklama, name='gunluk_yoklama'),
    path('yoklama-listesi/', views.yoklama_listesi, name='yoklama_listesi'),
    
    path('yoklama/<int:id>/duzenle/', views.yoklama_duzenle, name='yoklama_duzenle'),
    path('yoklama/<int:id>/sil/', views.yoklama_sil, name='yoklama_sil'),
    path('yoklama-listesi/ajax/', views.yoklama_ajax, name='yoklama_ajax'),
    # path('yoklama-export/', views.yoklama_export_csv, name='yoklama_export'),  # Dışa aktarım butonu için
    
    path('aylik-analiz/', views.aylik_analiz, name='aylik_analiz'),

    # Yeni: Misafir Listesini Excel'e Aktarma URL'si
    # liste_turu parametresini alarak hangi listenin aktarılacağını belirler
    path('misafir/export/excel/<str:liste_turu>/', views.misafir_export_excel, name='misafir_export_excel'),
    
    # Başvuru Formu Çıktısı
    path('misafir/<int:pk>/basvuru-formu-cikti/', basvuru_formu_cikti_view, name='basvuru_formu_cikti'),

    # Açık Rıza Formu
    path('misafir/<int:pk>/acikriza-formu/', acikriza_formu_view, name='acikriza_formu'),

    # Açık Rıza Soybis Formu
    path('misafir/<int:pk>/acikriza-soybis/', acikriza_soybis_view, name='acikriza_soybis'),

    # Yatak No Ekle ve Liste
    path('yataklar/', views.yatak_ekle, name='yatak_ekle'),
    path('yatak/<int:pk>/sil/', views.yatak_sil, name='yatak_sil'),
    path('yatak/<int:pk>/duzenle/', views.yatak_duzenle, name='yatak_duzenle'),
    # path('yataklar/', views.yatak_listesi, name='yatak_listesi'),  # Bonus listeleme

    path('sosyal-guvence/', views.sosyal_guvence_ekle, name='sosyal_guvence_ekle'),
    path('sosyal-guvence/<int:pk>/sil/', views.sosyal_guvence_sil, name='sosyal_guvence_sil'),

    path("islem-detay/", views.islem_detay, name="islem_detay"),

    path("stok/ekle/", views.stok_ekle, name="stok_ekle"),
    path("stok/rapor/", views.stok_raporu, name="stok_raporu"),  
    path('yardim-gecmisi/<int:urun_id>/', views.yardim_gecmisi, name='yardim_gecmisi'),


]
