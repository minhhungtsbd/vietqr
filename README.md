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

Hoặc copy file `vietqr.py` + thư mục `templates/` (chứa ảnh template và logo) vào `/var/www/vietqr`.

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
pip install flask qrcode[pil] pillow gunicorn
```

Hoặc dùng file `requirements.txt`:
```bash
pip install -r requirements.txt
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
Description=Gunicorn instance to serve vietqr Flask app
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
sudo systemctl status vietqr
```

Xem log real-time:
```bash
journalctl -u vietqr -f
```

Restart service sau khi update code:
```bash
sudo systemctl restart vietqr
```

---

Cấu hình Nginx (HTTPS với Certbot):
```nginx
server {
    server_name vietqr.cloudmini.net;

    location / {
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

---

## 🛠️ API Usage

### Endpoints

#### 1. `/vietqr` - Endpoint đầy đủ tham số (linh hoạt)
```
GET /vietqr
```

#### 2. `/cloudmini` - Endpoint rút gọn (hardcoded defaults)
```
GET /cloudmini?amount=100000&noidung=12392NTCM399033
```
- Tự động dùng: `bankcode=970436`, `account=9909141311`, `template=vcb.png`, `logo=cloudmini.png`
- Chỉ cần truyền: `amount` và `noidung`

---

### Query Parameters (cho `/vietqr`)

| Tham số     | Bắt buộc | Mô tả |
|-------------|----------|-------|
| `bankcode`  | ✅       | Mã ngân hàng (6 chữ số, ví dụ: `970436` cho Vietcombank) |
| `account`   | ✅       | Số tài khoản / số thẻ nhận tiền |
| `amount`    | ❌       | Số tiền giao dịch (VNĐ) |
| `noidung`   | ❌       | Nội dung chuyển khoản |
| `template`  | ❌       | Tên file template (ví dụ: `vcb.png`, `VietQR.png`) trong thư mục `templates/` |
| `style`     | ❌       | `template` nếu muốn dùng `VietQR.png` mặc định |
| `logo`      | ❌       | Tên file logo PNG (ví dụ: `cloudmini.png`) trong thư mục `templates/` |
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
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan&template=vcb.png&logo=cloudmini.png
```

5. **QR template + logo nhỏ hơn (10%)**  
```
https://vietqr.cloudmini.net/vietqr?bankcode=970436&account=123456789&amount=100000&noidung=ThanhToan&template=vcb.png&logo=cloudmini.png&logo_size=0.1
```

6. **Endpoint rút gọn CloudMini (chỉ cần amount + noidung)**  
```
https://vietqr.cloudmini.net/cloudmini?amount=100000&noidung=12392NTCM399033
```

---

## 📂 Cấu trúc thư mục

```
/var/www/vietqr/
├── vietqr.py           # Mã nguồn Flask
├── requirements.txt    # Danh sách thư viện Python
├── README.md           # Tài liệu hướng dẫn
├── venv/               # Virtualenv Python
└── templates/          # Thư mục chứa templates và logo
    ├── VietQR.png      # Template nền VietQR mặc định
    ├── vcb.png         # Template nền VCB
    ├── cloudmini.png   # Logo Cloudmini
    └── favicon.png     # Favicon
```

---

## 🔍 Debug & Troubleshooting

### Kiểm tra service status
```bash
sudo systemctl status vietqr
```

### Xem log realtime
```bash
journalctl -u vietqr -f
```

### Xem 100 dòng log gần nhất
```bash
journalctl -u vietqr -n 100
```

### Restart service sau khi update code
```bash
sudo systemctl restart vietqr
```

### Kiểm tra file templates có tồn tại không
```bash
ls -lah /var/www/vietqr/templates/
```

---

## 🔒 Bảo mật cơ bản

- Dùng Nginx + Certbot để bắt buộc HTTPS.  
- Thêm **rate limiting** trong Nginx hoặc Flask-Limiter để tránh spam.  
- Validate input (đã có trong code).  
- Có thể bổ sung API key nếu cần.  

---

## 📜 License
Tự do sử dụng trong dự án cá nhân hoặc doanh nghiệp.
