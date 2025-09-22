# VietQR Generator API

Dịch vụ web nhỏ viết bằng **Python Flask** để sinh mã QR theo chuẩn **EMVCo VietQR**.  
Hỗ trợ 3 chế độ:
- QR cơ bản
- QR dán vào template nền
- QR với logo ở giữa (tùy chỉnh tỉ lệ)

---

## 🚀 Cài đặt

### 1. Clone / tải mã nguồn
```bash
cd /var/www
git clone https://github.com/minhhungtsbd/vietqr.git
cd vietqr
```

Hoặc copy file `vietqr.py` + ảnh `VietQR.png` (template nền) + logo (ví dụ `cloudmini.png`) vào thư mục `/var/www/vietqr`.

---

### 2. Cài đặt môi trường Python
Khuyến nghị dùng **Python 3.9+**.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài thư viện
```bash
pip install flask qrcode[pil] pillow
```

---

## ⚙️ Chạy thử trực tiếp

```bash
python3 vietqr.py
```

Mặc định Flask chạy ở:
```
http://0.0.0.0:5000
```

---

## 🔗 Tích hợp với Nginx + SSL

Tạo systemd service `/etc/systemd/system/vietqr.service`:

```ini
[Unit]
Description=Gunicorn instance to serve VietQR API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vietqr
ExecStart=/var/www/vietqr/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 vietqr:app

[Install]
WantedBy=multi-user.target
```

Khởi động service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vietqr
sudo systemctl start vietqr
```

Cấu hình Nginx (HTTPS với Certbot):
```nginx
server {
    server_name vietqr.cloudmini.net;

    location / {
        # Chỉ cho phép các IP cụ thể
        allow 127.0.0.1;
        deny all;
		
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/vietqr.cloudmini.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vietqr.cloudmini.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = vietqr.cloudmini.net) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name vietqr.cloudmini.net;
    return 404;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```
---

## 🛠️ API Usage

### Endpoint
```
GET /vietqr
```

### Query Parameters

| Tham số     | Bắt buộc | Mô tả |
|-------------|----------|-------|
| `bankcode`  | ✅       | Mã ngân hàng (6 chữ số, ví dụ: `970436` cho Vietcombank) |
| `account`   | ✅       | Số tài khoản / số thẻ nhận tiền |
| `amount`    | ❌       | Số tiền giao dịch (VNĐ) |
| `noidung`   | ❌       | Nội dung chuyển khoản |
| `style`     | ❌       | `template` nếu muốn dán QR vào nền `VietQR.png` |
| `logo`      | ❌       | Đường dẫn / file logo PNG để dán vào giữa |
| `logo_size` | ❌       | Tỉ lệ logo so với QR (mặc định `0.15` = 15%) |

---

### Ví dụ

1. **QR cơ bản**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789
```

2. **QR có số tiền + nội dung**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan
```

3. **QR dán template nền**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan&style=template
```

4. **QR template + logo Cloudmini**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan&style=template&logo=cloudmini.png
```

5. **QR template + logo nhỏ hơn (10%)**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan&style=template&logo=cloudmini.png&logo_size=0.1
```

---

## 📂 Cấu trúc thư mục

```
/var/www/vietqr/
├── vietqr.py        # Mã nguồn Flask
├── venv/            # Virtualenv Python
├── VietQR.png       # Template nền VietQR
└── cloudmini.png    # Logo Cloudmini
```

---

## 🔒 Bảo mật cơ bản

- Dùng Nginx + Certbot để bắt buộc HTTPS.  
- Rule Nginx chỉ cho phép 1 số IP có thể truy cập để tránh spam.  
- Validate input (đã có trong code).  
- Có thể bổ sung API key nếu cần.  
- Firewal iptables để block all chỉ cho phép 1 số ip có thể truy cập.

---

## 📜 License
Tự do sử dụng trong dự án cá nhân hoặc doanh nghiệp.
