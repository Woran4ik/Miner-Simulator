import os
import sys
import subprocess
import urllib.request
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Настройки проекта
REPO_OWNER = "Woran4ik"
REPO_NAME = "Miner-Simulator"
CURRENT_VERSION = "0.2.0"

# Исправленный путь к version.txt с учетом папки "Miner Simulator"
VERSION_FILE_URL = f"https://raw.githubusercontent.com/Woran4ik/Miner-Simulator/main/version.txt"
GITHUB_API_URL = f"https://api.github.com/repos/Woran4ik/Miner-Simulator/releases/latest"
SETUP_FILENAME = "MinerSimulator_Setup.exe"

# Перехват версии из аргументов запуска
if "--version" in sys.argv:
    try:
        idx = sys.argv.index("--version")
        CURRENT_VERSION = sys.argv[idx + 1].strip().lstrip("v")
    except (IndexError, ValueError):
        pass

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обновление Miner Simulator")
        self.root.geometry("400x150")
        self.root.resizable(False, False)

        # Фоновый режим: окно изначально скрыто
        self.root.withdraw()

        # Центрирование
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w // 2) - 200
        y = (screen_h // 2) - 75
        self.root.geometry(f"400x150+{x}+{y}")

        self.label = ttk.Label(root, text="Загрузка обновления...", font=("Arial", 10))
        self.label.pack(pady=15)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=320, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = ttk.Label(root, text="", font=("Arial", 8))
        self.status_label.pack(pady=5)

        # Фоновая проверка
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def parse_remote_version(self, text):
        """ Извлекает чистую версию, даже если в файле написано version=1.3.1 """
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                if key.strip().lower() in ("version", "ver"):
                    return val.strip().lstrip("v")
            else:
                return line.lstrip("v")
        return ""

    def check_for_updates(self):
        try:
            # 1. Читаем версию из version.txt
            req_ver = urllib.request.Request(VERSION_FILE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_ver, timeout=5) as resp_ver:
                raw_text = resp_ver.read().decode('utf-8')
                remote_version = self.parse_remote_version(raw_text)

            local_version = CURRENT_VERSION.strip().lower().lstrip("v")

            # 2. Сравниваем версии
            if remote_version and remote_version != local_version:
                req_api = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_api, timeout=5) as resp_api:
                    data = json.loads(resp_api.read().decode())

                download_url = None
                # Ищем установщик
                for asset in data.get("assets", []):
                    asset_name = asset["name"].lower()
                    if asset_name == SETUP_FILENAME.lower() or "setup" in asset_name or asset_name.endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break

                if download_url:
                    self.root.after(0, lambda: self.prompt_update(remote_version, download_url))
                else:
                    self.root.after(0, self.root.destroy)
            else:
                self.root.after(0, self.root.destroy)

        except Exception:
            # В случае ошибки соединения тихо закрываемся
            self.root.after(0, self.root.destroy)

    def prompt_update(self, new_version, download_url):
        # Показываем окно при наличии обновления
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

        if messagebox.askyesno("Обновление", f"Доступно новое обновление v{new_version}!\nХотите обновить игру сейчас?"):
            self.root.attributes("-topmost", False)
            threading.Thread(target=self.download_and_install, args=(download_url,), daemon=True).start()
        else:
            self.root.destroy()

    def download_and_install(self, url):
        installer_path = os.path.join(os.environ.get("TEMP", "."), SETUP_FILENAME)

        def hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = int((downloaded / total_size) * 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                self.root.after(0, lambda: self.update_progress(percent, mb_downloaded, mb_total))

        try:
            urllib.request.urlretrieve(url, installer_path, reporthook=hook)
            self.root.after(0, lambda: self.label.config(text="Запуск установки..."))

            # Запуск установки
            subprocess.Popen([installer_path, "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"])
            self.root.after(500, sys.exit)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при скачивании:\n{e}"))
            self.root.after(0, self.root.destroy)

    def update_progress(self, percent, mb_downloaded, mb_total):
        self.progress["value"] = min(percent, 100)
        self.status_label.config(text=f"{percent}% ({mb_downloaded:.1f} МБ / {mb_total:.1f} МБ)")

if __name__ == "__main__":
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()