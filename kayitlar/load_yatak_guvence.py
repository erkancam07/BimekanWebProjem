import pandas as pd
from kayitlar.models import Yatak, SosyalGuvence
# shell terminala yazılacak kod 
# exec(open('kayitlar/load_yatak_guvence.py', encoding='utf-8').read())


# 📄 Excel dosyasını oku
df = pd.read_excel(
    r'C:\Users\erkan\OneDrive\Masaüstü\BimekanWeb2\Bimekan_web\templates\bimekan\bilgiler.xlsx',
    sheet_name='Sayfa1'
)

# 💬 Başlıkları temizlemeden doğrudan kullanıyoruz
# Başlıklar: 'Yataklar', 'Dolu mu', 'Sosyal Güvenceler'

# 🛏️ Yatakları işle
yataklar_df = df[['Yataklar', 'Dolu mu']].dropna(subset=['Yataklar'])
yatak_eklenen = 0

for _, row in yataklar_df.iterrows():
    # 🧼 Yatak numarasını düzenle
    yatak_no = str(row['Yataklar']).replace('.', '-').strip()

    # 🧠 Dolu mu bilgisi - hepsi boşsa varsayılan False
    dolu_mu = False

    # 🛏️ Yatak oluştur/güncelle
    yatak, created = Yatak.objects.get_or_create(yatak_numarasi=yatak_no)
    yatak.dolu_mu = dolu_mu
    yatak.save()

    if created:
        yatak_eklenen += 1

print(f"\n🛏️ Toplam {yatak_eklenen} yeni yatak eklendi.")

# 🛡️ Sosyal Güvenceleri işle
guvenceler_raw = (
    df['Sosyal Güvenceler']
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
    .unique()
    .tolist()
)

guvence_eklenen = 0
for ad in guvenceler_raw:
    _, created = SosyalGuvence.objects.get_or_create(ad=ad)
    if created:
        guvence_eklenen += 1

print(f"🛡️ Toplam {guvence_eklenen} yeni sosyal güvence eklendi.")
