import os
import re
import json
from collections import defaultdict

class BooleanSearchEngine:
    def __init__(self, docs_source):
        """
        docs_source: либо список строк (документов), либо путь к папке с .txt файлами.
        """
        self.documents = {}  # id -> текст
        self.inverted_index = defaultdict(list)  # термин -> список id
        self.all_docs = set()

        if isinstance(docs_source, list):
            # Документы переданы списком строк
            for i, text in enumerate(docs_source, start=1):
                self.documents[i] = text
        elif isinstance(docs_source, str) and os.path.isdir(docs_source):
            # Читаем все .txt файлы из папки
            for i, filename in enumerate(sorted(os.listdir(docs_source)), start=1):
                if filename.endswith('.txt'):
                    with open(os.path.join(docs_source, filename), 'r', encoding='utf-8') as f:
                        self.documents[i] = f.read().strip()
        else:
            raise ValueError("docs_source должен быть списком строк или путём к папке")

        self.all_docs = set(self.documents.keys())
        self._build_index()

    def _build_index(self):
        """Построение инвертированного индекса."""
        for doc_id, text in self.documents.items():
            # Токенизация: слова из букв (включая русские и английские), приводим к нижнему регистру
            words = re.findall(r'\b[а-яА-Яa-zA-ZёЁ]+\b', text)
            for word in words:
                word_low = word.lower()
                if doc_id not in self.inverted_index[word_low]:
                    self.inverted_index[word_low].append(doc_id)

    def save_index(self, filepath):
        """Сохраняет индекс в JSON."""
        data = {
            'документы': self.documents,
            'индекс': self.inverted_index,
            'все_документы': list(self.all_docs)
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_index(self, filepath):
        """Загружает индекс из JSON (альтернативный способ создания объекта)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.documents = {int(k): v for k, v in data['документы'].items()}
        self.inverted_index = {k: v for k, v in data['индекс'].items()}
        self.all_docs = set(data['все_документы'])

    def search(self, query):
        """
        Выполняет булев запрос, возвращает список id документов, удовлетворяющих запросу.
        """
        # Токенизация запроса
        tokens = self._tokenize_query(query)
        # Преобразование в постфиксную запись (ОПН)
        postfix = self._infix_to_postfix(tokens)
        # Вычисление результата
        result_set = self._evaluate_postfix(postfix)
        return sorted(result_set)

    def _tokenize_query(self, query):
        """Разбивает строку запроса на токены: слова, операторы, скобки."""
        # Регулярное выражение для выделения слов (буквы), операторов AND, OR, NOT и скобок
        pattern = r'\(|\)|\bAND\b|\bOR\b|\bNOT\b|\b[а-яА-Яa-zA-ZёЁ]+\b'
        tokens = re.findall(pattern, query)
        # Приводим термины (не операторы) к нижнему регистру
        result = []
        for t in tokens:
            if t not in ('AND', 'OR', 'NOT', '(', ')'):
                result.append(t.lower())
            else:
                result.append(t)
        return result

    def _infix_to_postfix(self, tokens):
        """Преобразует инфиксную последовательность токенов в постфиксную (алгоритм сортировочной станции)."""
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        output = []
        stack = []

        for token in tokens:
            if token not in ('AND', 'OR', 'NOT', '(', ')'):
                # Операнд (термин)
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # убираем '('
            else:
                # Оператор
                while (stack and stack[-1] != '(' and
                       precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)

        while stack:
            output.append(stack.pop())

        return output

    def _evaluate_postfix(self, postfix):
        """Вычисляет значение выражения в постфиксной записи, используя множества doc_id."""
        stack = []

        for token in postfix:
            if token == 'NOT':
                # Унарный оператор
                operand = stack.pop()
                # NOT A = все_документы \ A
                result = self.all_docs - operand
                stack.append(result)
            elif token in ('AND', 'OR'):
                # Бинарные операторы
                right = stack.pop()
                left = stack.pop()
                if token == 'AND':
                    result = left & right
                else:  # OR
                    result = left | right
                stack.append(result)
            else:
                # Термин: получаем множество id документов, содержащих этот термин (или пустое)
                doc_set = set(self.inverted_index.get(token, []))
                stack.append(doc_set)

        # В стеке должен остаться один элемент – итоговое множество
        return stack.pop() if stack else set()


def main():
    # Демонстрационная коллекция документов
    docs = [
        "Клеопатра и Цезарь были связаны",
        "Антоний и Цицерон соперничали",
        "Помпей был великим полководцем",
        "Цезарь победил Помпея",
        "Антоний влюбился в Клеопатру",
        "Цицерон был оратором"
    ]

    # Создаём поисковый движок
    engine = BooleanSearchEngine(docs)

    # Сохраняем индекс в файл (требование задания)
    engine.save_index('inverted_index.json')
    print("Индекс сохранён в файл inverted_index.json\n")

    # Запрос вводится с клавиатуры (не хардкодится)
    print("Введите булев запрос (поддерживаются AND, OR, NOT, скобки).")
    print("Пример: (Клеопатра AND Цезарь) OR (Антоний AND Цицерон) OR Помпей")
    query = input("Запрос: ").strip()

    if not query:
        query = "(Клеопатра AND Цезарь) OR (Антоний AND Цицерон) OR Помпей"
        print(f"Используется демо-запрос: {query}")

    result_ids = engine.search(query)

    print(f"\nНайдено документов: {len(result_ids)}")
    for doc_id in result_ids:
        print(f"{doc_id}: {engine.documents[doc_id]}")


if __name__ == "__main__":
    main()