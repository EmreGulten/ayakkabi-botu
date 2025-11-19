from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Loglama ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_driver():
    chrome_options = Options()
    # --- Render için Chromium Ayarları ---
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Sistemdeki Chromium'u kullan
    chrome_options.binary_location = "/usr/bin/chromium"

    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Driver hatası: {e}")
        raise e

def fiyat_temizle(fiyat_metni):
    try:
        temiz = fiyat_metni.replace("TL", "").replace(".", "").replace(",", ".").strip()
        return float(temiz)
    except:
        return 999999.0

@app.get("/")
def ana_sayfa():
    return {"durum": "Aktif", "mesaj": "Bot Hazır! Sadece en ucuz 5 ürünü getirir."}

@app.get("/ara")
def ayakkabi_ara(marka: str = "spor", beden: str = "42"):
    driver = None
    sonuclar = []
    arama_terimi = f"{marka} erkek ayakkabı {beden}" 
    
    try:
        driver = get_driver()
        base_url = f"https://www.trendyol.com/sr?q={arama_terimi}&os=1"
        
        logger.info(f"Gidiliyor: {base_url}")
        driver.get(base_url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-card-wrppr")))
        
        urunler = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        
        # İlk 20 ürünü tarıyoruz (elemelerden sonra elimizde en az 5 tane kalsın diye)
        for urun in urunler[:20]:
            try:
                marka_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text
                model_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text
                tam_isim = f"{marka_ismi} {model_ismi}"
                link = urun.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Beden doğrulaması (Başlıkta numara yazmıyorsa pas geç)
                if beden not in tam_isim and beden not in link:
                     continue 

                try:
                    fiyat_element = urun.find_element(By.CLASS_NAME, "prc-box-dscntd")
                except:
                    fiyat_element = urun.find_element(By.CLASS_NAME, "prc-box-sllng")
                
                fiyat_text = fiyat_element.text
                fiyat_sayi = fiyat_temizle(fiyat_text)
                
                sonuclar.append({
                    "isim": tam_isim,
                    "fiyat": fiyat_text,
                    "fiyat_sayi": fiyat_sayi,
                    "link": link
                })
            except Exception:
                continue
                
    except Exception as e:
        logger.error(f"Hata: {e}")
        return {"hata": str(e)}
    finally:
        if driver:
            driver.quit()

    # Önce fiyata göre sırala (En ucuz en üstte)
    sirali_sonuclar = sorted(sonuclar, key=lambda x: x['fiyat_sayi'])
    
    # BURASI DEĞİŞTİ: Listeyi kesip sadece ilk 5 tanesini alıyoruz
    ilk_5_sonuc = sirali_sonuclar[:5]
    
    return {
        "aranan_beden": beden,
        "bulunan_toplam_uygun": len(sirali_sonuclar), # Toplam kaç tane bulduğunu da bilgi olarak verelim
        "gosterilen": len(ilk_5_sonuc),
        "sonuclar": ilk_5_sonuc
    }
