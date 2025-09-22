#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, Response
import qrcode
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# =============================
# CRC16-CCITT (False) cho VietQR
# =============================
def crc16_ccitt(data: str) -> str:
    crc = 0xFFFF
    for c in data:
        crc ^= (ord(c) << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return f"{crc:04X}"


# =============================
# Hàm build EMV field
# =============================
def emv_field(tag: str, value: str) -> str:
    length = f"{len(value):02d}"
    return f"{tag}{length}{value}"


# =============================
# Hàm build VietQR payload
# =============================
def build_vietqr(bankcode, account, amount=None, noidung=None) -> str:
    payload = "000201010212"  # Dynamic QR

    # Merchant account info
    aid = emv_field("00", "A000000727")
    bank = emv_field("00", bankcode)
    acc  = emv_field("01", account)
    nhan_tien = emv_field("01", bank + acc)
    dich_vu = emv_field("02", "QRIBFTTA")  # hoặc QRIBFTTC (qua thẻ)

    merchant = emv_field("38", aid + nhan_tien + dich_vu)

    # Quốc gia & tiền tệ
    currency = emv_field("53", "704")  # VND
    country  = emv_field("58", "VN")

    # Amount nếu có
    amt = ""
    if amount:
        amt = emv_field("54", str(int(amount)))

    # Nội dung nếu có
    desc = ""
    if noidung:
        desc = emv_field("62", emv_field("08", noidung))

    # Ghép chuỗi
    payload = payload + merchant + currency + amt + country + desc

    # Thêm CRC16
    payload_crc = payload + "6304"
    crc = crc16_ccitt(payload_crc)
    return payload_crc + crc


# =============================
# Hàm sinh QR duy nhất
# =============================
def generate_qr(payload,
                template_path=None,
                logo_path=None,
                qr_size=360,
                logo_ratio=0.15):
    """
    Sinh QR code:
      - Chỉ QR (nếu không có template, logo)
      - QR dán vào template (nếu template_path)
      - QR + logo giữa (nếu logo_path)
    """

    # Tạo QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0 if template_path else 4  # nếu có template thì bỏ border
    )
    qr.add_data(payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Resize QR nếu dùng template
    if template_path:
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        template = Image.open(template_path).convert("RGBA")
        tw, th = template.size
        x = (tw - qr_size) // 2
        y = (th - qr_size) // 2
        template.paste(qr_img, (x, y), qr_img)
        base_img = template
    else:
        base_img = qr_img

    # Thêm logo
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        # resize logo theo tỷ lệ QR
        current_qr_size = qr_size if template_path else base_img.size[0]
        logo_size = int(current_qr_size * logo_ratio)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # căn giữa
        bx, by = base_img.size
        lx = (bx - logo_size) // 2
        ly = (by - logo_size) // 2
        base_img.paste(logo, (lx, ly), logo)

    return base_img


# =============================
# Flask route tạo QR
# =============================
@app.route("/vietqr")
def vietqr():
    bankcode = request.args.get("bankcode")
    account  = request.args.get("account")
    amount   = request.args.get("amount")
    noidung  = request.args.get("noidung")
    style    = request.args.get("style")   # "template" hoặc None
    logo     = request.args.get("logo")    # tên file logo, ví dụ "cloudmini.png"
    logo_ratio = float(request.args.get("logo_size", 0.15))  # tỉ lệ logo, mặc định 20%

    if not bankcode or not account:
        return "Thiếu tham số bankcode hoặc account", 400

    payload = build_vietqr(bankcode, account, amount, noidung)

    template_path = "VietQR.png" if style == "template" else None
    logo_path = logo if logo else None

    img = generate_qr(payload,
                      template_path=template_path,
                      logo_path=logo_path,
                      qr_size=360,
                      logo_ratio=logo_ratio)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")


# =============================
# Chạy server Flask
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
