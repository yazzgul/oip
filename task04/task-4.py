# import os
# import re
# import math
# import glob
# from collections import Counter, defaultdict
# from bs4 import BeautifulSoup
# import pymorphy3

# # Настройка путей
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# TOKENS_FILE = os.path.join(BASE_DIR, '..', 'task02', 'tokens_output.txt')
# LEMMAS_FILE = os.path.join(BASE_DIR, '..', 'task02', 'lemmas_output.txt')
# PAGES_DIR = os.path.join(BASE_DIR, '..', 'task01', 'downloaded_pages')
# PAGE_PATTERN = os.path.join(PAGES_DIR, 'page_*.txt')

# # Папки для результатов
# TERMS_RESULT_DIR = os.path.join(BASE_DIR, 'results', 'terms')
# LEMMAS_RESULT_DIR = os.path.join(BASE_DIR, 'results', 'lemmas')
# os.makedirs(TERMS_RESULT_DIR, exist_ok=True)
# os.makedirs(LEMMAS_RESULT_DIR, exist_ok=True)

# # Загрузка терминов (каждая строка — одно слово)
# def load_terms(filename):
#     with open(filename, 'r', encoding='utf-8') as f:
#         return set(line.strip() for line in f if line.strip())

# # Загрузка лемм (поддерживает оба формата)
# def load_lemmas(filename):
#     lemmas = set()
#     with open(filename, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
            
#             # Если есть двоеточие — берём левую часть
#             if ':' in line:
#                 lemma = line.split(':')[0].strip()
#                 if lemma:
#                     lemmas.add(lemma)
#             else:
#                 # Если нет двоеточия — вся строка это лемма
#                 lemmas.add(line)
    
#     return lemmas

# print("Загрузка терминов и лемм...")
# terms_set = load_terms(TOKENS_FILE)
# lemmas_set = load_lemmas(LEMMAS_FILE)
# print(f"Терминов: {len(terms_set)}, лемм: {len(lemmas_set)}")

# # Инициализация лемматизатора
# morph = pymorphy3.MorphAnalyzer()

# def tokenize(text):
#     return re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', text.lower())

# processed_files = []
# processed_term_freq = []
# processed_lemma_freq = []
# processed_token_count = []

# page_files = sorted(glob.glob(PAGE_PATTERN))
# print(f"Найдено {len(page_files)} страниц. Начинаем обработку...")

# for i, page_file in enumerate(page_files):
#     with open(page_file, 'r', encoding='utf-8') as f:
#         html = f.read()
    
#     soup = BeautifulSoup(html, 'html.parser')
#     text = soup.get_text()
#     tokens = tokenize(text)
#     token_count = len(tokens)
    
#     if token_count == 0:
#         print(f"Предупреждение: документ {page_file} не содержит слов, пропускаем.")
#         continue
    
#     # Частота терминов
#     token_counter = Counter(tokens)
#     term_freq = {term: token_counter.get(term, 0) for term in terms_set}
#     term_freq = {k: v for k, v in term_freq.items() if v > 0}
    
#     # Частота лемм
#     lemma_counter = Counter()
#     for token in tokens:
#         lemma = morph.parse(token)[0].normal_form
#         # Проверяем, есть ли лемма в нашем списке
#         if lemma in lemmas_set:
#             lemma_counter[lemma] += 1
    
#     lemma_freq = dict(lemma_counter)  # только те леммы, что встретились
    
#     processed_files.append(page_file)
#     processed_term_freq.append(term_freq)
#     processed_lemma_freq.append(lemma_freq)
#     processed_token_count.append(token_count)
    
#     if (i+1) % 20 == 0:
#         print(f"Обработано {i+1} страниц")

# print("Обработка завершена. Вычисляем IDF...")
# total_docs = len(processed_files)
# print(f"Документов с текстом: {total_docs}")

# # IDF для терминов
# term_df = defaultdict(int)
# for tf in processed_term_freq:
#     for term in tf:
#         term_df[term] += 1

# term_idf = {}
# for term in terms_set:
#     df = term_df.get(term, 0)
#     term_idf[term] = 0.0 if df == 0 else math.log(total_docs / df)

# # IDF для лемм
# lemma_df = defaultdict(int)
# for lf in processed_lemma_freq:
#     for lemma in lf:
#         lemma_df[lemma] += 1

# lemma_idf = {}
# for lemma in lemmas_set:
#     df = lemma_df.get(lemma, 0)
#     lemma_idf[lemma] = 0.0 if df == 0 else math.log(total_docs / df)

# print("IDF вычислен. Генерируем файлы с TF-IDF...")

# for idx, page_file in enumerate(processed_files):
#     basename = os.path.basename(page_file).replace('.txt', '')
    
#     # Файл для терминов
#     term_out_file = os.path.join(TERMS_RESULT_DIR, f"{basename}_terms.txt")
#     with open(term_out_file, 'w', encoding='utf-8') as f:
#         term_freq = processed_term_freq[idx]
#         token_count = processed_token_count[idx]
#         for term in sorted(term_freq.keys()):
#             tf = term_freq[term] / token_count
#             tf_idf = tf * term_idf[term]
#             f.write(f"{term} {term_idf[term]:.6f} {tf_idf:.6f}\n")
    
#     # Файл для лемм
#     lemma_out_file = os.path.join(LEMMAS_RESULT_DIR, f"{basename}_lemmas.txt")
#     with open(lemma_out_file, 'w', encoding='utf-8') as f:
#         lemma_freq = processed_lemma_freq[idx]
#         token_count = processed_token_count[idx]
#         for lemma in sorted(lemma_freq.keys()):
#             tf = lemma_freq[lemma] / token_count
#             tf_idf = tf * lemma_idf[lemma]
#             f.write(f"{lemma} {lemma_idf[lemma]:.6f} {tf_idf:.6f}\n")

# print("Готово! Результаты сохранены в папках results/terms и results/lemmas.")
import os
import re
import math
import glob
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import pymorphy3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOKENS_FILE = os.path.join(BASE_DIR, '..', 'task02', 'tokens_output.txt')
LEMMAS_FILE1 = os.path.join(BASE_DIR, '..', 'task02', 'lemmas_1.txt')
LEMMAS_FILE2 = os.path.join(BASE_DIR, '..', 'task02', 'lemmas_2.txt')
PAGES_DIR = os.path.join(BASE_DIR, '..', 'task01', 'downloaded_pages')
PAGE_PATTERN = os.path.join(PAGES_DIR, 'page_*.txt')

TERMS_RESULT_DIR = os.path.join(BASE_DIR, 'results', 'terms')
LEMMAS_RESULT_DIR = os.path.join(BASE_DIR, 'results', 'lemmas')
os.makedirs(TERMS_RESULT_DIR, exist_ok=True)
os.makedirs(LEMMAS_RESULT_DIR, exist_ok=True)

def load_terms(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def load_lemmas_from_file(filename):
    """Загружает леммы из файла формата 'лемма: список форм'."""
    lemmas = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            # Берём только то, что до двоеточия
            lemma = line.split(':')[0].strip()
            if lemma:
                lemmas.add(lemma)
    return lemmas

def load_all_lemmas():
    """Загружает леммы из всех файлов lemmas_*.txt"""
    lemmas = set()
    
    # Загружаем из lemmas_1.txt
    if os.path.exists(LEMMAS_FILE1):
        l1 = load_lemmas_from_file(LEMMAS_FILE1)
        lemmas.update(l1)
        print(f"Загружено лемм из lemmas_1.txt: {len(l1)}")
    
    # Загружаем из lemmas_2.txt
    if os.path.exists(LEMMAS_FILE2):
        l2 = load_lemmas_from_file(LEMMAS_FILE2)
        lemmas.update(l2)
        print(f"Загружено лемм из lemmas_2.txt: {len(l2)}")
    
    return lemmas

def tokenize(text):
    return re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', text.lower())

print("Загрузка терминов и лемм...")
terms_set = load_terms(TOKENS_FILE)
lemmas_set = load_all_lemmas()
print(f"Терминов: {len(terms_set)}")
print(f"Всего уникальных лемм: {len(lemmas_set)}")
print(f"Примеры лемм: {sorted(list(lemmas_set))[:20]}")

morph = pymorphy3.MorphAnalyzer()

processed_files = []
processed_term_freq = []
processed_lemma_freq = []
processed_token_count = []

page_files = sorted(glob.glob(PAGE_PATTERN))
print(f"Найдено {len(page_files)} страниц. Начинаем обработку...")

for i, page_file in enumerate(page_files):
    with open(page_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    tokens = tokenize(text)
    token_count = len(tokens)
    
    if token_count == 0:
        print(f"Предупреждение: документ {page_file} не содержит слов, пропускаем.")
        continue
    
    # Частота терминов
    token_counter = Counter(tokens)
    term_freq = {term: token_counter.get(term, 0) for term in terms_set}
    term_freq = {k: v for k, v in term_freq.items() if v > 0}
    
    # Частота лемм
    lemma_counter = Counter()
    for token in tokens:
        try:
            lemma = morph.parse(token)[0].normal_form
            if lemma in lemmas_set:
                lemma_counter[lemma] += 1
        except:
            continue
    
    lemma_freq = dict(lemma_counter)
    
    # Отладка для первых 3 документов
    if i < 3:
        print(f"\n=== Документ {os.path.basename(page_file)} ===")
        print(f"Токенов: {token_count}")
        print(f"Примеры токенов: {tokens[:10]}")
        print(f"Примеры лемм: {list(lemma_freq.keys())[:10]}")
        print(f"Найдено лемм из списка: {len(lemma_freq)}")
    
    processed_files.append(page_file)
    processed_term_freq.append(term_freq)
    processed_lemma_freq.append(lemma_freq)
    processed_token_count.append(token_count)
    
    if (i+1) % 20 == 0:
        print(f"Обработано {i+1} страниц")

print("\n=== Статистика ===")
print(f"Документов с текстом: {len(processed_files)}")

# Проверим, какие леммы встречаются
all_found_lemmas = set()
total_lemma_occurrences = 0
for lf in processed_lemma_freq:
    all_found_lemmas.update(lf.keys())
    total_lemma_occurrences += sum(lf.values())

print(f"Лемм из списка, которые встретились: {len(all_found_lemmas)} из {len(lemmas_set)}")
print(f"Процент покрытия: {len(all_found_lemmas)/len(lemmas_set)*100:.1f}%")
print(f"Всего вхождений лемм в тексты: {total_lemma_occurrences}")

# Вычисляем IDF
total_docs = len(processed_files)

term_df = defaultdict(int)
for tf in processed_term_freq:
    for term in tf:
        term_df[term] += 1

term_idf = {}
for term in terms_set:
    df = term_df.get(term, 0)
    term_idf[term] = 0.0 if df == 0 else math.log(total_docs / df)

lemma_df = defaultdict(int)
for lf in processed_lemma_freq:
    for lemma in lf:
        lemma_df[lemma] += 1

lemma_idf = {}
for lemma in lemmas_set:
    df = lemma_df.get(lemma, 0)
    lemma_idf[lemma] = 0.0 if df == 0 else math.log(total_docs / df)

print("\nIDF вычислен. Генерируем файлы...")

for idx, page_file in enumerate(processed_files):
    basename = os.path.basename(page_file).replace('.txt', '')
    
    # Термины
    term_out_file = os.path.join(TERMS_RESULT_DIR, f"{basename}_terms.txt")
    with open(term_out_file, 'w', encoding='utf-8') as f:
        term_freq = processed_term_freq[idx]
        token_count = processed_token_count[idx]
        for term in sorted(term_freq.keys()):
            tf = term_freq[term] / token_count
            tf_idf = tf * term_idf[term]
            f.write(f"{term} {term_idf[term]:.6f} {tf_idf:.6f}\n")
    
    # Леммы
    lemma_out_file = os.path.join(LEMMAS_RESULT_DIR, f"{basename}_lemmas.txt")
    with open(lemma_out_file, 'w', encoding='utf-8') as f:
        lemma_freq = processed_lemma_freq[idx]
        token_count = processed_token_count[idx]
        if lemma_freq:
            for lemma in sorted(lemma_freq.keys()):
                tf = lemma_freq[lemma] / token_count
                tf_idf = tf * lemma_idf[lemma]
                f.write(f"{lemma} {lemma_idf[lemma]:.6f} {tf_idf:.6f}\n")
        else:
            f.write("# В этом документе не найдено ни одной леммы из списка\n")

print(f"Готово! Создано файлов: {len(processed_files)}")