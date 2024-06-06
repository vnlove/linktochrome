import tkinter as tk
from tkinter import ttk
import os
import subprocess
import json
import pyautogui
import time

# Đường dẫn đến tệp tin cấu hình
CONFIG_FILE = "chrome_profiles_config.json"

def get_chrome_profiles():
    chrome_user_data_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data")
    profiles = [name for name in os.listdir(chrome_user_data_dir) if os.path.isdir(os.path.join(chrome_user_data_dir, name))]
    return profiles

def load_profiles_from_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_profiles_to_config(profiles, links, notes):
    data = {"profiles": profiles, "links": links, "notes": notes}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def open_link_on_profile(profile, link):
    if link:
        command = ["C:/Program Files/Google/Chrome/Application/chrome.exe", "--start-fullscreen", f"--profile-directory={profile}", link]
        subprocess.Popen(command, close_fds=True)

def open_links():
    links = entry.get("1.0", tk.END).strip().split('\n')
    selected_profiles = [profile for profile, var, _ in profile_comboboxes if var.get()]
    notes = {profile: note.get() for profile, _, note in profile_comboboxes}
    if selected_profiles:
        for profile, var, _ in profile_comboboxes:
            if var.get():
                for link in links:
                    open_link_on_profile(profile, link)
        save_profiles_to_config(selected_profiles, links, notes)
        status_label.config(text="Đã mở các liên kết thành công!", fg="green")
    else:
        status_label.config(text="Vui lòng chọn ít nhất một profile trước khi mở các liên kết.", fg="red")

def close_all_chrome_windows():
    # Lấy danh sách tiêu đề của tất cả các cửa sổ đang chạy
    window_titles = pyautogui.getAllTitles()

    # Kiểm tra từng tiêu đề
    for title in window_titles:
        # Kiểm tra xem tiêu đề có chứa từ "Google Chrome" không
        if "Google Chrome" in title:
            # Nếu có, tìm cửa sổ bằng tiêu đề
            chrome_window = pyautogui.getWindowsWithTitle(title)[0]
            # Đóng cửa sổ
            chrome_window.close()
            time.sleep(0.5)  # Đợi cửa sổ đóng
    status_label.config(text="Đã đóng tất cả cửa sổ Chrome thành công!", fg="green")

def toggle_select_all():
    all_checked = all(var.get() for _, var, _ in profile_comboboxes)
    if all_checked:
        deselect_all()
        button_toggle_select.config(text="Chọn all")
    else:
        select_all()
        button_toggle_select.config(text="Bỏ all")

def toggle_profile_frame():
    if frame_profiles.winfo_ismapped():
        frame_profiles.pack_forget()
        button_toggle_profiles.config(text="List Profile")
    else:
        frame_profiles.pack()
        button_toggle_profiles.config(text="Ẩn")

root = tk.Tk()
root.title("OPEN ALL LINK")

# Nhãn và Ô nhập liên kết cùng với nút "Mở liên kết"
frame_link = tk.Frame(root)
frame_link.pack(side='top')

label_link = tk.Label(frame_link, text="Danh sách link:")
label_link.pack(side='top')

entry = tk.Text(frame_link, width=50, height=4)
entry.pack(side='left')

button_open = tk.Button(frame_link, text="OPEN", command=open_links,  bg="lightblue")
button_open.pack(side='left', padx=(0, 5))

button_close = tk.Button(frame_link, text="CLOSE", command=close_all_chrome_windows, bg="red")
button_close.pack(side='left')

# Khung chọn profile
frame_profiles = tk.Frame(root)

# Đưa Nút "Chọn tất cả" lên trên đầu
button_toggle_select = tk.Button(frame_profiles, text="Chọn all", command=toggle_select_all)
button_toggle_select.pack(side='top')

def deselect_all():
    for _, var, _ in profile_comboboxes:
        var.set(False)

def select_all():
    for _, var, _ in profile_comboboxes:
        var.set(True)


# Load các profile đã được chọn từ tệp tin cấu hình
config_data = load_profiles_from_config()
if isinstance(config_data, dict):
    selected_profiles = config_data.get("profiles", [])
    saved_links = config_data.get("links", [])
    saved_notes = config_data.get("notes", {})
else:
    selected_profiles = []
    saved_links = []
    saved_notes = {}

profile_comboboxes = []  # Định nghĩa biến toàn cục profile_comboboxes

for profile in get_chrome_profiles():
    profile_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", profile)
    if os.path.exists(os.path.join(profile_path, "Preferences")):
        var = tk.BooleanVar()
        if profile in selected_profiles:
            var.set(True)
        else:
            var.set(False)
        combobox = ttk.Checkbutton(frame_profiles, text=f"{profile}: ", variable=var)
        combobox.pack(side='top')

        note = tk.Entry(frame_profiles, width=30)
        if profile in saved_notes:
            note.insert(tk.END, saved_notes[profile])
        note.pack(side='top')

        profile_comboboxes.append((profile, var, note))  # Thêm vào danh sách profile_comboboxes

# Tạo nút để hiện hoặc ẩn khung chọn profile
button_toggle_profiles = tk.Button(root, text="Hiện list profile", command=toggle_profile_frame)
button_toggle_profiles.pack(side='top')

# Tạo Label để hiển thị thông báo
status_label = tk.Label(root, text="", fg="green")
status_label.pack(side='bottom', fill='x')

# Tự động điền danh sách liên kết từ lần sử dụng trước
if saved_links:
    entry.insert(tk.END, "\n".join(saved_links))

root.mainloop()
