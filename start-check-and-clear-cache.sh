#!/bin/bash

# Kiểm tra xem Python 3 đã được cài đặt chưa
if command -v python3 &>/dev/null; then
    echo "Python 3 đã được cài đặt."
else
    echo "Chưa có Python 3 cài đặt."
    read -p "Cài đặt Python 3 (Yes/No): " answer

    if [[ "$answer" == "Yes" || "$answer" == "yes" ]]; then
        echo "Đang tiến hành cài đặt Python 3 và pip3..."

        # Cài đặt Homebrew (nếu chưa có)
        if ! command -v brew &>/dev/null; then
            echo "Homebrew chưa được cài đặt, đang cài đặt..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        # Cài đặt Python 3
        brew install python3

        # Kiểm tra và cài đặt pip3 nếu cần thiết
        if ! command -v pip3 &>/dev/null; then
            echo "Cài đặt pip3..."
            python3 -m ensurepip --upgrade
        fi

        # Cài đặt các components cần thiết
        echo "Đang cài đặt các component cần thiết..."
        pip3 install --upgrade setuptools wheel

        echo "Cài đặt hoàn tất!"
        #sleep(5)
        echo " BẮT ĐẦU CHƯƠNG TRÌNH KIỂM TRA THƯ MỤC CACHE ---> "
        curl -s https://raw.githubusercontent.com/MHGtv/Automation/refs/heads/main/check_cache.py | python3

    else
        echo "Chương trình yêu cầu Python 3 để tiếp tục. Vui lòng cài đặt Python 3 để sử dụng."
    fi
fi
