# 1. Python yüklü temel bir Linux sürümü seç
FROM python:3.9

# 2. Google Chrome'u Linux'a yükle
RUN apt-get update && apt-get install -y wget gnupg2 unzip
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kodları kopyala
COPY . .

# 6. Uygulamayı başlat (Port 8000'de)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]