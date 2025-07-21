from django import forms
from django.db.models import Q # Q objesi eklendi
from .models import Misafir, Islem, Yatak, IslemTuru, SosyalGuvence, YoklamaDurumu
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils import tckn_dogrula 

# TCKN için özel bir Django Validator fonksiyonu tanımlıyoruz
def tckn_validator(value):
    gecerli, mesaj = tckn_dogrula(value)
    if not gecerli:
        raise ValidationError(mesaj)

class GunlukYoklamaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kisiler = kwargs.pop('kisiler')
        durumlar = kwargs.pop('durumlar')
        super().__init__(*args, **kwargs)

        for kisi in kisiler:
            self.fields[f'durum_{kisi.id}'] = forms.ModelChoiceField(
                queryset=durumlar,
                label=f"{kisi.ad} {kisi.soyad}",
                required=True,
                widget=forms.Select(attrs={'class': 'form-select'})
            )

class MisafirKayitForm(forms.ModelForm):
    """
    Yeni misafir kaydı için kullanılan form.
    Sosyal Güvence seçenekleri ve yatak listesi dinamik olarak çekilir.
    Giriş tarihi otomatik olarak bugünün tarihiyle dolu gelir.
    """
    class Meta:
        model = Misafir
        fields = [
            'ad', 'soyad', 'tc_kimlik_no', 'dogum_tarihi', 'dogum_yeri',
            'fotograf', 'telefon', 'adres', 'sosyal_guvence', 'yatak_no',
            'giris_tarihi', 'beyan'
        ]
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Adı'
            }),
            'soyad': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Soyadı'
            }),
            'tc_kimlik_no': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'maxlength': '11',
                'placeholder': 'TC Kimlik Numarası'
            }),
            'dogum_tarihi': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'dogum_yeri': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Doğum Yeri'
            }),
            'telefon': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Telefon No'
            }),
            'adres': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Adres'
            }),
            'sosyal_guvence': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'yatak_no': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'required': 'required'
            }),
            'giris_tarihi': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'beyan': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Kişinin beyanı veya önemli notlar...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            now = timezone.localtime(timezone.now())
            self.initial['giris_tarihi'] = now.strftime('%Y-%m-%dT%H:%M')
        else:
            if self.instance.giris_tarihi:
                if timezone.is_aware(self.instance.giris_tarihi):
                    local_dt = timezone.localtime(self.instance.giris_tarihi)
                    self.initial['giris_tarihi'] = local_dt.strftime('%Y-%m-%dT%H:%M')
                else:
                    self.initial['giris_tarihi'] = self.instance.giris_tarihi.strftime('%Y-%m-%dT%H:%M')

            if self.instance.dogum_tarihi:
                self.initial['dogum_tarihi'] = self.instance.dogum_tarihi.strftime('%Y-%m-%d')

        self.fields['sosyal_guvence'].queryset = SosyalGuvence.objects.all().order_by('ad')
        self.fields['sosyal_guvence'].empty_label = "Sosyal Güvence Seçin"

        self.fields['yatak_no'].queryset = Yatak.objects.filter(dolu_mu=False).order_by('yatak_numarasi')
        self.fields['yatak_no'].empty_label = "Boş Yatak Seçin"
        self.fields['yatak_no'].label_from_instance = lambda obj: obj.yatak_numarasi.upper() if hasattr(obj, 'yatak_numarasi') and isinstance(obj.yatak_numarasi, str) else str(obj)

    def clean_yatak_no(self):
        yatak_no = self.cleaned_data.get('yatak_no')
        if not yatak_no:
            raise forms.ValidationError("Lütfen bir yatak numarası seçin.")
        if yatak_no.dolu_mu:
            raise forms.ValidationError(f"Seçtiğiniz yatak ({yatak_no.yatak_numarasi}) şu anda doludur. Lütfen başka bir yatak seçin.")
        return yatak_no

    def clean_tc_kimlik_no(self):
        tc_kimlik_no = self.cleaned_data.get('tc_kimlik_no')
        gecerli, mesaj = tckn_dogrula(tc_kimlik_no)
        if not gecerli:
            raise ValidationError(mesaj)
        if not self.instance.pk:
            if Misafir.objects.filter(tc_kimlik_no=tc_kimlik_no).exists():
                raise ValidationError("Bu TC Kimlik Numarası ile zaten kayıtlı bir misafir bulunmaktadır.")
        return tc_kimlik_no

class MisafirIslemForm(forms.ModelForm):
    giris_tarihi = forms.DateTimeField(
        label='Giriş Tarihi',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-green-600 focus:ring-green-600 p-2 hover:bg-blue-50 focus:outline-none transition-colors duration-200'
        })
        
        
    )

    cikis_tarihi = forms.DateTimeField(
        label='Çıkış Tarihi',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
        })
    )

    cikis_nedeni = forms.CharField(
        label='Çıkış Nedeni',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
            'placeholder': 'Çıkış nedeni'
        })
    )

    class Meta:
        model = Islem
        fields = ['islem_turu', 'tutar', 'aciklama', 'giris_tarihi', 'cikis_tarihi', 'cikis_nedeni', 'kurum']

        widgets = {
            'islem_turu': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'tutar': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': '0.00'
            }),
            'aciklama': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'İşlemle ilgili notlar...'
            }),
            'kurum': forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm p-2 focus:ring-blue-600 focus:border-blue-600 hover:bg-green-50 transition-colors duration-200'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        islem_turu = cleaned_data.get('islem_turu')
        cikis_nedeni = cleaned_data.get('cikis_nedeni')
        cikis_tarihi = cleaned_data.get('cikis_tarihi')

        try:
            cikis_islem_obj = IslemTuru.objects.get(ad__iexact='Çıkış')
            if islem_turu == cikis_islem_obj:
                if not cikis_nedeni:
                    self.add_error('cikis_nedeni', 'Çıkış işlemi için çıkış nedeni zorunludur.')
                if not cikis_tarihi:
                    self.add_error('cikis_tarihi', 'Çıkış işlemi için çıkış tarihi zorunludur.')
        except IslemTuru.DoesNotExist:
            pass

        return cleaned_data

    def clean_giris_tarihi(self):
        giris_tarihi = self.cleaned_data.get('giris_tarihi')
        if giris_tarihi and timezone.is_naive(giris_tarihi):
            return timezone.make_aware(giris_tarihi)
        return giris_tarihi

    def clean_cikis_tarihi(self):
        cikis_tarihi = self.cleaned_data.get('cikis_tarihi')
        if cikis_tarihi and timezone.is_naive(cikis_tarihi):
            return timezone.make_aware(cikis_tarihi)
        return cikis_tarihi

class MisafirGuncelleForm(forms.ModelForm):
    gecici_dosya_yap = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Misafir
        fields = [
            'dosya_no','ad', 'soyad', 'tc_kimlik_no', 'dogum_tarihi', 'dogum_yeri',
            'fotograf', 'telefon', 'adres', 'sosyal_guvence', 'yatak_no',
            'giris_tarihi', 'beyan'
        ]
        widgets = {
            'dosya_no': forms.TextInput(attrs={
                # Mevcut Tailwind CSS sınıflarına 'border-2 border-gray-300' ve diğer genel stilleri ekledik
                'class': 'mt-1 block w-1/2 rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2',
                'placeholder': 'Dosya No',
                'id': 'id_dosya_no', # JavaScript için ID
                'readonly': 'readonly' # Bu satırı ekleyerek alanı salt okunur yapıyoruz
            }),
            'ad': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Adı'
            }),
            'soyad': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Soyadı'
            }),
            'tc_kimlik_no': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'maxlength': '11',
                'placeholder': 'TC Kimlik Numarası'
            }),
            'dogum_tarihi': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'dogum_yeri': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Doğum Yeri'
            }),
            'telefon': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Telefon No'
            }),
            'adres': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Adres'
            }),
            'sosyal_guvence': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'yatak_no': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'giris_tarihi': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200'
            }),
            'beyan': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-blue-600 focus:ring-blue-600 p-2 hover:bg-green-50 focus:ring-green-500 focus:border-green-500 focus:outline-none transition-colors duration-200',
                'placeholder': 'Kişinin beyanı veya önemli notlar...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        dosya_no = cleaned_data.get('dosya_no')
        gecici_dosya_yap = cleaned_data.get('gecici_dosya_yap')

        if dosya_no: # dosya_no alanı doluysa doğrulama yap
            if gecici_dosya_yap:
                # Eğer 'Geçici Dosya Yap' checkbox'ı işaretliyse, dosya_no 'G-' ile başlamalı
                if not dosya_no.startswith('G-'):
                    raise forms.ValidationError("Geçici dosya numarası 'G-' ile başlamalıdır.")
            else:
                # Eğer 'Geçici Dosya Yap' checkbox'ı işaretli değilse, dosya_no 'G-' ile başlamamalı
                # Bu kısım, normal dosya numaralarının 'G-' ile başlamamasını sağlar.
                # Eğer "G- olmayan bir şey de olabilir" derseniz bu 'else' bloğunu kaldırabilirsiniz.
                if dosya_no.startswith('G-'):
                    raise forms.ValidationError("Geçici dosya seçilmediği için dosya numarası 'G-' ile başlayamaz.")
        
        return cleaned_data
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sosyal_guvence'].queryset = SosyalGuvence.objects.all().order_by('ad')
        self.fields['sosyal_guvence'].empty_label = "Sosyal Güvence Seçin"
       
        # Eğer misafir aktifse sadece boş yatakları göster, pasifse tüm yatakları göster (veya mevcut yatağını)
        if self.instance and self.instance.durum == 'AKTIF':
            self.fields['yatak_no'].queryset = Yatak.objects.filter(Q(dolu_mu=False) | Q(pk=self.instance.yatak_no_id)).order_by('yatak_numarasi')
        else:
            # Pasifse veya yeni kayıt ise, sadece mevcut yatağını göster (eğer varsa)
            # veya boş bir queryset. HTML'de disabled olarak gösterildiği için burada çok önemli değil.
            self.fields['yatak_no'].queryset = Yatak.objects.filter(pk=self.instance.yatak_no_id) if self.instance and self.instance.yatak_no else Yatak.objects.none()
            
        self.fields['yatak_no'].empty_label = "Yatak Seçin"
        self.fields['yatak_no'].label_from_instance = lambda obj: obj.yatak_numarasi.upper() if hasattr(obj, 'yatak_numarasi') and isinstance(obj.yatak_numarasi, str) else str(obj)

        if self.instance.giris_tarihi:
            if timezone.is_aware(self.instance.giris_tarihi):
                local_dt = timezone.localtime(self.instance.giris_tarihi)
                self.initial['giris_tarihi'] = local_dt.strftime('%Y-%m-%dT%H:%M')
            else:
                self.initial['giris_tarihi'] = self.instance.giris_tarihi.strftime('%Y-%m-%dT%H:%M')
        
        if self.instance.dogum_tarihi:
            self.initial['dogum_tarihi'] = self.instance.dogum_tarihi.strftime('%Y-%m-%d')

        if self.instance and self.instance.dosya_no:
            # Eğer mevcut dosya_no 'G-' ile başlıyorsa, 'gecici_dosya_yap' checkbox'ını varsayılan olarak işaretli yap.
            if self.instance.dosya_no.startswith('G-'):
                self.fields['gecici_dosya_yap'].initial = True
            # Not: dosya_no'nun kendisi ModelForm tarafından otomatik olarak doldurulacaktır.
            # Dolayısıyla burada dosya_no_prefix/suffix ayrımı yapmaya gerek kalmaz.

    def clean_tc_kimlik_no(self):
        tc_kimlik_no = self.cleaned_data.get('tc_kimlik_no')
        gecerli, mesaj = tckn_dogrula(tc_kimlik_no)
        if not gecerli:
            raise ValidationError(mesaj)
        if Misafir.objects.filter(tc_kimlik_no=tc_kimlik_no).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Bu TC Kimlik Numarası başka bir misafire aittir.")
        return tc_kimlik_no

# Yatak modeli için özel form
class YatakForm(forms.ModelForm):
    class Meta:
        model = Yatak
        fields = '__all__' # Yatak modelinizin tüm alanlarını kullanın
        widgets = {
            'yatak_numarasi': forms.TextInput(attrs={
                'class': 'w-40 rounded-md border-2 border-gray-300 p-2 text-sm',
                'placeholder': 'Yatak Numarası'
            }),
            'dolu_mu': forms.CheckboxInput(attrs={
                'class': 'mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            # Yatak modelinizin diğer alanları için de widget tanımlarını buraya ekleyebilirsiniz.
        }

    def clean_yatak_numarasi(self):
        """
        yatak_numarasi alanına girilen değeri büyük harfe çevirir.
        """
        yatak_numarasi = self.cleaned_data.get('yatak_numarasi')
        if yatak_numarasi:
            return yatak_numarasi.upper()
        return yatak_numarasi

class SosyalGuvenceForm(forms.ModelForm):
    class Meta:
        model = SosyalGuvence
        fields = ['ad']
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'w-64 rounded-md border-2 border-gray-300 p-2 text-sm uppercase',
                'placeholder': 'Sosyal Güvence Türü'
            })
        }