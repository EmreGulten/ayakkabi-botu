from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Loglama
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def fiyat_temizle(fiyat_metni):
    try:
        # "1.250,99 TL" -> 1250.99
        temiz = fiyat_metni.replace("TL", "").replace(".", "").replace(",", ".").strip()
        return float(temiz)
    except:
        return 999999.0

@app.get("/")
def ana_sayfa():
    return {"durum": "Aktif", "mod": "Hafif Mod (BeautifulSoup)", "mesaj": "/ara?marka=adidas&beden=42"}

@app.get("/ara")
def ayakkabi_ara(marka: str = "spor", beden: str = "42"):
    sonuclar = []
    arama_terimi = f"{marka} erkek ayakkabı {beden}"
    
    # Trendyol'un bizi engellememesi için gerçek bir tarayıcı gibi kimlik oluşturuyoruz
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/"
    }

    try:
        # Trendyol Arama Linki
        url = f"https://www.trendyol.com/sr?q={arama_terimi}&os=1"
        logger.info(f"İstek atılıyor: {url}")
        
        # Siteye istek at (Selenium yerine Requests kullanıyoruz)
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {"hata": "Trendyol bağlantıyı reddetti.", "kod": response.status_code}

        # Gelen HTML'i parçala
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Ürün kartlarını bul
        urunler = soup.find_all("div", class_="p-card-wrppr")
        
        # İlk 20 ürünü tara
        for urun in urunler[:20]:
            try:
                # Marka ve Model ismini çek
                marka_tag = urun.find("span", class_="prdct-desc-cntnr-ttl")
                model_tag = urun.find("span", class_="prdct-desc-cntnr-name")
                
                if not marka_tag or not model_tag:
                    continue

                # İsimleri birleştir
                marka_text = marka_tag.text if marka_tag else ""
                model_text = model_tag.text if model_tag else ""
                tam_isim = f"{marka_text} {model_text}"
                
                # Linki çek
                link_tag = urun.find("a")
                link = "https://www.trendyol.com" + link_tag["href"]
                
                # --- FİLTRELEME ---
                # Aradığımız beden ürünün isminde veya linkinde geçiyor mu?
                if beden not in tam_isim and beden not in link:
                    continue

                # Fiyatı Çek
                # İndirimli fiyat var mı?
                fiyat_tag = urun.find("div", class_="prc-box-dscntd")
                if not fiyat_tag:
                    # Yoksa normal fiyat
                    fiyat_tag = urun.find("div", class_="prc-box-sllng")
                
                if fiyat_tag:
                    fiyat_text = fiyat_tag.text
                    fiyat_sayi = fiyat_temizle(fiyat_text)
                    
                    sonuclar.append({
                        "isim": tam_isim,
                        "fiyat": fiyat_text,
                        "fiyat_sayi": fiyat_sayi,
                        "link": link
                    })
            except Exception as e:
                continue

    except Exception as e:
        return {"hata": str(e)}

    # Fiyata göre sırala ve en ucuz 5 taneyi al
    sirali_sonuclar = sorted(sonuclar, key=lambda x: x['fiyat_sayi'])
    
    return {
        "aranan_beden": beden,
        "bulunan_toplam": len(sirali_sonuclar),
        "sonuclar": sirali_sonuclar[:5]
    }
