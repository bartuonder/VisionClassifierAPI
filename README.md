# Vision Classifier API

Asenkron yapay zeka destekli görüntü sınıflandırma sistemi. FastAPI backend, Celery worker, RabbitMQ mesaj kuyruğu ve Google ViT (Vision Transformer) modeli kullanır.

## Özellikler

- JWT tabanlı kullanıcı kaydı ve girişi
- Görüntü yükleme ve arka planda sınıflandırma (Celery + RabbitMQ)
- **google/vit-base-patch16-224** modeli ile ImageNet sınıflandırması
- Görev durumu sorgulama (pending → processing → completed / failed)
- Modern web arayüzü (`frontend/`)

## Proje Yapısı

```
VisionClassifierAPI/
├── api/              # FastAPI route'ları, auth, şemalar
├── db/               # SQLAlchemy modelleri ve veritabanı
├── ml/               # ViT sınıflandırıcı (lazy load)
├── services/         # Celery worker ve görevler
├── frontend/         # Statik web arayüzü
├── uploads/          # Yüklenen görüntüler
├── main.py           # Uygulama giriş noktası
├── docker-compose.yml
└── requirements.txt
```

## Gereksinimler

- Python 3.10+
- RabbitMQ (Celery broker)
- CUDA destekli GPU 

## Kurulum

### 1. Sanal ortam ve bağımlılıklar

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

> **Not:** `python-jose` kullanılmalıdır; yanlışlıkla `jose` paketi kurulursa kaldırın: `pip uninstall jose`

### 2. Ortam değişkenleri

`.env.example` dosyasını kopyalayın:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux / macOS
```

`.env` içeriği:

| Değişken | Açıklama |
|----------|----------|
| `DATABASE_URL` | SQLite veya PostgreSQL bağlantı dizesi |
| `SECRET_KEY` | JWT imzalama anahtarı |
| `ALGORITHM` | JWT algoritması (örn. `HS256`) |
| `CELERY_BROKER_URL` | RabbitMQ adresi |

### 3. RabbitMQ

Docker ile:

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Yönetim paneli: http://localhost:15672 (guest / guest)

## Çalıştırma

Üç ayrı terminal gerekir:

**Terminal 1 — API sunucusu**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Celery worker**

```bash
celery -A services.celery_config.celery_app worker --loglevel=info
```

**Terminal 3 — (Opsiyonel) RabbitMQ zaten çalışıyorsa gerekmez**

### Web arayüzü

Tarayıcıda açın: **http://localhost:8000**

- Kayıt ol / giriş yap
- Görüntü sürükleyip bırakın veya dosya seçin
- Sonuç otomatik olarak güncellenir

### API dokümantasyonu

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Compose

Tüm servisleri birlikte başlatmak için:

```bash
docker compose up --build
```

> **Not:** `requirements.txt` dosyası UTF-8 olmalıdır. UTF-16 kaydedilirse pip build hatası verir. PyTorch kurulumu Dockerfile içinde ayrı yapılır.

Servisler:

| Servis | Port | Açıklama |
|--------|------|----------|
| `api` | 8000 | FastAPI |
| `worker` | — | Celery worker |
| `rabbitmq` | 5672, 15672 | Mesaj kuyruğu |

## API Özeti

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/auth/signup` | Kullanıcı kaydı | Hayır |
| POST | `/auth/login` | JWT token al | Hayır |
| GET | `/user/me` | Profil bilgisi | Evet |
| PUT | `/user/change_password` | Şifre değiştir | Evet |
| POST | `/classify/` | Görüntü yükle | Evet |
| GET | `/classify/status/{task_id}` | Görev durumu | Evet |

### Örnek: Görüntü sınıflandırma

```bash
# Token al
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=KULLANICI&password=SIFRE"

# Görüntü yükle
curl -X POST http://localhost:8000/classify/ \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@resim.jpg"

# Durum sorgula
curl http://localhost:8000/classify/status/1 \
  -H "Authorization: Bearer TOKEN"
```

