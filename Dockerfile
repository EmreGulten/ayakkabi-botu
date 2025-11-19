# 1. Python sürümü
FROM python:3.9

# 2. Çalışma klasörü
WORKDIR /app

# 3. Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kodları kopyala
COPY . .

# 5. Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
