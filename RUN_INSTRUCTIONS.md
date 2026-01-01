# Projeyi Çalıştırma Rehberi

Bu proje iki parçadan oluşur: **Backend (Python/FastAPI)** ve **Frontend (React)**. İkisini aynı anda çalıştırmanız gerekir.

## 1. Hazırlık (Sadece ilk kez)
Eğer paketleri yüklemediyseniz:

**Backend için:**
```bash
cd /Users/edanurunal/film-recommender-backend-1
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend için:**
```bash
cd /Users/edanurunal/film-recommender-backend-1/frontend
npm install
```

---

## 2. Çalıştırma Adımları

Projeyi çalıştırmak için **iki ayrı terminal** penceresi (veya sekmesi) açın.

### Terminal 1: Backend (Sunucu)
Veritabanı ve API'yi çalıştırır.

1.  Doğru klasöre gidin:
    ```bash
    cd /Users/edanurunal/film-recommender-backend-1
    ```
2.  Sanal ortamı aktif edin:
    ```bash
    source venv/bin/activate
    ```
3.  Sunucuyu başlatın:
    ```bash
    uvicorn app.main:app --reload
    ```

*Başarılı olduğunda `INFO: Uvicorn running on http://127.0.0.1:8000` yazısını göreceksiniz.*

### Terminal 2: Frontend (Arayüz)
Web sitesini çalıştırır.

1.  Frontend klasörüne gidin:
    ```bash
    cd /Users/edanurunal/film-recommender-backend-1/frontend
    ```
2.  Uygulamayı başlatın:
    ```bash
    npm start
    ```

*Bu komut otomatik olarak tarayıcınızı açıp `http://localhost:3000` adresine gidecektir.*

---

## Notlar
- **Kapatmak için:** Her iki terminalde de `CTRL+C` tuşlarına basarak işlemi durdurabilirsiniz.
- **Hata alırsanız:** `requirements.txt` dosyasındaki tüm paketlerin `venv` aktifken yüklendiğinden emin olun.
