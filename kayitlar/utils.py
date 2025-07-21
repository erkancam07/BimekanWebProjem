# Bu fonksiyon, T.C. Kimlik Numarası'nın doğruluğunu kontrol eder
def tckn_dogrula(tckn):
    # 1. Uzunluk Kontrolü
    if not tckn.isdigit() or len(tckn) != 11:
        return False, "TCKN 11 haneli sayısal bir değer olmalıdır."

    # 2. İlk Hane Sıfır Olamaz
    if int(tckn[0]) == 0:
        return False, "T.C Kimlik No Geçersiz"

    # Haneleri int'e çevir
    haneler = [int(digit) for digit in tckn]

    # 3. Kural: 10. Hane Kontrolü
    # (1., 3., 5., 7., 9. hanelerin toplamının 7 katı ile 2., 4., 6., 8. hanelerin toplamının 9 katının toplamının birler basamağı 10. haneyi vermeli)
    tek_haneler_toplami = haneler[0] + haneler[2] + haneler[4] + haneler[6] + haneler[8]
    cift_haneler_toplami = haneler[1] + haneler[3] + haneler[5] + haneler[7]

    hesaplanan_onuncu_hane = (tek_haneler_toplami * 7 - cift_haneler_toplami) % 10
    if hesaplanan_onuncu_hane != haneler[9]:
        return False, "T.C Kimlik No Geçersiz"

    # 4. Kural: 11. Hane Kontrolü
    # (İlk 10 hanenin toplamının birler basamağı 11. haneyi vermeli)
    toplam_ilk_on_hane = sum(haneler[:10])
    hesaplanan_onbirinci_hane = toplam_ilk_on_hane % 10
    if hesaplanan_onbirinci_hane != haneler[10]:
        return False, "T.C Kimlik No Geçersiz"
    
    # 5. Kural: 11. Hane Çift Olmalı
    if haneler[10] % 2 != 0:
        return False, "T.C Kimlik No Geçersiz" # "TCKN'nin 11. hanesi çift sayı olmalıdır."


    return True, "TCKN geçerli."


# Örnek Kullanım:
# gecerli_tckn = "10000000146" # Kendi geçerli bir TCKN'nizi buraya yazabilirsiniz.
# print(tckn_dogrula(gecerli_tckn))

# gecersiz_tckn_baslangic = "01234567890"
# print(tckn_dogrula(gecesiz_tckn_baslangic))

# gecersiz_tckn_uzunluk = "12345"
# print(tckn_dogrula(gecesiz_tckn_uzunluk))

# gecersiz_tckn_son_hane = "10000000147" # Son hane tek
# print(tckn_dogrula(gecesiz_tckn_son_hane))
