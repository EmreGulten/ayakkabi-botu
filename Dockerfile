# 1. Python yüklü temel Linux sürümü
FROM python:3.9

# 2. Gerekli araçları yükle
RUN apt-get update && apt-get install -y wget unzip

# 3. Google Chrome'u en garanti yöntemle (direkt .deb dosyası indirerek) yükle
# Bu yöntem 'apt-key' hatasını atlar.
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# 4. Çalışma klasörünü ayarla
WORKDIR /app

# 5. Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kodları kopyala
COPY . .

# 7. Uygulamayı başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
