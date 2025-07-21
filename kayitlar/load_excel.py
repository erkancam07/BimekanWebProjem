import pandas as pd
from kayitlar.models import Misafir, Yatak, SosyalGuvence, IslemTuru
# shell yükleme kodu
# exec(open('kayitlar/load_excel.py', encoding='utf-8').read())

dosya_yolu = r'C:\Users\erkan\OneDrive\Masaüstü\BimekanWeb2\Bimekan_web\templates\bimekan\bilgiler.xlsx'

try:
    df = pd.read_excel(
        dosya_yolu,
        sheet_name='Veritabani',
        engine='openpyxl',
        parse_dates=['DOĞUM TARİHİ', 'GİRİŞ TARİHİ', 'ÇIKIŞ TARİHİ']
    )
    print("✅ Excel başarıyla yüklendi.")
except Exception as e:
    print(f"❌ Excel yüklenemedi: {e}")
    exit()

basarili = 0
hatali = 0
hatalar = []

for index, row in df.iterrows():
    try:
        dogum_tarihi = row['DOĞUM TARİHİ']
        if pd.isna(dogum_tarihi):
            raise ValueError("Doğum tarihi eksik")

        ad = str(row['ADI']).strip()
        soyad = str(row['SOYAD']).strip()
        tc_kimlik = str(row['T.C. KİMLİK NO']).strip() if not pd.isna(row['T.C. KİMLİK NO']) else ''
        giris_tarihi = row['GİRİŞ TARİHİ'] if not pd.isna(row['GİRİŞ TARİHİ']) else None
        cikis_tarihi = row['ÇIKIŞ TARİHİ'] if not pd.isna(row['ÇIKIŞ TARİHİ']) else None
        dogum_yeri = str(row['DOĞUM YERİ']).strip() if not pd.isna(row['DOĞUM YERİ']) else ''
        telefon = str(row['TELEFONU']).strip() if not pd.isna(row['TELEFONU']) else ''
        adres = str(row['ADRESİ']).strip() if not pd.isna(row['ADRESİ']) else ''
        cikis_nedeni = str(row['ÇIKIŞ NEDENİ']).strip() if not pd.isna(row['ÇIKIŞ NEDENİ']) else ''

        # 🛏️ Yatak
        yatak_no_raw = str(row['YATAK NO']).replace('.', '-').strip()
        yatak, _ = Yatak.objects.get_or_create(yatak_numarasi=yatak_no_raw)

        # 🛡️ Sosyal Güvence
        guvence_adi = row['SOSYA GÜVENCESİ']
        guvence_adi = 'YOK' if pd.isna(guvence_adi) else str(guvence_adi).strip().upper()
        sosyal_guvence, _ = SosyalGuvence.objects.get_or_create(ad=guvence_adi)

        # ⚙️ İşlem Türü
        islem_adi = str(row['İŞLEM TÜRÜ']).strip()
        try:
            islem_turu = IslemTuru.objects.get(ad__iexact=islem_adi)
        except IslemTuru.DoesNotExist:
            islem_turu = None

        # 🎯 Durumu İşlem Türüne göre belirle
        if islem_turu and islem_turu.durum_degistirir_mi and islem_turu.yeni_durum:
            durum = islem_turu.yeni_durum
        else:
            durum_raw = str(row['DURUM']).strip().lower()
            durum = 'AKTİF' if 'aktif' in durum_raw else 'PASİF'

        # 🛏️ Yatak durumu güncellemesi gerekiyorsa
        if islem_turu and islem_turu.yatak_guncelleme_gerektirir_mi:
            yatak.dolu_mu = True
            yatak.save()

        Misafir.objects.create(
            ad=ad,
            soyad=soyad,
            tc_kimlik_no=tc_kimlik,
            dogum_tarihi=dogum_tarihi,
            dogum_yeri=dogum_yeri,
            telefon=telefon,
            durum=durum,
            giris_tarihi=giris_tarihi,
            cikis_tarihi=cikis_tarihi,
            cikis_nedeni=cikis_nedeni,
            adres=adres,
            yatak_no=yatak,
            sosyal_guvence=sosyal_guvence
        )

        basarili += 1

    except Exception as e:
        hatali += 1
        hatalar.append(f"  - Satır {index+2}: {e}")

print(f"\n✅ {basarili} kayıt başarıyla eklendi.")
if hatali:
    print(f"⚠️ {hatali} satırda hata oluştu:")
    for hata in hatalar:
        print(hata)
else:
    print("🎉 Hiç hata yok, tüm kayıtlar başarıyla aktarıldı.")
