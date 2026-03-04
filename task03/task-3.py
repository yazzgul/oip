import os
import re
import json
from collections import defaultdict

# ─── Настройки путей ─────────────────────────────────────────────────────────
LEMMAS_DIR  = "../task02/output"              # папка с файлами lemmas_XXXX.txt из задания 2
INDEX_FILE  = "inverted_index.json" # куда сохранить индекс


# ─── Построение инвертированного индекса из файлов лемм ──────────────────────
def build_index_from_lemmas(lemmas_dir: str) -> tuple:
    """
    Читает все файлы lemmas_XXXX.txt из папки задания 2.
    Формат строки в файле: <лемма> <форма1> <форма2> ... <формаN>

    Возвращает:
      inverted_index : { лемма -> [doc_id, ...] }
      doc_names      : { doc_id -> имя файла }
    """
    inverted_index = defaultdict(list)
    doc_names = {}

    lemma_files = sorted(
        f for f in os.listdir(lemmas_dir) if re.match(r"lemmas_\d+\.txt$", f)
    )

    if not lemma_files:
        raise FileNotFoundError(f"В папке '{lemmas_dir}' не найдено файлов lemmas_XXXX.txt")

    for lemma_file in lemma_files:
        # Извлекаем номер документа из имени файла (например, 0001)
        num = re.search(r"(\d+)", lemma_file).group(1)
        doc_id = int(num)
        doc_names[doc_id] = lemma_file.replace("lemmas_", "page_")

        path = os.path.join(lemmas_dir, lemma_file)
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                lemma = parts[0]  # первое слово — лемма
                # Добавляем doc_id к данной лемме (без дубликатов)
                if doc_id not in inverted_index[lemma]:
                    inverted_index[lemma].append(doc_id)

    # Сортируем списки doc_id для удобства
    for lemma in inverted_index:
        inverted_index[lemma].sort()

    print(f"Загружено документов: {len(doc_names)}")
    print(f"Уникальных лемм в индексе: {len(inverted_index)}")
    return dict(inverted_index), doc_names


def save_index(inverted_index: dict, doc_names: dict, filepath: str):
    """Сохраняет инвертированный индекс в JSON."""
    data = {
        "документы": doc_names,
        "индекс": inverted_index,
        "все_документы": sorted(doc_names.keys())
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Индекс сохранён: {filepath}")


def load_index(filepath: str) -> tuple:
    """Загружает индекс из JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    inverted_index = data["индекс"]
    doc_names = {int(k): v for k, v in data["документы"].items()}
    all_docs = set(data["все_документы"])
    return inverted_index, doc_names, all_docs


# ─── Булев поиск ─────────────────────────────────────────────────────────────
class BooleanSearch:
    def __init__(self, inverted_index: dict, all_docs: set):
        self.index = inverted_index
        self.all_docs = all_docs

    def search(self, query: str) -> list:
        tokens = self._tokenize_query(query)
        postfix = self._infix_to_postfix(tokens)
        result = self._evaluate(postfix)
        return sorted(result)

    def _tokenize_query(self, query: str) -> list:
        pattern = r'\(|\)|\bAND\b|\bOR\b|\bNOT\b|\b[а-яёА-ЯЁa-zA-Z]+\b'
        tokens = re.findall(pattern, query)
        result = []
        for t in tokens:
            if t in ('AND', 'OR', 'NOT', '(', ')'):
                result.append(t)
            else:
                result.append(t.lower())
        return result

    def _infix_to_postfix(self, tokens: list) -> list:
        """Алгоритм сортировочной станции (shunting-yard)."""
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        output, stack = [], []
        for token in tokens:
            if token not in ('AND', 'OR', 'NOT', '(', ')'):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # убираем '('
            else:  # оператор
                while (stack and stack[-1] != '(' and
                       precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def _evaluate(self, postfix: list) -> set:
        stack = []
        for token in postfix:
            if token == 'NOT':
                operand = stack.pop()
                stack.append(self.all_docs - operand)
            elif token == 'AND':
                right, left = stack.pop(), stack.pop()
                stack.append(left & right)
            elif token == 'OR':
                right, left = stack.pop(), stack.pop()
                stack.append(left | right)
            else:
                # Термин — ищем в индексе по лемме
                doc_set = set(self.index.get(token, []))
                stack.append(doc_set)
        return stack.pop() if stack else set()


# ─── Главная программа ───────────────────────────────────────────────────────
def main():
    # Шаг 1: построить индекс из лемм задания 2 (или загрузить готовый)
    if os.path.exists(INDEX_FILE):
        print(f"Загружаю существующий индекс из {INDEX_FILE}...")
        inverted_index, doc_names, all_docs = load_index(INDEX_FILE)
        print(f"  Документов: {len(doc_names)}, лемм: {len(inverted_index)}")
    else:
        print("Строю индекс из файлов лемм задания 2...")
        inverted_index, doc_names = build_index_from_lemmas(LEMMAS_DIR)
        all_docs = set(doc_names.keys())
        save_index(inverted_index, doc_names, INDEX_FILE)

    engine = BooleanSearch(inverted_index, all_docs)

    # Шаг 2: булев поиск
    print("\nБулев поиск по инвертированному индексу")
    print("Операторы: AND, OR, NOT  |  Пример: автомобиль AND беспилотник")
    print("Введите пустую строку для выхода.\n")

    while True:
        query = input("Запрос: ").strip()
        if not query:
            break

        result_ids = engine.search(query)
        print(f"Найдено документов: {len(result_ids)}")
        for doc_id in result_ids:
            print(f"  [{doc_id:04d}] {doc_names.get(doc_id, '???')}")
        print()


if __name__ == "__main__":
    main()