import os
import re
from collections import defaultdict

# ─── Импорт pymorphy3 или pymorphy2 ─────────────────────────────────────────
try:
    import pymorphy3 as pymorphy
    print("Используется pymorphy3")
except ImportError:
    try:
        import pymorphy2 as pymorphy
        print("Используется pymorphy2")
    except ImportError:
        raise ImportError("Установите: pip install pymorphy3")

# ─── Стоп-слова ──────────────────────────────────────────────────────────────
# Части речи, которые фильтруем через pymorphy (не нужны как токены)
SKIP_POS = {
    'PREP',   # предлог  (в, на, из, ...)
    'CONJ',   # союз     (и, но, или, ...)
    'PRCL',   # частица  (не, ни, бы, ...)
    'INTJ',   # междометие
    'NPRO',   # местоимение (он, она, они, ...)
}

# Дополнительные слова-исключения (которые pymorphy может не поймать)
EXTRA_STOPWORDS = {
    # русские
    "это","также","тоже","уже","ещё","еще","просто","именно","вообще",
    "например","отчасти","постепенно","совместно","конкретно","ранее",
    "сейчас","нужно","очень","более","менее","самый","самая","самое",
    "весь","вся","всё","все","который","которая","которое","которые",
    "свой","своя","своё","свои","наш","наша","наше","ваш","ваша",
    "такой","такая","такое","такие","там","тут","здесь","куда","где",
    "нет","да","вот","вон","тем","нам","вам","них","его","её","ее",
    # английские
    "the","and","or","but","for","with","from","this","that","these",
    "those","will","would","can","could","may","might","must","shall",
    "should","have","has","had","does","did","been","being","also",
    "just","very","more","some","any","all","both","each","only","not",
    "into","onto","upon","about","above","below","over","under","off",
    "out","back","here","there","then","than","when","where","which",
    "who","what","how","why","once","even","still","already","now",
    "its","our","your","their","his","her","them","you","they","she",
    "was","were","are","too","nor","yet","via","per",
}

PAGES_DIR  = "../task01/downloaded_pages"
# PAGES_DIR  = "task01/downloaded_pages"
OUTPUT_DIR = "output"
MIN_LEN    = 3


# ─── Извлечение текста из HTML ───────────────────────────────────────────────
def extract_text(html: str) -> str:
    text = re.sub(
        r'<(script|style|noscript)[^>]*>.*?</(script|style|noscript)>',
        ' ', html, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]{2,6};', ' ', text)
    text = re.sub(r'&#?\w+;', ' ', text)
    return text


# ─── Валидация токена ────────────────────────────────────────────────────────
def has_mixed_alphabets(t: str) -> bool:
    cyr = any('\u0400' <= c <= '\u04FF' for c in t)
    lat = any('a' <= c.lower() <= 'z' for c in t)
    return cyr and lat


def is_valid(token: str) -> bool:
    if len(token) < MIN_LEN:
        return False
    if any(c.isdigit() for c in token):
        return False
    if has_mixed_alphabets(token):
        return False
    if token in EXTRA_STOPWORDS:
        return False
    clean = token.strip('-')
    if len(clean) < MIN_LEN or not clean.replace('-', '').isalpha():
        return False
    return True


# ─── Лемматизация через pymorphy ─────────────────────────────────────────────
morph = pymorphy.MorphAnalyzer()

def get_lemma(token: str) -> tuple:
    """
    Возвращает (лемма, часть_речи) для токена.
    Если слово является предлогом/союзом/частицей/местоимением — возвращает None.
    """
    parsed = morph.parse(token)
    if not parsed:
        return token, None
    best = parsed[0]
    pos = best.tag.POS
    if pos in SKIP_POS:
        return None, pos
    lemma = best.normal_form
    return lemma, pos


# ─── Токенизация одной страницы ──────────────────────────────────────────────
def tokenize_page(path: str) -> list:
    with open(path, encoding="utf-8", errors="ignore") as f:
        html = f.read()
    text = extract_text(html)
    raw = re.findall(r"[а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z\-]*", text)
    tokens = []
    for t in raw:
        t_low = t.lower().strip('-')
        if not is_valid(t_low):
            continue
        lemma, pos = get_lemma(t_low)
        if lemma is None:          # стоп-слово по части речи
            continue
        tokens.append((t_low, lemma))
    return tokens


# ─── Основная обработка ──────────────────────────────────────────────────────
def process_all_pages():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.isdir(PAGES_DIR):
        print(f"Папка '{PAGES_DIR}' не найдена.")
        return

    page_files = sorted(
        f for f in os.listdir(PAGES_DIR) if re.match(r"page_\d+\.txt$", f)
    )
    if not page_files:
        print("Файлы page_XXXX.txt не найдены.")
        return

    print(f"Найдено страниц: {len(page_files)}\n")

    for page_file in page_files:
        num = re.search(r"(\d+)", page_file).group(1)

        token_lemma_pairs = tokenize_page(os.path.join(PAGES_DIR, page_file))

        # Уникальные токены
        unique_tokens = sorted(set(t for t, _ in token_lemma_pairs))

        # Группировка по леммам
        lemma_to_forms = defaultdict(set)
        for token, lemma in token_lemma_pairs:
            lemma_to_forms[lemma].add(token)

        # tokens_XXXX.txt
        with open(os.path.join(OUTPUT_DIR, f"tokens_{num}.txt"), "w", encoding="utf-8") as f:
            for t in unique_tokens:
                f.write(t + "\n")

        # lemmas_XXXX.txt
        with open(os.path.join(OUTPUT_DIR, f"lemmas_{num}.txt"), "w", encoding="utf-8") as f:
            for lemma in sorted(lemma_to_forms.keys()):
                forms = sorted(lemma_to_forms[lemma])
                f.write(lemma + " " + " ".join(forms) + "\n")

        print(f"  [{num}] {page_file}  →  {len(unique_tokens):5d} токенов  |  {len(lemma_to_forms):5d} лемм")

    print(f"\nГотово! Файлы сохранены в '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    process_all_pages()