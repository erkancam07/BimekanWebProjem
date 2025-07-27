from django.db import models
from django.utils import timezone
import uuid
import re
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# --- Yatak Modeli ---
class Yatak(models.Model):
    yatak_numarasi = models.CharField(max_length=10, unique=True, verbose_name="Yatak Numarası")
    dolu_mu = models.BooleanField(default=False, verbose_name="Dolu Mu?") 

    def __str__(self):
        return f"Yatak: {self.yatak_numarasi} - {'Dolu' if self.dolu_mu else 'Boş'}"

    class Meta:
        verbose_name = "Yatak"
        verbose_name_plural = "Yataklar"
        ordering = ['yatak_numarasi']

# --- Yeni İşlem Türü Modeli ---
class IslemTuru(models.Model):
    ad = models.CharField(max_length=100, unique=True, verbose_name="İşlem Türü Adı")
    durum_degistirir_mi = models.BooleanField(default=False, verbose_name="Durum Değiştirir Mi?")
    yeni_durum = models.CharField(
        max_length=10,
        choices=[('AKTIF', 'Aktif'), ('PASIF', 'Pasif')],
        blank=True,
        null=True,
        verbose_name="Yeni Durum (Eğer Değiştirirse)"
    )
    yatak_guncelleme_gerektirir_mi = models.BooleanField(default=False, verbose_name="Yatak Güncelleme Gerektirir Mi?")

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "İşlem Türü"
        verbose_name_plural = "İşlem Türleri"
        ordering = ['ad']

# --- Yeni Sosyal Güvence Modeli ---
class SosyalGuvence(models.Model):
    ad = models.CharField(max_length=100, unique=True, verbose_name="Sosyal Güvence Adı")
     
    def save(self, *args, **kwargs):
        self.ad = self.ad.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "Sosyal Güvence"
        verbose_name_plural = "Sosyal Güvenceler"
        ordering = ['ad']

# --- Misafir Modeli (Cari Kart) ---
class Misafir(models.Model):
    DURUM_SECENEKLERI = [
        ('AKTIF', 'Aktif'),
        ('PASIF', 'Pasif'),
    ]
    SOSYAL_GUVENCE_CHOICES = [
        ('SGK', 'SGK'),
        ('BAGKUR', 'Bağkur'),
        ('EMEKLI_SANDIGI', 'Emekli Sandığı'),
        ('YOK', 'Yok'),
        ('DIGER', 'Diğer'),
    ]

    dosya_no = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Dosya No",
        help_text="Kişiye özel benzersiz dosya numarası"
    )
    ad = models.CharField(max_length=100, verbose_name="Adı")
    soyad = models.CharField(max_length=100, verbose_name="Soyadı")
    tc_kimlik_no = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="T.C. Kimlik No",
        help_text="11 haneli T.C. Kimlik Numarası"
    )
    giris_tarihi = models.DateTimeField(
        default=timezone.now,
        verbose_name="Giriş Tarihi"
    )
    cikis_tarihi = models.DateTimeField( # Misafir modeline taşındı
        blank=True,
        null=True,
        verbose_name="Çıkış Tarihi"
    )
    cikis_nedeni = models.TextField( # Misafir modeline taşındı
        verbose_name="Son Çıkış Nedeni", 
        blank=True, 
        null=True,
        help_text="Kişinin en son çıkış yapma nedeni."
    )
    dogum_tarihi = models.DateField(verbose_name="Doğum Tarihi")
    dogum_yeri = models.CharField(max_length=100, verbose_name="Doğum Yeri")
    telefon = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefonu"
    )
    durum = models.CharField(
        max_length=10,
        choices=DURUM_SECENEKLERI,
        default='AKTIF',
        verbose_name="Durum Bilgisi"
    )
    yatak_no = models.ForeignKey(
        Yatak,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Yatak Numarası",
        help_text="Kişinin kaldığı yatak numarası"
    )
    adres = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adresi"
    )
    sosyal_guvence = models.ForeignKey(
        SosyalGuvence,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Sosyal Güvencesi"
    )
    fotograf = models.ImageField(
        upload_to='misafir_fotograflari/',
        blank=True,
        null=True,
        verbose_name="Kişi Fotoğrafı"
    )
    beyan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Kişinin Beyanı",
        help_text="Kişinin kendi beyanı veya önemli notlar"
    )

    # Misafir kaydedildiğinde yatak doluluk durumunu güncelle
    def save(self, *args, **kwargs):
        # Eğer yeni bir kayıt veya yatak numarası değiştiyse
        if self.pk: # Mevcut kayıt
            old_misafir = Misafir.objects.get(pk=self.pk)
            if old_misafir.yatak_no and old_misafir.yatak_no != self.yatak_no:
                # Eski yatağı boşalt
                old_misafir.yatak_no.dolu_mu = False
                old_misafir.yatak_no.save()
        
        # Yeni yatağı doldur
        if self.yatak_no:
            self.yatak_no.dolu_mu = True
            self.yatak_no.save()

        if not self.dosya_no:
            max_numeric_part = 0
            existing_dosya_nos = Misafir.objects.filter(dosya_no__startswith='BMK-').values_list('dosya_no', flat=True)
            for dn in existing_dosya_nos:
                match = re.match(r'BMK-(\d+)', dn)
                if match:
                    numeric_part = int(match.group(1))
                    if numeric_part > max_numeric_part:
                        max_numeric_part = numeric_part
            
            new_number = max_numeric_part + 1
            self.dosya_no = f"BMK-{new_number}"

            # Oluşturulan dosya numarasının hala benzersiz olduğundan emin olmak için kontrol
            while Misafir.objects.filter(dosya_no=self.dosya_no).exists():
                new_number += 1
                self.dosya_no = f"BMK-{new_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.dosya_no})"

    # Ad ve soyadı birleştiren özellik
    @property
    def ad_soyad(self):
        return f"{self.ad} {self.soyad}"
    
    class Meta:
        verbose_name = "Misafir"
        verbose_name_plural = "Misafirler"
        ordering = ['-giris_tarihi']

# Misafir silindiğinde yatağı boşaltmak için sinyal
@receiver(post_delete, sender=Misafir)
def release_bed_on_misafir_delete(sender, instance, **kwargs):
    if instance.yatak_no:
        instance.yatak_no.dolu_mu = False
        instance.yatak_no.save()

class Kurum(models.Model):
    kurum_adi = models.CharField(max_length=255, verbose_name="Kurum Adı")

    def __str__(self):
        return self.kurum_adi
# --- İşlem Modeli ---
class Islem(models.Model):
    misafir = models.ForeignKey(
        Misafir,
        on_delete=models.CASCADE,
        related_name='islemler',
        verbose_name="İlgili Misafir"
    )
    islem_no = models.CharField(
        max_length=35,
        unique=True,
        verbose_name="İşlem Numarası",
        help_text="Otomatik oluşturulan benzersiz işlem numarası"
    )
    islem_turu = models.ForeignKey(
        IslemTuru,
        on_delete=models.PROTECT,
        verbose_name="İşlem Türü"
    )
    islem_zamani = models.DateTimeField(
        auto_now_add=True,
        verbose_name="İşlem Zamanı"
    )
    kurum = models.ForeignKey(
        Kurum, on_delete=models.SET_NULL, null=True, blank=True, related_name="islemler")
    aciklama = models.TextField(
        blank=True,
        null=True,
        verbose_name="İşlem Açıklaması",
        help_text="Yapılan işlemle ilgili detaylı açıklama"
    )
    tutar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Tutar",
        help_text="Yapılan işlemin tutarı"
    )
    # cikis_nedeni ve cikis_tarihi alanları Islem modelinden kaldırıldı, Misafir modeline taşındı.
    # cikis_nedeni = models.CharField(
    #     max_length=255, 
    #     blank=True, 
    #     null=True
    # )
    # cikis_tarihi = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.islem_no:
            max_numeric_part = 0
            # Sadece 'ISLEM-' ile başlayanları filtrele
            existing_islem_nos = Islem.objects.filter(islem_no__startswith='ISLEM-').values_list('islem_no', flat=True)
            for isn in existing_islem_nos:
                match = re.match(r'ISLEM-(\d+)', isn)
                if match:
                    numeric_part = int(match.group(1))
                    if numeric_part > max_numeric_part:
                        max_numeric_part = numeric_part
            
            new_number = max_numeric_part + 1
            self.islem_no = f"ISLEM-{new_number}"

            # Oluşturulan işlem numarasının hala benzersiz olduğundan emin olmak için kontrol
            while Islem.objects.filter(islem_no=self.islem_no).exists():
                new_number += 1
                self.islem_no = f"ISLEM-{new_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.misafir.ad} {self.misafir.soyad} - {self.islem_turu.ad} ({self.islem_zamani.strftime('%d-%m-%Y %H:%M')})"

    class Meta:
        verbose_name = "İşlem"
        verbose_name_plural = "İşlemler"
        ordering = ['-islem_zamani']


class YoklamaDurumu(models.Model):
    ad = models.CharField(max_length=50)

    def __str__(self):
        return self.ad

class YoklamaKaydi(models.Model):
    kisi = models.ForeignKey(Misafir, on_delete=models.CASCADE)
    tarih = models.DateField(default=timezone.now)
    durum = models.ForeignKey(YoklamaDurumu, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.kisi} – {self.tarih} – {self.durum}"


class GiyimUrunu(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Ürün Adı")  # Eşofman, mont vs.
    kategori = models.CharField(max_length=50, choices=[("Üst", "Üst"), ("Alt", "Alt"), ("Ayakkabı", "Ayakkabı")], blank=True)
    mevcut_adet = models.PositiveIntegerField(default=0, verbose_name="Mevcut Stok")
    aciklama = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ad} ({self.mevcut_adet} adet)"

class GiyimIslem(models.Model):
    urun = models.ForeignKey(GiyimUrunu, on_delete=models.CASCADE)
    miktar = models.PositiveIntegerField(default=1)
    alici = models.ForeignKey(Misafir, on_delete=models.CASCADE)
    islem_turu = models.CharField(max_length=10, choices=[("Giriş", "Giriş"), ("Çıkış", "Çıkış")])
    tarih = models.DateTimeField(auto_now_add=True)
    aciklama = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Otomatik stok güncellemesi
        if self.pk is None:  # Yeni kayıt
            if self.islem_turu == "Giriş":
                self.urun.mevcut_adet += self.miktar
            elif self.islem_turu == "Çıkış":
                self.urun.mevcut_adet -= self.miktar
            self.urun.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.islem_turu}: {self.urun.ad} → {self.alici} ({self.miktar} adet)"