
import tkinter as tk
import requests
import socket
import socks
import winreg
import ctypes
import threading

# آدرس تست
TEST_URL = "https://www.google.com"
PROXY_LIST_URL = "https://www.proxy-list.download/api/v1/get?type=http"

def set_system_proxy(host, port):
    INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(INTERNET_SETTINGS, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")
    winreg.CloseKey(INTERNET_SETTINGS)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

def disable_system_proxy():
    INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(INTERNET_SETTINGS)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

def test_proxy(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get(TEST_URL, proxies=proxies, timeout=5)
        if r.status_code == 200:
            return True
    except:
        return False
    return False

def find_and_set_proxy(status_label):
    status_label.config(text="در حال دریافت لیست پروکسی‌ها...")
    try:
        r = requests.get(PROXY_LIST_URL, timeout=10)
        proxy_list = r.text.strip().split("\r\n")
    except Exception as e:
        status_label.config(text=f"خطا در دریافت لیست: {e}")
        return

    status_label.config(text="در حال تست پروکسی‌ها...")
    for proxy in proxy_list[:50]:  # تست 50 تا اول برای سرعت
        if test_proxy(proxy):
            host, port = proxy.split(":")
            set_system_proxy(host, port)
            status_label.config(text=f"پروکسی فعال شد: {proxy}")
            return

    status_label.config(text="هیچ پروکسی فعالی پیدا نشد.")

def start_search(status_label):
    threading.Thread(target=find_and_set_proxy, args=(status_label,), daemon=True).start()

root = tk.Tk()
root.title("One Button Proxy Finder")
root.geometry("400x200")

status_label = tk.Label(root, text="روی دکمه کلیک کنید.", wraplength=350)
status_label.pack(pady=20)

btn_find = tk.Button(root, text="پیدا کن و ست کن", command=lambda: start_search(status_label))
btn_find.pack(pady=10)

btn_disable = tk.Button(root, text="خاموش کردن پروکسی", command=lambda: disable_system_proxy())
btn_disable.pack(pady=10)

root.mainloop()
