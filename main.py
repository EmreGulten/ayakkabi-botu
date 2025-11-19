from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

app = FastAPI()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ekransız mod (Zorunlu)
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Sunucuda Chrome'u otomatik bulup yönetmesi için:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

@app.get("/")
def ana_sayfa():
    return {"Mesaj": "Ayakkabı botu çalışıyor! Aramak için: /ara?beden=42&kelime=nike"}

@app.get("/ara")
def arama_yap(beden: str, kelime: str):
    driver = get_driver()
    sonuclar = []
    
    try:
        # ÖRNEK: Google'da arama yapıp başlığı çekelim (Demo amaçlı)
        # Sen burayı Trendyol/Amazon linkiyle değiştireceksin.
        url = f"https://www.google.com/search?q={kelime}+ayakkabi+{beden}+numara"
        driver.get(url)
        
        baslik = driver.title
        sonuclar.append({"site_basligi": baslik, "not": "Gerçek veri için siteye özel kod yazılmalı."})
        
    except Exception as e:
        return {"hata": str(e)}
    finally:
        driver.quit() # Tarayıcıyı mutlaka kapat
        
    return {"bulunanlar": sonuclar}