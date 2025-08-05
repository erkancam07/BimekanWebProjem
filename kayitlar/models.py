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
        # auto_now_add=True,
        default=timezone.now,  # Varsayılan değer olarak şu anki zamanı ayarlayın
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
    # Yeni eklenecek alanlar
    urun = models.ForeignKey(
        'GiyimUrunu',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Verilen Ayni Ürün",
        help_text="Eğer işlem türü 'Ayni Yardım' ise verilen ürün"
    )
    miktar = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Verilen Ayni Miktar",
        help_text="Eğer işlem türü 'Ayni Yardım' ise verilen ürünün miktarı"
    )
    # cikis_nedeni ve cikis_tarihi alanları Misafir modeline taşındı, Islem modelinden kaldırıldı.
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

        # ❗ Önemli: Stok güncelleme mantığı buraya veya bir sinyale taşınacak ❗
        # Bu kısım şimdilik yok, bir sonraki adımda ekleyeceğiz.
        # super().save(*args, **kwargs)

        # Yeni stok güncelleme mantığı (buraya eklendi)
        # Eğer bu bir güncelleme işlemiyse, eski değerleri almamız gerekebilir.
        is_creating = not self.pk # Yeni bir kayıt mı?
        old_islem = None
        if not is_creating:
            try:
                old_islem = Islem.objects.get(pk=self.pk)
            except Islem.DoesNotExist:
                old_islem = None # Obje silinmiş olabilir, devam et

        super().save(*args, **kwargs) # Önce objeyi kaydet ki PK'si olsun.

        # Sadece yeni oluşturulan veya islem_turu değişen işlemleri kontrol et
        if self.islem_turu.ad.lower() == 'ayni yardım':
            if self.urun and self.miktar is not None:
                # Yeni kayıt ise veya ayni ürün/miktar değiştiyse
                if is_creating or \
                   (old_islem and (old_islem.urun != self.urun or old_islem.miktar != self.miktar)):
                    # Önceki ayni işlem varsa, stokları geri ekle
                    if old_islem and old_islem.urun and old_islem.miktar is not None \
                       and old_islem.islem_turu.ad.lower() == 'ayni yardım':
                        old_urun = old_islem.urun
                        old_urun.mevcut_adet += old_islem.miktar
                        old_urun.save()

                    # Yeni/güncellenmiş ayni işlem için stok düşüşü
                    if self.urun.mevcut_adet >= self.miktar:
                        self.urun.mevcut_adet -= self.miktar
                        self.urun.save()
                    else:
                        # Yetersiz stok durumunda hata fırlatma veya loglama
                        # Şu an için basitçe loglayalım veya messages ile kullanıcıya bildirelim
                        print(f"UYARI: Ayni yardım işlemi için yetersiz stok! Ürün: {self.urun.ad}, İstenen: {self.miktar}, Mevcut: {self.urun.mevcut_adet}")
                        # Alternatif olarak ValidationError fırlatılabilir, ancak bu noktada model kaydedilmiş oluyor.
                        # En iyisi formda bu kontrolü yapmak (zaten yapıldı).
                        # Burada sadece bir güvenlik katmanı olarak bırakıyorum.
        # Eğer işlem türü Ayni Yardım değilse ve daha önce Ayni Yardım idiyse stok geri gelsin
        elif old_islem and old_islem.islem_turu.ad.lower() == 'ayni yardım' and old_islem.urun and old_islem.miktar is not None:
            old_urun = old_islem.urun
            old_urun.mevcut_adet += old_islem.miktar
            old_urun.save()


    def __str__(self):
        return f"{self.misafir.ad} {self.misafir.soyad} - {self.islem_turu.ad} ({self.islem_zamani.strftime('%d-%m-%Y %H:%M')})"

    class Meta:
        verbose_name = "İşlem"
        verbose_name_plural = "İşlemler"
        ordering = ['-islem_zamani']

# Misafir silindiğinde veya bir İşlem silindiğinde yatak ve ayni yardım stoklarını güncelleyen sinyaller
@receiver(post_delete, sender=Misafir)
def release_bed_on_misafir_delete(sender, instance, **kwargs):
    if instance.yatak_no:
        instance.yatak_no.dolu_mu = False
        instance.yatak_no.save()

@receiver(post_delete, sender=Islem)
def update_stock_on_islem_delete(sender, instance, **kwargs):
    if instance.islem_turu.ad.lower() == 'ayni yardım' and instance.urun and instance.miktar is not None:
        instance.urun.mevcut_adet += instance.miktar
        instance.urun.save()
        print(f"Stok geri eklendi: {instance.miktar} adet {instance.urun.ad.isim} ({instance.urun.kategori}) - İşlem silindi.")


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

class UrunAdi(models.Model):
    isim = models.CharField(max_length=100, unique=True, verbose_name="Ürün Adı")

    class Meta:
        verbose_name = "Ürün Adı Tanımı"
        verbose_name_plural = "Ürün Adı Tanımları"
        ordering = ['isim'] # İsimlere göre sıralama

    def __str__(self):
        return self.isim

class GiyimUrunu(models.Model):
    ad = models.ForeignKey(UrunAdi, on_delete=models.CASCADE, verbose_name="Ürün Adı")
    kategori = models.CharField(max_length=50, choices=[("Üst", "Üst"), ("Alt", "Alt"), ("Ayakkabı", "Ayakkabı")], blank=True, verbose_name="Kategori")
    mevcut_adet = models.PositiveIntegerField(default=0, verbose_name="Mevcut Stok") # Bu alan toplam mevcut stoğu tutacak
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Giyim Ürünü"
        verbose_name_plural = "Giyim Ürünleri"
        # Bu kısım ÇOK ÖNEMLİ: ad ve kategori kombinasyonu benzersiz olmalı
        unique_together = ('ad', 'kategori')

    def __str__(self):
        return f"{self.ad.isim} ({self.kategori}) - {self.mevcut_adet} adet" # Kategori bilgisini de ekledim

class GiyimIslem(models.Model):
    ISLEM_TURU_SECENEKLERI = [
        ('Giriş', 'Giriş'),
        ('Çıkış', 'Çıkış'), # Bu seçenek artık Kuruma İade için kullanılacak
    ]
    urun = models.ForeignKey(GiyimUrunu, on_delete=models.CASCADE, verbose_name="Ürün")
    miktar = models.PositiveIntegerField(verbose_name="Miktar")
    islem_turu = models.CharField(max_length=10, choices=ISLEM_TURU_SECENEKLERI, verbose_name="İşlem Türü")
    
    # Misafire olan ilişkisi (ayni yardımlar Islem modelinde olduğu için, bu alan GiyimIslem'de "Çıkış" için mantıksızlaşıyor)
    # Ancak eski verilerinizde Misafir'e bağlı GiyimIslem çıkışları varsa silmeyin.
    # Şimdilik dursun, ama formda gizleyeceğiz.
    alici = models.ForeignKey(Misafir, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Alıcı (Misafir)")
    
    # YENİ ALAN: Kuruma yapılan çıkışlar/iadeler için
    kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Alıcı (Kurum)")
    
    kaynak_firma = models.CharField(max_length=100, blank=True, null=True, verbose_name="Giriş Kaynağı/Tedarikçi")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Stok Hareketi"
        verbose_name_plural = "Stok Hareketleri"
        ordering = ['-tarih']

    def __str__(self):
        if self.islem_turu == 'Giriş':
            return f"{self.urun.ad.isim} ({self.urun.kategori}) - {self.miktar} adet Giriş ({self.kaynak_firma or 'Belirtilmemiş'})"
        elif self.islem_turu == 'Çıkış' and self.kurum:
            return f"{self.urun.ad.isim} ({self.urun.kategori}) - {self.miktar} adet Çıkış ({self.kurum.kurum_adi})"
        elif self.islem_turu == 'Çıkış' and self.alici: # Eski çıkışlar için
             return f"{self.urun.ad.isim} ({self.urun.kategori}) - {self.miktar} adet Çıkış ({self.alici.ad} {self.alici.soyad})"
        return f"{self.urun.ad.isim} ({self.urun.kategori}) - {self.miktar} adet {self.get_islem_turu_display()}"

    def save(self, *args, **kwargs):
        old_giyim_islem = None
        if self.pk:
            try:
                old_giyim_islem = GiyimIslem.objects.get(pk=self.pk)
            except GiyimIslem.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Stok güncelleme mantığı
        if old_giyim_islem:
            # Eski miktarı geri al
            if old_giyim_islem.islem_turu == 'Giriş':
                self.urun.mevcut_adet -= old_giyim_islem.miktar
            elif old_giyim_islem.islem_turu == 'Çıkış': # Eski çıkışları da geri al
                 self.urun.mevcut_adet += old_giyim_islem.miktar

        # Yeni işlem türüne göre stok güncellemesi
        if self.islem_turu == 'Giriş':
            self.urun.mevcut_adet += self.miktar
        elif self.islem_turu == 'Çıkış': # GiyimIslem'den yapılan Çıkış işlemi (Kuruma İade)
            self.urun.mevcut_adet -= self.miktar
            # Stokun negatif olmamasını sağlamak isterseniz burada kontrol ekleyebilirsiniz:
            # if self.urun.mevcut_adet < 0:
            #     # Hata fırlat veya 0'a eşitle
            #     self.urun.mevcut_adet = 0
            #     # raise ValidationError("Stok eksiye düşemez.") 

        self.urun.save()
