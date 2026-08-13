# Rhamaa App Builder (Manifest → App)

Panduan ini menjelaskan workflow untuk mengembangkan **Rhamaa-Apps** dari file manifest `rhamaa-app.json` menjadi app baru di `apps/<app_name>/` (dibuat oleh user), dengan bantuan AI agent.

## Goal

Ubah manifest (`rhamaa-app.json`) menjadi app nyata di dalam project Django/Wagtail yang dikelola RhamaaCMS/RhamaaCLI:

- Membuat/overwrite `apps/<app_name>/` dengan struktur yang konsisten
- Memastikan `apps/<app_name>/rhamaa-app.json` ada dan valid (sesuai schema)
- Membuat file penting yang dirujuk manifest (paling penting `apps/<app_name>/urls.py`)
- (Opsional) apply manifest ke project saat ini (edit `settings.py` + `urls.py`, buat `apps/<app_name>/urls.py`, jalankan post-install) via pipeline ManifestApplier

Catatan: ini **bukan** workflow untuk download prebuilt registry. Ini fokus ke **local app generation** dari manifest.

## Input yang dibutuhkan

- **Sumber manifest**
  - Path ke `rhamaa-app.json`, atau
  - JSON mentah yang ditempel di chat, atau
  - Permintaan “buatkan manifest untuk app X” (buat default manifest dulu)
- **Nama app** (`app_name`) → target folder `apps/<app_name>/`
- **Scaffold style**
  - `minimal` (Django app)
  - `wagtail` (Wagtail-style: templates/migrations/static)
- **Mode**
  - `generate-only` (hanya generate app files)
  - `apply` (generate + apply manifest ke project)
- **Overwrite**
  - Overwrite hanya jika user memang minta (setara `--force`)

## Constraints penting

- Semua write harus di dalam workspace project (kecuali user minta lain)
- Jangan edit secrets atau `.env`
- Saat apply, asumsi eksekusi dari project root; kalau tidak, deteksi dan beri warning
- Buat workflow idempotent: re-run tidak bikin duplikasi

## Workflow

### 1) Locate & validate manifest

1. Kalau user memberi path, baca file tersebut.
2. Kalau user paste JSON, simpan ke `apps/<app_name>/rhamaa-app.json` (buat folder jika perlu).
3. Validasi minimal (lihat schema di `rhamaa/manifest.py`):
   - `name`, `slug`
   - `urls[*].path` harus berakhir dengan `/`
   - `urls[*].include` wajib ada

Kalau ada yang kurang, normalisasi JSON (pertahankan intent) dan catat perubahan.

### 2) Generate scaffold `apps/<app_name>/`

Buat struktur dasar berikut.

**Selalu ada:**
- `apps/<app_name>/__init__.py`
- `apps/<app_name>/apps.py` (pastikan `name = 'apps.<app_name>'`)
- `apps/<app_name>/urls.py` (minimal punya `urlpatterns = []`)
- `apps/<app_name>/models.py`, `views.py`, `admin.py`, `tests.py`
- `apps/<app_name>/rhamaa-app.json` (hasil normalisasi)

**Jika scaffold `wagtail`:**
- `apps/<app_name>/migrations/__init__.py`
- `apps/<app_name>/templates/<app_name>/`
- `apps/<app_name>/static/<app_name>/`

Gunakan manifest untuk memastikan direktori yang dirujuk benar-benar ada:
- Jika `django.templates.dirs` menyebut folder templates, buat foldernya.
- Jika `staticfiles.dirs` menyebut folder static, buat foldernya.

### 3) Placeholder vs concrete app name

- Default: **biarkan placeholder** (`{app_name}`, `{app_class}`, `{app_upper}`) supaya app bisa dipaketkan jadi prebuilt di kemudian hari.
- Jika user mau app lokal “fixed”, placeholder boleh di-resolve jadi nilai konkret (pastikan sesuai keinginan user).

### 4) (Opsional) Apply manifest ke project

Jika mode `apply`:

- Load manifest dari `apps/<app_name>/rhamaa-app.json`
- Resolve placeholders untuk `app_name`
- Apply settings + urls (pakai pipeline yang ada di `rhamaa/manifest_applier.py`)
- Pastikan `apps/<app_name>/urls.py` ada
- Jalankan post-install tasks jika ada

Jika tidak memungkinkan dipanggil programmatically, buat snippet Python yang bisa dijalankan user dari project root untuk menjalankan `ManifestApplier`.

### 5) Output yang wajib diberikan agent

Selalu keluarkan ringkasan:

- **Created/updated files** (list)
- **Manifest status**: valid / dinormalisasi / field diperbaiki
- **Apply status** (jika apply): perubahan ke settings/urls + command yang dijalankan
- **Next commands** (copy-paste):
  - `python manage.py makemigrations <app_name>`
  - `python manage.py migrate`
  - `python manage.py runserver`

## Contoh prompt user

- “Buat app `devices` dari manifest ini (ini JSON-nya)…”
- “Generate Rhamaa-App dari `apps/foo/rhamaa-app.json` dan apply ke project.”
- “Aku ada prebuilt manifest, tapi mau bikin app lokal dari situ.”

