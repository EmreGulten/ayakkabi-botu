from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Loglama ayarı (Hata olursa terminalde nedenini görmek için)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_driver():
    chrome_options = Options()
    # --- KRİTİK AYARLAR (Render'da Çökmemesi İçin) ---
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") # En önemli ayar bu! (Bellek sorununu çözer)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Driver oluşturulurken hata: {e}")
        raise e

def fiyat_temizle(fiyat_metni):
    try:
        temiz = fiyat_metni.replace("TL", "").replace(".", "").replace(",", ".").strip()
        return float(temiz)
    except:
        return 999999.0

@app.get("/")
def ana_sayfa():
    return {"durum": "Aktif", "mesaj": "Bot Hazır. Yeni kod yuklendi! /ara?marka=nike&beden=42"}

@app.get("/ara")
def ayakkabi_ara(marka: str = "spor", beden: str = "42"):
    driver = None
    sonuclar = []
    arama_terimi = f"{marka} ayakkabı {beden} numara"
    
    try:
        driver = get_driver()
        base_url = f"https://www.trendyol.com/sr?q={arama_terimi}&os=1"
        
        logger.info(f"Gidiliyor: {base_url}")
        driver.get(base_url)
        
        # Sayfanın yüklenmesini bekle
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-card-wrppr")))
        
        urunler = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        
        for urun in urunler[:10]: # Hız için ilk 10 ürün
            try:
                marka_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text
                model_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text
                link = urun.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                try:
                    fiyat_element = urun.find_element(By.CLASS_NAME, "prc-box-dscntd")
                except:
                    fiyat_element = urun.find_element(By.CLASS_NAME, "prc-box-sllng")
                
                fiyat_text = fiyat_element.text
                fiyat_sayi = fiyat_temizle(fiyat_text)
                
                sonuclar.append({
                    "isim": f"{marka_ismi} {model_ismi}",
                    "fiyat": fiyat_text,
                    "fiyat_sayi": fiyat_sayi,
                    "link": link
                })
            except Exception:
                continue
                
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
        return {"hata": str(e), "detay": "Server loglarına bakınız."}
    finally:
        if driver:
            driver.quit()

    sirali_sonuclar = sorted(sonuclar, key=lambda x: x['fiyat_sayi'])
    
    return {
        "aranan": arama_terimi,
        "sonuclar": sirali_sonuclar
    }
