from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from datetime import timedelta
import os
from googletrans import Translator
from pytube import YouTube
import requests

def zaman_formatla(seconds):
    return str(timedelta(seconds=seconds))

def altyazi_dilleri(video_kimlik):
    try:
        altyazi_listesi = YouTubeTranscriptApi.list_transcripts(video_kimlik)
        return altyazi_listesi
    except Exception as hata:
        print(f"Bir hata oluştu: {hata}")
        return None

def altyazi_cek(video_kimlik, dil='en'):
    try:
        altyazi_listesi = YouTubeTranscriptApi.get_transcript(video_kimlik, languages=[dil])
        return altyazi_listesi
    except Exception as hata:
        print(f"Bir hata oluştu: {hata}")
        return None

def altyazi_cevirisi(altyazi_listesi, hedef_dil='tr'):
    translator = Translator()
    cevrilmis_altyazilar = []
    for kayit in altyazi_listesi:
        cevrilmis_metin = translator.translate(kayit['text'], dest=hedef_dil).text
        cevrilmis_altyazilar.append({
            'start': kayit['start'],
            'text': cevrilmis_metin
        })
    return cevrilmis_altyazilar

def video_bilgilerini_al(youtube_link):
    try:
        yt = YouTube(youtube_link)
        video_baslik = yt.title
        video_aciklama = yt.description
        return video_baslik, video_aciklama
    except Exception as hata:
        print(f"Bir hata oluştu: {hata}")
        return None, None

try:
    youtube_link = input("YouTube video linkini girin: ")
    video_kimlik = youtube_link.split('v=')[1]

    altyazi_dil_secenekleri = altyazi_dilleri(video_kimlik)

    if altyazi_dil_secenekleri:
        print("Mevcut Altyazı Dilleri:")
        for altyazi in altyazi_dil_secenekleri:
            print(f"{altyazi.language_code} - {altyazi.language}")

        secilen_dil = input("Hangi dilde altyazı çekmek istersiniz? (varsayılan: en): ").strip() or 'en'
        altyazilar = altyazi_cek(video_kimlik, secilen_dil)

        if altyazilar:
            ceviri_secim = input("Altyazıları çevirmek ister misiniz? (E/H): ").strip().lower()
            if ceviri_secim == 'e':
                hedef_dil = input("Hangi dile çevirmek istersiniz? (varsayılan: tr): ").strip() or 'tr'
                altyazilar = altyazi_cevirisi(altyazilar, hedef_dil)

            altyazi_listesi = []
            for kayit in altyazilar:
                baslangic_zamani = zaman_formatla(kayit['start'])
                metin = kayit['text']
                altyazi_listesi.append(f"{baslangic_zamani} - {metin}")
                print(f"{baslangic_zamani} - {metin}")

            kelime_ara = input("Altyazılarda aramak istediğiniz kelimeyi girin (boş bırakabilirsiniz): ").strip()
            if kelime_ara:
                print(f"'{kelime_ara}' kelimesi için arama sonuçları:")
                for kayit in altyazilar:
                    if kelime_ara.lower() in kayit['text'].lower():
                        baslangic_zamani = zaman_formatla(kayit['start'])
                        print(f"{baslangic_zamani} - {kayit['text']}")

            video_baslik, video_aciklama = video_bilgilerini_al(youtube_link)
            print(f"Video Başlık: {video_baslik}")
            print(f"Video Açıklama: {video_aciklama}")

            kaydet_secim = input("Altyazıları bir txt dosyasına kaydetmek ister misiniz? (E/H): ").strip().lower()

            if kaydet_secim == 'e':
                dosya_adi = f"{video_kimlik}_altyazilar.txt"
                dosya_yolu = os.path.join(os.getcwd(), dosya_adi)

                with open(dosya_yolu, 'w', encoding='utf-8') as dosya:
                    dosya.write("\n".join(altyazi_listesi))

                print(f"Altyazılar '{dosya_yolu}' konumuna kaydedildi.")
except Exception as hata:
    print(f"Bir hata oluştu: {hata}")
