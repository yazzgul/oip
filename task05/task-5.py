import os
import re
import math
from collections import defaultdict

# ─── Настройки путей ──────────────────────────────────────────────────────────
TERMS_DIR  = os.path.join("../task04/results", "terms")
LEMMAS_DIR = os.path.join("../task04/results", "lemmas")

# режимы поиска: "terms" или "lemmas"
SEARCH_MODE = "lemmas"


# ─── Загрузка TF-IDF индекса из файлов задания 4 ─────────────────────────────
def load_tfidf_index(results_dir: str) -> tuple:
    """
    Читает все файлы page_XXXX_*.txt из папки задания 4.
    Возвращает:
      doc_vectors : { doc_id -> { слово -> tf_idf } }
      idf_table   : { слово -> idf }
      doc_names   : { doc_id -> имя файла }
    """
    suffix = "_terms.txt" if "terms" in results_dir else "_lemmas.txt"
    files = sorted(
        f for f in os.listdir(results_dir)
        if f.endswith(suffix)
    )
    if not files:
        raise FileNotFoundError(f"В '{results_dir}' не найдено файлов {suffix}")

    doc_vectors = {}
    idf_table   = {}
    doc_names   = {}

    for fname in files:
        num = re.search(r'(\d+)', fname).group(1)
        doc_id = int(num)
        doc_names[doc_id] = f"page_{num}.txt"

        vector = {}
        path = os.path.join(results_dir, fname)
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                word, idf, tf_idf = parts[0], float(parts[1]), float(parts[2])
                if tf_idf > 0:
                    vector[word] = tf_idf
                    idf_table[word] = idf   # idf одинаков для слова по всем документам

        doc_vectors[doc_id] = vector

    print(f"Загружено документов: {len(doc_vectors)}")
    print(f"Слов в словаре: {len(idf_table)}")
    return doc_vectors, idf_table, doc_names


# ─── Косинусное сходство ─────────────────────────────────────────────────────
def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Косинусное сходство между двумя разреженными векторами."""
    # Скалярное произведение
    dot = sum(vec_a.get(w, 0.0) * vec_b.get(w, 0.0) for w in vec_b)
    if dot == 0:
        return 0.0
    # Нормы
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ─── Векторизация запроса ─────────────────────────────────────────────────────
def vectorize_query(query: str, idf_table: dict) -> dict:
    """
    Превращает строку запроса в TF-IDF вектор.
    TF считается внутри самого запроса, IDF берётся из индекса.
    """
    words = re.findall(r'[а-яёА-ЯЁa-zA-Z]+', query.lower())
    if not words:
        return {}

    # TF внутри запроса
    word_count = defaultdict(int)
    for w in words:
        word_count[w] += 1
    total = len(words)

    query_vector = {}
    for word, count in word_count.items():
        if word in idf_table:
            tf = count / total
            query_vector[word] = tf * idf_table[word]

    return query_vector


# ─── Поиск ───────────────────────────────────────────────────────────────────
def search(query: str, doc_vectors: dict, idf_table: dict,
           doc_names: dict, top_k: int = 10) -> list:
    """
    Возвращает top_k наиболее релевантных документов.
    Каждый элемент: (doc_id, имя_файла, cosine_similarity)
    """
    query_vec = vectorize_query(query, idf_table)

    if not query_vec:
        print("  Ни одно слово из запроса не найдено в индексе.")
        return []

    # Считаем сходство с каждым документом
    scores = []
    for doc_id, doc_vec in doc_vectors.items():
        sim = cosine_similarity(doc_vec, query_vec)
        if sim > 0:
            scores.append((doc_id, doc_names[doc_id], sim))

    # Сортируем по убыванию сходства
    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[:top_k]


# ─── Главная программа ───────────────────────────────────────────────────────
def main():
    results_dir = TERMS_DIR if SEARCH_MODE == "terms" else LEMMAS_DIR

    print(f"Режим поиска: {SEARCH_MODE}")
    print(f"Загружаю TF-IDF индекс из '{results_dir}'...\n")

    doc_vectors, idf_table, doc_names = load_tfidf_index(results_dir)

    print(f"\nВекторный поиск готов!")
    print("Введите запрос (одно или несколько слов).")
    print("Введите пустую строку для выхода.\n")

    while True:
        query = input("Запрос: ").strip()
        if not query:
            break

        results = search(query, doc_vectors, idf_table, doc_names, top_k=10)

        if not results:
            print("Документов не найдено.\n")
            continue

        print(f"Найдено документов: {len(results)} (топ-10 по релевантности)\n")
        print(f"  {'№':<6} {'Документ':<20} {'Сходство':>10}")
        print(f"  {'-'*6} {'-'*20} {'-'*10}")
        for rank, (doc_id, name, sim) in enumerate(results, 1):
            print(f"  {rank:<6} {name:<20} {sim:>10.6f}")
        print()


if __name__ == "__main__":
    main()