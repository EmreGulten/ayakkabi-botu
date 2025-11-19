# 1. Python 3.9 tabanlı bir sistem kur
FROM python:3.9

# 2. Chromium ve gerekli sürücüsünü Linux marketinden indir (En sağlam yöntem)
RUN apt-get update && apt-get install -y chromium chromium-driver

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kodları kopyala
COPY . .

# 6. Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
