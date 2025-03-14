#!/bin/bash

# Cài đặt môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Thiết lập cơ sở dữ liệu
python manage.py makemigrations
python manage.py migrate


# Chạy ứng dụng
echo "Chạy ứng dụng Django..."
python manage.py runserver