import os
import re
import math
from collections import Counter, defaultdict

# ─── Настройки путей ──────────────────────────────────────────────────────────
PAGES_DIR   = "../task01/downloaded_pages"    
TASK2_DIR   = "../task02/output"

TERMS_OUT   = os.path.join("results", "terms")    # выход: термины
LEMMAS_OUT  = os.path.join("results", "lemmas")   # выход: леммы

os.makedirs(TERMS_OUT, exist_ok=True)
os.makedirs(LEMMAS_OUT, exist_ok=True)


# ─── Извлечение текста из HTML ────────────────────────────────────────────────
def extract_text(html: str) -> str:
    text = re.sub(
        r'<(script|style|noscript)[^>]*>.*?</(script|style|noscript)>',
        ' ', html, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]{2,6};', ' ', text)
    return text

def get_word_counts(html: str) -> tuple:
    """Возвращает (Counter слов, общее кол-во слов) из HTML-страницы."""
    text = extract_text(html)
    words = re.findall(r'[а-яёА-ЯЁa-zA-Z]+', text.lower())
    return Counter(words), len(words)


# ─── Загрузка файлов задания 2 ────────────────────────────────────────────────
def load_tokens(num: str) -> set:
    """Загружает список токенов для страницы XXXX."""
    path = os.path.join(TASK2_DIR, f"tokens_{num}.txt")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def load_lemmas(num: str) -> dict:
    """
    Загружает леммы для страницы XXXX.
    Формат строки: <лемма> <форма1> <форма2> ...
    Возвращает: { форма -> лемма }
    """
    path = os.path.join(TASK2_DIR, f"lemmas_{num}.txt")
    if not os.path.exists(path):
        return {}
    form_to_lemma = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 1:
                continue
            lemma = parts[0]
            # все формы (включая саму лемму) → лемма
            for form in parts:
                form_to_lemma[form] = lemma
    return form_to_lemma


# ─── Шаг 1: считаем TF для каждой страницы ───────────────────────────────────
print("Шаг 1: Считаем TF для каждой страницы...")

# Собираем номера страниц по файлам задания 2
nums = sorted(
    re.search(r'(\d+)', f).group(1)
    for f in os.listdir(TASK2_DIR)
    if re.match(r'tokens_\d+\.txt$', f)
)

if not nums:
    raise FileNotFoundError(f"Не найдено файлов tokens_XXXX.txt в '{TASK2_DIR}'")

print(f"Найдено страниц: {len(nums)}")

# Структуры для хранения данных по всем документам
all_term_tf   = {}   # num -> { термин  -> tf }
all_lemma_tf  = {}   # num -> { лемма   -> tf }
term_df       = defaultdict(int)   # термин -> кол-во документов где встречается
lemma_df      = defaultdict(int)   # лемма  -> кол-во документов где встречается

for num in nums:
    page_path = os.path.join(PAGES_DIR, f"page_{num}.txt")
    if not os.path.exists(page_path):
        print(f"  [!] Не найдена страница page_{num}.txt — пропуск")
        continue

    # Читаем страницу и считаем слова
    with open(page_path, encoding="utf-8", errors="ignore") as f:
        html = f.read()
    word_counts, total_words = get_word_counts(html)

    if total_words == 0:
        continue

    # --- TF терминов ---
    tokens_set = load_tokens(num)
    term_tf = {}
    for term in tokens_set:
        count = word_counts.get(term, 0)
        if count > 0:
            term_tf[term] = count / total_words
    all_term_tf[num] = term_tf

    # Обновляем DF терминов
    for term in term_tf:
        term_df[term] += 1

    # --- TF лемм ---
    # Считаем вхождения через формы: если слово на странице = форма леммы,
    # прибавляем к счётчику этой леммы
    form_to_lemma = load_lemmas(num)
    lemma_counts = Counter()
    for word, count in word_counts.items():
        if word in form_to_lemma:
            lemma_counts[form_to_lemma[word]] += count

    lemma_tf = {}
    for lemma, count in lemma_counts.items():
        lemma_tf[lemma] = count / total_words
    all_lemma_tf[num] = lemma_tf

    # Обновляем DF лемм
    for lemma in lemma_tf:
        lemma_df[lemma] += 1

    print(f"  [{num}] терминов с TF>0: {len(term_tf)}, лемм с TF>0: {len(lemma_tf)}")

# ─── Шаг 2: считаем IDF ──────────────────────────────────────────────────────
print("\nШаг 2: Считаем IDF...")
N = len(all_term_tf)  # общее число документов

# IDF(t) = log(N / df(t))
term_idf  = { t: math.log(N / df) for t, df in term_df.items() if df > 0 }
lemma_idf = { l: math.log(N / df) for l, df in lemma_df.items() if df > 0 }

print(f"  Уникальных терминов с IDF: {len(term_idf)}")
print(f"  Уникальных лемм с IDF:    {len(lemma_idf)}")


# ─── Шаг 3: записываем файлы TF-IDF ─────────────────────────────────────────
print("\nШаг 3: Записываем результаты...")

for num in all_term_tf:

    # --- Термины: results/terms/page_XXXX_terms.txt ---
    term_tf = all_term_tf[num]
    out_path = os.path.join(TERMS_OUT, f"page_{num}_terms.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for term in sorted(term_tf.keys()):
            idf    = term_idf.get(term, 0.0)
            tf_idf = term_tf[term] * idf
            f.write(f"{term} {idf:.6f} {tf_idf:.6f}\n")

    # --- Леммы: results/lemmas/page_XXXX_lemmas.txt ---
    lemma_tf = all_lemma_tf.get(num, {})
    out_path = os.path.join(LEMMAS_OUT, f"page_{num}_lemmas.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for lemma in sorted(lemma_tf.keys()):
            idf    = lemma_idf.get(lemma, 0.0)
            tf_idf = lemma_tf[lemma] * idf
            f.write(f"{lemma} {idf:.6f} {tf_idf:.6f}\n")

print(f"\nГотово! Создано файлов: {len(all_term_tf)} × 2")
print(f"  Термины: results/terms/page_XXXX_terms.txt")
print(f"  Леммы:   results/lemmas/page_XXXX_lemmas.txt")
print(f"  Формат:  <слово> <idf> <tf-idf>")