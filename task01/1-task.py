import os
import time
import requests
from urllib.parse import urlparse

# Конфигурация
URLS_FILE = "/Users/yazgul/Desktop/urls.txt"                 # файл со списком ссылок
OUTPUT_DIR = "/Users/yazgul/Desktop/downloaded_pages"         # папка для сохранения страниц
INDEX_FILE = "/Users/yazgul/Desktop/index.txt"                # файл с индексом
DELAY = 1                                # задержка между запросами (сек)
TIMEOUT = 10                             # таймаут соединения

def create_output_dir():
    """Создаёт папку для скачанных страниц, если её нет."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def download_page(url, file_number):
    """
    Скачивает страницу по URL с правильными заголовками и сохраняет в файл.
    """
    # Заголовки, которые отправляет обычный браузер
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    }
    
    try:
        # Добавляем заголовки в запрос
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            filename = f"page_{file_number:04d}.txt"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"[+] {filename} сохранён: {url}")
            return True
        else:
            print(f"[-] Ошибка HTTP {response.status_code} для {url}")
            # Дополнительно выведем причину, если сервер её прислал
            if response.status_code == 403:
                print("    Сервер отклонил запрос (403 Forbidden). Возможно, нужны ещё заголовки или задержка.")
            return False
            
    except Exception as e:
        print(f"[-] Ошибка при скачивании {url}: {e}")
        return False

def main():
    # Проверяем наличие файла со ссылками
    if not os.path.exists(URLS_FILE):
        print(f"Файл {URLS_FILE} не найден. Создайте его со списком URL.")
        return

    # Читаем ссылки, пропуская пустые строки
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    if len(urls) < 100:
        print(f"Внимание: найдено только {len(urls)} ссылок, требуется минимум 100.")

    create_output_dir()
    index_entries = []
    success_count = 0

    for i, url in enumerate(urls, start=1):
        print(f"\nОбработка {i}/{len(urls)}: {url}")
        if download_page(url, i):
            index_entries.append(f"{i:04d} {url}\n")
            success_count += 1
        time.sleep(DELAY)   # вежливая пауза

    # Записываем индекс
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.writelines(index_entries)

    print(f"\nГотово. Скачано {success_count} страниц из {len(urls)}.")
    print(f"Файлы сохранены в папке '{OUTPUT_DIR}', индекс в '{INDEX_FILE}'.")

if __name__ == "__main__":
    main()