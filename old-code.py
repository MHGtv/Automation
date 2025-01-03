import os
import shutil
import time
import subprocess

def close_final_cut_pro():
    try:
        # Kiểm tra xem Final Cut Pro có đang chạy không
        result = subprocess.run(["pgrep", "-x", "Final Cut Pro"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            # Nếu ứng dụng đang chạy, tắt nó
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
        # Khởi động lại Final Cut Pro
        subprocess.run(["open", "-a", "Final Cut Pro"], check=True)
        print("Final Cut Pro đã được bật.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi bật Final Cut Pro: {e}")
    except Exception as e:
        print(f"Có lỗi không mong muốn xảy ra: {e}")

def send_notification(title, message):
    """
    Send a macOS notification.
    """
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"'
    ])

def get_folder_size(directory):
    """
    Calculate the total size of a directory in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def clear_cache(directory):
    """
    Deletes all files and folders in the specified directory.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Delete files and symbolic links
                print(f"Deleted file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete directories
                print(f"Deleted folder: {item_path}")
        except Exception as e:
            print(f"Failed to delete '{item_path}': {e}")

def monitor_and_clean(directory, warn_limit, clean_limit):
    """
    Monitor the directory size and take action based on the thresholds.
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    folder_size = get_folder_size(directory)
    folder_size_gb = folder_size / (1024 ** 3)  # Convert to GB

    print(f"Current size of '{directory}': {folder_size_gb:.2f} GB")

    if folder_size > warn_limit:
        warning_message = f"Cảnh Báo: Dung lượng Cache FinalCut đạt đến giới hạn {warn_limit / (1024 ** 3):.2f} GB!"
        print(warning_message)
        send_notification("Folder Size Warning", warning_message)

    if folder_size > clean_limit:
        clean_message = (
            f"Hệ thống tự động dọn dẹp dung lượng {clean_limit / (1024 ** 3):.2f} GB. "
            "Cleaning space folder cache after 30 seconds."
        )
        print(clean_message)
        send_notification("Folder Cache Full", clean_message)
        time.sleep(30)  # Wait for 30 seconds before cleaning
        close_final_cut_pro() #Thoát chương trình Final Cut Pro trước khi xoá cache
        time.sleep(5) # nghỉ 5s để chương trình thoát hoàn toàn
        clear_cache(directory) #xoá toàn bộ cache
        send_notification("Folder Cache Cleaned", "Cache folder has been successfully cleaned!")
        print("Folder cleaned successfully!")
        time.sleep(5) # nghỉ 5s để thao tác xoá hoàn toàn
        open_final_cut_pro() # tự động mở lại chương trình

def create_launchd_job():
    """
    Create the launchd automation job for periodic execution.
    """
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

    # Replace <your_username> with actual macOS username
    username = os.getlogin()
    plist_content = plist_content.replace("<your_username>", username)

    plist_path = f"/Users/{username}/Library/LaunchAgents/com.user.cachemonitor.plist"
    
    # Save the plist content to a file
    with open(plist_path, "w") as plist_file:
        plist_file.write(plist_content)
    
    # Load the job into launchd
    subprocess.run(["launchctl", "load", plist_path])

    print("Automation job created successfully!")

if __name__ == "__main__":
    cache_dir = "/Volumes/Lily/VIDEO/Template/Cache-lib"
    warning_limit = 80 * (1024 ** 3)  # 20 GB in bytes
    cleaning_limit = 81 * (1024 ** 3)  # 50 GB in bytes

    # Run the monitoring and cleaning function
    monitor_and_clean(cache_dir, warning_limit, cleaning_limit)

    # Ask the user if they want to set up automation
#    setup_automation = input("Do you want to automate this task to clean the cache? (Yes/No): ").strip().lower()

 #   if setup_automation == "yes":
  #      create_launchd_job()
   # else:
    #    print("Automation setup skipped.")
