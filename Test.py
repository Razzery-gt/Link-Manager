import webbrowser
import json
import os
import getpass
import bcrypt
import validators
import requests
import csv
import yaml
import xml.etree.ElementTree as ET
from docx import Document
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import pyperclip
from datetime import datetime
from colorama import init, Fore
import shutil
import logging
from typing import Dict, Any, Optional, List

# Инициализация библиотеки colorama
init(autoreset=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.expanduser("~"), "Documents", "LinkManager files", "link_manager.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Константы
DOCUMENTS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "LinkManager files")
LINKS_FILENAME = os.path.join(DOCUMENTS_DIR, 'url_links.json')
SETTINGS_FILENAME = os.path.join(DOCUMENTS_DIR, 'settings.json')
HISTORY_FILENAME = os.path.join(DOCUMENTS_DIR, 'history.json')
BACKUP_DIR = os.path.join(DOCUMENTS_DIR, "backups")

# Создание необходимых директорий
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Начальные настройки
default_settings = {
    "password": bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
    "password_required": False,
    "show_links": True,
    "check_updates": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    },
    "logging_level": "INFO"
}

# Стандартные ссылки
default_links = {
    "поисковики": {
        "гугл": {
            "url": "https://www.google.com",
            "date_added": str(datetime.now()),
            "comment": "Поисковая система Google"
        },
        "яндекс": {
            "url": "https://www.yandex.ru",
            "date_added": str(datetime.now()),
            "comment": "Поисковая система Яндекс"
        }
    },
    "разное": {
        "пример": {
            "url": "https://example.com",
            "date_added": str(datetime.now()),
            "comment": "Пример сайта"
        }
    }
}

def load_links() -> Dict[str, Any]:
    """Загрузка ссылок из файла"""
    if os.path.exists(LINKS_FILENAME):
        try:
            with open(LINKS_FILENAME, 'r', encoding='utf-8') as f:
                links = json.load(f)
                # Конвертация старого формата
                for category, category_links in links.items():
                    if isinstance(category_links, dict):
                        for key, value in category_links.items():
                            if isinstance(value, str):
                                links[category][key] = {
                                    "url": value,
                                    "date_added": str(datetime.now()),
                                    "comment": ""
                                }
                return links
        except Exception as e:
            logger.error(f"Ошибка загрузки ссылок: {e}")
    return default_links.copy()

def save_links(links: Dict[str, Any]) -> None:
    """Сохранение ссылок в файл"""
    try:
        with open(LINKS_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка сохранения ссылок: {e}")

def load_settings() -> Dict[str, Any]:
    """Загрузка настроек"""
    if os.path.exists(SETTINGS_FILENAME):
        try:
            with open(SETTINGS_FILENAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
    return default_settings.copy()

def save_settings(settings: Dict[str, Any]) -> None:
    """Сохранение настроек"""
    try:
        with open(SETTINGS_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек: {e}")

def load_history() -> List[Dict[str, str]]:
    """Загрузка истории"""
    if os.path.exists(HISTORY_FILENAME):
        try:
            with open(HISTORY_FILENAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки истории: {e}")
    return []

def save_history(history: List[Dict[str, str]]) -> None:
    """Сохранение истории"""
    try:
        with open(HISTORY_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка сохранения истории: {e}")

def log_opened_link(key: str, url: str) -> None:
    """Логирование открытой ссылки"""
    history = load_history()
    history.append({
        "key": key,
        "url": url,
        "timestamp": str(datetime.now())
    })
    save_history(history[-100:])  # Ограничение истории 100 записями

def check_for_updates() -> None:
    """Проверка обновлений"""
    try:
        response = requests.get(
            "https://api.github.com/repos/yourusername/LinkManager/releases/latest",
            timeout=5
        )
        if response.status_code == 200:
            latest_version = response.json().get("tag_name", "1.0")
            if latest_version > "1.0":
                print(Fore.YELLOW + f"Доступна новая версия: {latest_version}")
    except Exception as e:
        logger.error(f"Ошибка проверки обно��лений: {e}")

def export_links(links: Dict[str, Any], filename: str, format: str) -> None:
    """Экспорт ссылок"""
    try:
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Key', 'URL', 'Comment', 'Date Added'])
                for category, data in links.items():
                    for key, values in data.items():
                        writer.writerow([category, key, values['url'], values.get('comment', ''), values['date_added']])
        elif format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(links, f, indent=4)
        print(Fore.GREEN + f"Экспорт в {format} успешен!")
    except Exception as e:
        logger.error(f"Ошибка экспорта: {e}")
        print(Fore.RED + "Ошибка экспорта!")

def import_links(filename: str, format: str) -> Dict[str, Any]:
    """Импорт ссылок"""
    links = {}
    try:
        if format == 'csv':
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row['Category']
                    if category not in links:
                        links[category] = {}
                    links[category][row['Key']] = {
                        "url": row['URL'],
                        "comment": row['Comment'],
                        "date_added": row['Date Added']
                    }
        return links
    except Exception as e:
        logger.error(f"Ошибка импорта: {e}")
        return {}

def main_menu() -> None:
    """Главное меню"""
    links = load_links()
    settings = load_settings()

    # Проверка пароля
    if settings["password_required"]:
        password = getpass.getpass("Введите пароль: ")
        if not bcrypt.checkpw(password.encode(), settings["password"].encode()):
            print(Fore.RED + "Неверный пароль!")
            return

    # Проверка обновлений
    if settings["check_updates"]:
        check_for_updates()

    while True:
        print(Fore.MAGENTA + "\n=== Link Manager ===")
        print("1. Показать ссылки")
        print("2. Добавить ссылку")
        print("3. Удалить ссылку")
        print("4. Экспорт ссылок")
        print("5. Импорт ссылок")
        print("6. Настройки")
        print("7. Выход")

        choice = input(Fore.WHITE + "Выберите действие: ")

        if choice == "1":
            # Показать ссылки
            pass  # Реализация показа ссылок
        elif choice == "2":
            # Добавить ссылку
            pass
        elif choice == "7":
            print(Fore.GREEN + "До свидания!")
            break
        else:
            print(Fore.RED + "Неверный ввод!")

if __name__ == "__main__":
    main_menu()
