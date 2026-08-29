# Crypto ETL Project

Pipeline ETL Python lấy dữ liệu thị trường tiền mã hóa từ CoinGecko, làm sạch dữ liệu bằng pandas và lưu snapshot vào PostgreSQL.

## Kiến trúc

```text
CoinGecko API
     |
     v
Extract: app/extract.py
     |  JSON -> pandas DataFrame
     v
Transform: app/transform.py
     |  chọn cột, chuẩn hóa kiểu dữ liệu và timestamp, loại dữ liệu lỗi/trùng
     v
Load: app/load.py
     |  upsert an toàn bằng PostgreSQL ON CONFLICT DO NOTHING
     v
PostgreSQL: crypto.crypto_market_snapshot
```

Điểm khởi chạy là `main.py`, lần lượt gọi `run_extract()`, `clean_crypto_data()` và `load_to_postgres()`. Mỗi lần chạy lấy dữ liệu USD cho Bitcoin, Ethereum, Solana, Ripple và Cardano.

## Yêu cầu

- Python 3.10 trở lên
- PostgreSQL đang chạy và có thể truy cập từ máy chạy pipeline
- Tài khoản CoinGecko Demo API (khuyến nghị để tránh giới hạn API)

## Cài đặt

Tạo virtual environment và cài dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Tạo file cấu hình cục bộ từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Sau đó điền giá trị thực trong `.env`:

```env
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=your_coingecko_demo_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crypto_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

`COINGECKO_API_KEY` có thể để trống nếu API công khai vẫn đáp ứng nhu cầu của bạn. Không commit file `.env`, vì file này chứa secret và đã được đưa vào `.gitignore`.

## Tạo Database

Tạo database PostgreSQL có tên tương ứng với `DB_NAME`, ví dụ `crypto_db`:

```powershell
createdb -U postgres crypto_db
```

Khởi tạo schema, bảng và unique index từ các SQL scripts:

```powershell
psql -U postgres -d crypto_db -f sql/create_schema.sql
psql -U postgres -d crypto_db -f sql/create_table.sql
```

Nếu PostgreSQL không chạy ở `localhost:5432`, cập nhật `DB_HOST` và `DB_PORT` trong `.env`.

## Chạy Pipeline

Từ thư mục gốc project, sau khi activate virtual environment và cấu hình database:

```powershell
python main.py
```

Pipeline sẽ gọi CoinGecko, xử lý dữ liệu và ghi vào `crypto.crypto_market_snapshot`. Khóa duy nhất `(coin_id, source_updated_at)` ngăn cùng một snapshot được chèn lặp lại khi chạy lại pipeline.

Khi CoinGecko trả HTTP `429`, lỗi `5xx`, timeout hoặc lỗi kết nối, Extract sẽ retry tối đa 3 lần với exponential backoff 1, 2 và 4 giây. Các lỗi client khác, như `400` hoặc `401`, được trả về ngay để tránh retry vô ích.

Kiểm tra dữ liệu đã nạp:

```powershell
psql -U postgres -d crypto_db -c "SELECT coin_id, symbol, current_price, source_updated_at, ingested_at FROM crypto.crypto_market_snapshot ORDER BY source_updated_at DESC;"
```

## Chạy Test

Các unit test dùng mock cho API CoinGecko và DataFrame mẫu, vì vậy không cần internet hoặc PostgreSQL:

```powershell
python -m pytest -q
```

## Cấu trúc Thư mục

```text
app/
  extract.py       # Lấy market data từ CoinGecko
  transform.py     # Làm sạch và chuẩn hóa DataFrame
  load.py          # Ghi snapshot vào PostgreSQL
  db.py            # Tạo SQLAlchemy engine từ biến môi trường
main.py            # Orchestrate pipeline ETL
sql/               # Schema và table DDL
test/              # Unit tests cho Extract và Transform
.env.example       # Mẫu biến môi trường không chứa secret
requirements.txt   # Python dependencies
```

## Mô hình Dữ liệu

Bảng `crypto.crypto_market_snapshot` lưu dữ liệu snapshot cho từng đồng coin. Các trường chính gồm định danh (`coin_id`, `symbol`, `coin_name`), giá và chỉ số thị trường (`current_price`, `market_cap`, `total_volume`, high/low 24 giờ), biến động giá 24 giờ, thời điểm nguồn cập nhật (`source_updated_at`) và thời điểm pipeline nạp dữ liệu (`ingested_at`). Hai cột thời gian dùng `TIMESTAMPTZ`, nên PostgreSQL lưu và diễn giải timestamp kèm timezone; pipeline cung cấp chúng ở UTC.
