<div align="center">

# 🖼️ Vision Classifier API

### ⚡ Asenkron, yapay zeka destekli görüntü sınıflandırma platformu

*Bir görsel yükle → arka planda **Google ViT** modeli çalışsın → sonucu canlı izle.*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗%20Transformers-FFD21E?style=for-the-badge&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

## 📸 Ekran Görüntüleri

<div align="center">

### 🔐 Giriş & Kayıt

<img src="screenshots/login.png" width="48%" alt="Giriş ekranı"/>&nbsp;&nbsp;<img src="screenshots/signup.png" width="48%" alt="Kayıt ekranı"/>

### 🎯 Sınıflandırma Sonuçları

<img src="screenshots/car.png" width="80%" alt="Spor araba sınıflandırma sonucu"/>

<br/>

<img src="screenshots/flamingo.png" width="48%" alt="Flamingo sonucu"/>&nbsp;&nbsp;<img src="screenshots/volcano.png" width="48%" alt="Volkan sonucu"/>

</div>

---

## ✨ Proje Hakkında

**Vision Classifier API**, kullanıcıların web arayüzünden görsel yükleyip yapay zeka ile sınıflandırma yapabildiği uçtan uca bir sistemdir. Sınıflandırma işlemi ağır bir AI modeli gerektirdiği için **senkron değil asenkron** çalışır:

> 🧠 API isteği anında cevap verir, görsel bir **kuyruğa** atılır, arka plandaki **worker** modeli çalıştırır ve sonuç hazır olunca arayüz onu **canlı olarak** gösterir.

Bu mimari sayesinde uzun süren AI işlemleri API'yi bloke etmez ve sistem yatay olarak ölçeklenebilir.

### 🚀 Öne Çıkan Özellikler

| | Özellik |
|---|---|
| 🔑 | **JWT tabanlı kimlik doğrulama** — kayıt, giriş ve korumalı uçlar |
| ⚡ | **Asenkron işleme** — Celery + RabbitMQ ile arka plan görev kuyruğu |
| 🧠 | **google/vit-base-patch16-224** — ImageNet üzerinde 1000 sınıflı tahmin |
| 📊 | **Güven skoru** — her tahmin için yüzdelik doğruluk |
| 🔄 | **Canlı durum takibi** — `pending → processing → completed / failed` |
| 🎨 | **Modern web arayüzü** — sürükle-bırak yükleme, otomatik sonuç güncelleme |
| 🐳 | **Tek komutla Docker** — `docker compose up` ile tüm servisler ayakta |
| 🧪 | **Test paketi** — Pytest ile 25 test |

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| 🌐 **Web Framework** | FastAPI + Uvicorn + Starlette |
| 🔐 **Kimlik Doğrulama** | python-jose (JWT), passlib + bcrypt, OAuth2 |
| ✅ **Doğrulama** | Pydantic + email-validator |
| 🗄️ **Veritabanı** | SQLAlchemy (SQLite varsayılan, PostgreSQL destekli) |
| 📨 **Görev Kuyruğu** | Celery + RabbitMQ |
| 🤖 **Yapay Zeka** | PyTorch + Hugging Face Transformers (ViT) + Pillow |
| 🎨 **Arayüz** | Vanilla HTML + CSS + JavaScript |
| 🐳 **Dağıtım** | Docker + Docker Compose |

---

## 🏗️ Nasıl Çalışır?

```
   🧑 Kullanıcı                  ⚙️ FastAPI                 📨 RabbitMQ            🤖 Celery Worker
   ──────────                  ──────────                 ──────────            ─────────────────
       │  1. Görsel yükle          │                          │                        │
       │ ───────────────────────►  │  2. Kaydet + kuyruğa at  │                        │
       │  ◄─── 202 + task_id ────  │ ───────────────────────► │  3. Görevi al ───────► │
       │                           │                          │                        │ 4. ViT ile
       │  5. Durumu sorgula (poll) │                          │                        │    tahmin et
       │ ───────────────────────►  │  ◄──── sonucu DB'ye yaz ─────────────────────────  │
       │  ◄── completed + sonuç ─  │                          │                        │
```

---

## 📁 Proje Yapısı

```
VisionClassifierAPI/
├── 📂 api/                  # FastAPI route'ları, auth ve şemalar
│   ├── auth.py              #   → kayıt & giriş (JWT)
│   ├── deps.py              #   → DB session, JWT, bcrypt bağımlılıkları
│   ├── routes.py            #   → görüntü yükleme & durum sorgulama
│   ├── schemas.py           #   → Pydantic istek/yanıt modelleri
│   └── users.py             #   → profil & şifre değiştirme
├── 📂 db/                   # Veritabanı katmanı
│   ├── database.py          #   → SQLAlchemy engine & session
│   └── models.py            #   → Users & ImageTask modelleri
├── 📂 ml/
│   └── model.py             # 🧠 ViT sınıflandırıcı (lazy singleton)
├── 📂 services/
│   ├── celery_config.py     # ⚙️ Celery app + RabbitMQ broker
│   └── tasks.py             # 📨 Arka plan görüntü işleme görevi
├── 📂 static/               # 🎨 Web arayüzü (HTML/CSS/JS)
├── 📂 tests/                # 🧪 Pytest test paketi
├── 📂 screenshots/          # 📸 Ekran görüntüleri
├── 📂 uploads/              # 📥 Yüklenen görseller (runtime)
├── 🐍 main.py               # Uygulama giriş noktası
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
├── 📄 .env.example
└── 📄 requirements.txt
```

---

## ⚙️ Kurulum

### 1️⃣ Depoyu klonla & sanal ortam oluştur

```bash
git clone <repo-url>
cd VisionClassifierAPI

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 2️⃣ Bağımlılıkları kur

```bash
# PyTorch (CPU sürümü — GPU'n varsa CUDA sürümünü kurabilirsin)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Geri kalan bağımlılıklar
pip install -r requirements.txt
```

### 3️⃣ Ortam değişkenlerini ayarla

`.env.example` dosyasını kopyalayıp `.env` oluştur:

```bash
copy .env.example .env   # Windows
cp .env.example .env      # Linux / macOS
```

> 💡 Tüm değişkenlerin makul varsayılanları vardır; `.env` olmadan da (yerel SQLite + localhost RabbitMQ ile) çalışır.

---

## 🔑 Ortam Değişkenleri

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `DATABASE_URL` | Veritabanı bağlantı dizesi | `sqlite:///./database.db` |
| `SECRET_KEY` | JWT imzalama anahtarı | `uzun-rastgele-bir-anahtar` |
| `ALGORITHM` | JWT algoritması | `HS256` |
| `CELERY_BROKER_URL` | RabbitMQ adresi | `amqp://guest:guest@localhost:5672//` |
| `CORS_ORIGINS` | İzinli origin'ler (virgülle ayrılmış, `*` = tümü) | `*` |

---

## ▶️ Çalıştırma

### 🐳 Seçenek A — Docker (önerilen)

Tek komutla RabbitMQ + API + Worker birlikte ayağa kalkar:

```bash
docker compose up --build
```

| Servis | Port | Açıklama |
|--------|------|----------|
| `api` | `8000` | FastAPI sunucusu |
| `worker` | — | Celery worker |
| `rabbitmq` | `5672`, `15672` | Mesaj kuyruğu + yönetim paneli |

### 💻 Seçenek B — Yerel (3 terminal)

**1. RabbitMQ** (Docker ile)
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

**2. API sunucusu**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**3. Celery worker**
```bash
celery -A services.celery_config.celery_app worker --loglevel=info --pool=solo
```

---

## 🌐 Arayüzü Kullanma

Tarayıcıda aç 👉 **http://localhost:8000**

1. 📝 **Kayıt ol** (şifre 9–20 karakter) ve **giriş yap**
2. 🖼️ Görseli **sürükle-bırak** veya **seç**
3. ⚡ **Sınıflandır** butonuna bas
4. 📊 Sonuç (etiket + güven skoru) **otomatik** olarak ekranda belirir

> 🔧 Geliştiriciler için API dokümanları: **http://localhost:8000/docs** (Swagger) · **http://localhost:8000/redoc**

---

## 📡 API Uçları

| Method | Endpoint | Açıklama | 🔒 Auth |
|:------:|----------|----------|:------:|
| `POST` | `/auth/signup` | Yeni kullanıcı kaydı | ❌ |
| `POST` | `/auth/login` | JWT token al | ❌ |
| `GET` | `/user/me` | Profil bilgisi | ✅ |
| `PUT` | `/user/change_password` | Şifre değiştir | ✅ |
| `POST` | `/classify/` | Görüntü yükle (sınıflandırma başlat) | ✅ |
| `GET` | `/classify/status/{task_id}` | Görev durumu & sonuç | ✅ |
| `GET` | `/health` | Sağlık kontrolü | ❌ |

<details>
<summary>📋 cURL örnekleri</summary>

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

</details>

---

## 🧪 Testler

Test paketi tamamen bellek içinde çalışır (geçici SQLite, Celery taklit edilir, ViT modeli yüklenmez) — yani RabbitMQ veya GPU gerekmez:

```bash
pytest
```

```
======================== 25 passed ✅ ========================
```

Kapsam: kimlik doğrulama · kullanıcı profili · görüntü yükleme/durum uçları · Celery worker mantığı.

---

<div align="center">

Made with 🧠 **FastAPI** · ⚙️ **Celery** · 🤗 **Transformers**

</div>
