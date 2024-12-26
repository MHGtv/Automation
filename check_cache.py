import os
import shutil
import time
import subprocess
import requests

def download_script():
    """
    Download the cache_monitor.py script from the specified URL.
    """
    url = "https://raw.githubusercontent.com/MHGtv/Automation/refs/heads/main/cache_monitor.py"
    script_path = os.path.join(f"/Users/{os.getlogin()}", "Scripts", "cache_monitor.py")
    
    try:
        # Download the script content
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Ensure the directory exists
        os.makedirs(os.path.dirname(script_path), exist_ok=True)

        # Save the script to the desired location
        with open(script_path, "wb") as script_file:
            script_file.write(response.content)
        
        print(f"Script downloaded successfully to {script_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading script: {e}")

def close_final_cut_pro():
    try:
        result = subprocess.run(["pgrep", "-x", "Final Cut Pro"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            subprocess.run(["killall", "Final Cut Pro"], check=True)
            print("Final Cut Pro đã được tắt.")
        else:
            print("Final Cut Pro không đang chạy.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi tắt Final Cut Pro: {e}")
    except Exception as e:
        print(f"Có lỗi không mong muốn xảy ra: {e}")

def open_final_cut_pro():
    try:
        subprocess.run(["open", "-a", "Final Cut Pro"], check=True)
        print("Final Cut Pro đã được bật.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi bật Final Cut Pro: {e}")
    except Exception as e:
        print(f"Có lỗi không mong muốn xảy ra: {e}")

def send_notification(title, message):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"'
    ])

def get_folder_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def clear_cache(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"Deleted file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder: {item_path}")
        except Exception as e:
            print(f"Failed to delete '{item_path}': {e}")

def monitor_and_clean(directory, warn_limit, clean_limit):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    folder_size = get_folder_size(directory)
    folder_size_gb = folder_size / (1024 ** 3)

    print(f"Current size of '{directory}': {folder_size_gb:.2f} GB")

    if folder_size > warn_limit:
        warning_message = f"Cảnh Báo: Dung lượng Cache FinalCut đạt đến giới hạn {warn_limit / (1024 ** 3):.2f} GB!"
        print(warning_message)
        send_notification("Folder Size Warning", warning_message)

    if folder_size > clean_limit:
        clean_message = f"Hệ thống tự động dọn dẹp dung lượng {clean_limit / (1024 ** 3):.2f} GB. Cleaning space folder cache after 30 seconds."
        print(clean_message)
        send_notification("Folder Cache Full", clean_message)
        time.sleep(30)
        close_final_cut_pro()
        time.sleep(5)
        clear_cache(directory)
        send_notification("Folder Cache Cleaned", "Cache folder has been successfully cleaned!")
        print("Folder cleaned successfully!")
        time.sleep(5)
        open_final_cut_pro()

def create_launchd_job():
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.user.cachemonitor</string>
        <key>ProgramArguments</key>
        <array>
            <string>/usr/bin/python3</string>
            <string>/Users/<your_username>/Scripts/cache_monitor.py</string>
        </array>
        <key>StartInterval</key>
        <integer>1800</integer>
        <key>KeepAlive</key>
        <true/>
        <key>StandardOutPath</key>
        <string>/Users/<your_username>/Scripts/cache_monitor.log</string>
        <key>StandardErrorPath</key>
        <string>/Users/<your_username>/Scripts/cache_monitor_error.log</string>
    </dict>
    </plist>'''

    username = os.getlogin()
    plist_content = plist_content.replace("<your_username>", username)

    plist_path = f"/Users/{username}/Library/LaunchAgents/com.user.cachemonitor.plist"
    
    with open(plist_path, "w") as plist_file:
        plist_file.write(plist_content)
    
    subprocess.run(["launchctl", "load", plist_path])

    print("Automation job created successfully!")

def get_cache_dir_from_file():
    cache_file_path = "/Users/{}/Scripts/url-cache-dir".format(os.getlogin())
    
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as f:
            cache_dir = f.read().strip()
            if cache_dir:
                return cache_dir
            else:
                print("File is empty. Please provide the cache directory.")
                cache_dir = input("Enter the cache directory path: ").strip()
    
                 # Write the provided cache directory to the file
                with open(cache_file_path, 'w') as f:
                    f.write(cache_dir)
                
                return cache_dir

    else:
        print("url-cache-dir file not found. Please provide the cache directory.")
    
    # Prompt the user for the cache directory
    cache_dir = input("Enter the cache directory path: ").strip()
    
    # Write the provided cache directory to the file
    with open(cache_file_path, 'w') as f:
        f.write(cache_dir)
    
    return cache_dir

if __name__ == "__main__":
    cache_dir = get_cache_dir_from_file()
    warning_limit = 80 * (1024 ** 3)  # 80 GB in bytes
    cleaning_limit = 81 * (1024 ** 3)  # 81 GB in bytes

    monitor_and_clean(cache_dir, warning_limit, cleaning_limit)

    setup_automation = input("Do you want to automate this task to clean the cache? (Yes/No): ").strip().lower()

    if setup_automation == "yes":
        download_script()
        create_launchd_job()
    else:
        print("Automation setup skipped.")
