import importlib.util
import subprocess
import sys
import os
import re
from pathlib import Path


# =========================================================
# 1️⃣ TỰ ĐỘNG CÀI THƯ VIỆN NẾU THIẾU
# =========================================================
def ensure_package(pkg_name: str):
    """Kiểm tra và cài đặt gói nếu chưa có."""
    if importlib.util.find_spec(pkg_name) is None:
        print("CHƯƠNG TRÌNH ĐANG THIẾU THƯ VIỆN, HỆ THỐNG SẼ TỰ ĐỘNG CÀI ĐẶT \n")
        print(f"📦 Đang cài đặt gói {pkg_name} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        print(f"✅  Đã cài xong {pkg_name}.\n")

# Danh sách thư viện cần thiết
required_packages = ["gdown"]

for pkg in required_packages:
    ensure_package(pkg)

import gdown  # import lại sau khi cài


# =========================================================
# 2️⃣ HÀM HỖ TRỢ
# =========================================================
def get_desktop_path() -> Path:
    """Trả về Desktop (đa nền tảng)."""
    desktop = Path.home() / "Desktop"
    return desktop if desktop.exists() else Path.home()

def ensure_dir(path: Path):
    """Tạo thư mục nếu chưa có."""
    path.mkdir(parents=True, exist_ok=True)

def extract_id(url: str):
    """Xác định loại link (file hoặc folder) và trả về (type, id)."""
    file_match = re.search(r"/file/d/([-\w]{25,})", url)
    folder_match = re.search(r"/folders/([-\w]{25,})", url)
    if file_match:
        return "file", file_match.group(1)
    elif folder_match:
        return "folder", folder_match.group(1)
    else:
        raise ValueError("❌ Không xác định được ID Google Drive trong link.")

#-----
def build_download_url(file_id: str) -> str:
    """Tạo link tải trực tiếp"""
    return f"https://drive.google.com/uc?id={file_id}"

# =========================================================
# 3️⃣ HÀM CHÍNH
# =========================================================
def download_from_drive(url: str) -> list[str]:
    """
    Tải file hoặc toàn bộ folder Google Drive (share công khai).
    Trả về danh sách đường dẫn đã tải.
    """
    base_dir = get_desktop_path() / "VIDEO-DOWNLOAD"
    ensure_dir(base_dir)

    link_type, gid = extract_id(url)
    results = []

    if link_type == "file":
        print(f"🔹 Link chứa: VIDEO FILE id={gid}")
        #download_url = f"https://drive.google.com/uc?id={gid}"
        download_url = build_download_url(gid)
        #output_path = base_dir / f"{gid}.download"
        #gdown.download(download_url, str(output_path), quiet=False)
        output_path = gdown.download(url=download_url, output=None, quiet=False)
        #results.append(str(output_path))
        final_path = os.path.join(base_dir, os.path.basename(output_path))
        os.replace(output_path, final_path)

        print(f"✅  Đã lưu tại: {final_path}\n")
        return final_path
        if not output_path or not os.path.exists(output_path):
            raise FileNotFoundError("Không tải được file hoặc file rỗng.")

    elif link_type == "folder":
        print(f"🔹 Đường dẫn có chứa thư mục: FOLDER id={gid}")
        folder_url = f"https://drive.google.com/drive/folders/{gid}"
        files = gdown.download_folder(folder_url, output=str(base_dir), quiet=False, use_cookies=False)
        results.extend(files)

    print("\n✅ Đã tải xong:")
    for f in results:
        print(" -", f)

    return results


# =========================================================
# 4️⃣ TEST (ENTRY POINT)
# =========================================================
if __name__ == "__main__":
    print("=== Google Drive Downloader by Eric with ChatGPT picode ===\n")
    link = input("🔗 Nhập link Google Drive (file hoặc folder): ").strip()
    if not link:
        print("❌ Không có link nhập vào.")
    else:
        download_from_drive(link)
