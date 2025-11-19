from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_driver():
    chrome_options = Options()
    # Render için kritik ayarlar
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fiyat_temizle(fiyat_metni):
    try:
        temiz = fiyat_metni.replace("TL", "").replace(".", "").replace(",", ".").strip()
        return float(temiz)
    except:
        return 999999.0

@app.get("/")
def ana_sayfa():
    return {"durum": "Aktif", "mesaj": "Akıllı Filtre Devrede! /ara?marka=adidas&beden=43"}

@app.get("/ara")
def ayakkabi_ara(marka: str = "spor", beden: str = "42"):
    driver = None
    sonuclar = []
    # Arama terimini daha spesifik yapıyoruz
    arama_terimi = f"{marka} erkek ayakkabı {beden}" 
    
    try:
        driver = get_driver()
        # Trendyol'un kendi arama motorunu kullanıyoruz (En güvenlisi)
        base_url = f"https://www.trendyol.com/sr?q={arama_terimi}&os=1"
        
        logger.info(f"Gidiliyor: {base_url}")
        driver.get(base_url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-card-wrppr")))
        
        urunler = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        
        for urun in urunler[:20]: # İlk 20 ürüne bak
            try:
                marka_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl").text
                model_ismi = urun.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name").text
                tam_isim = f"{marka_ismi} {model_ismi}"
                
                link = urun.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # --- YENİ ÖZELLİK: BEDEN DOĞRULAMA ---
                # Eğer ürün başlığında aradığımız numara geçmiyorsa listeye ekleme!
                # Örneğin 43 aradık ama sonuçta 43 yazmıyorsa (veya 43.5 ise) bunu atlayabiliriz.
                if beden not in tam_isim and beden not in link:
                     # Bazen başlıkta yazmaz ama linkte yazar, ikisine de baktık.
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

    # Fiyata göre sırala
    sirali_sonuclar = sorted(sonuclar, key=lambda x: x['fiyat_sayi'])
    
    return {
        "aranan_beden": beden,
        "bulunan_sayisi": len(sirali_sonuclar),
        "sonuclar": sirali_sonuclar
    }
