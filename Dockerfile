# 1. Python 3.9 kullan
FROM python:3.9

# 2. Sistemi güncelle ve Chromium için GEREKLİ TÜM kütüphaneleri yükle
# Bu liste, "Unknown Error" hatasını çözen sihirli listedir.
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    --no-install-recommends

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kodları kopyala
COPY . .

# 6. Uygulamayı başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
