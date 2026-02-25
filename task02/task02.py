import sys
from collections import defaultdict
import re

# Стоп-слова (предлоги, союзы, частицы) для русского и английского
russian_stopwords = {
    "в", "во", "на", "с", "со", "и", "а", "но", "или", "же", "бы", "ли",
    "из", "за", "у", "к", "о", "об", "от", "до", "по", "под", "над", "при",
    "про", "без", "для", "через", "между", "из-за", "из-под", "как", "так",
    "что", "чтобы", "тоже", "также", "это", "эти", "этот", "эта", "это"
}
english_stopwords = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
    "with", "by", "of", "from", "as", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "can", "could",
    "may", "might", "must", "shall", "should", "that", "this", "these", "those"
}
stopwords = russian_stopwords.union(english_stopwords)

def has_mixed_alphabets(token):
    """Проверяет, содержит ли токен смесь кириллицы и латиницы"""
    has_cyrillic = any('\u0400' <= c <= '\u04FF' or c == 'ё' or c == 'Ё' for c in token)
    has_latin = any('a' <= c.lower() <= 'z' for c in token)
    return has_cyrillic and has_latin

def is_valid_token(token):
    # Проверка на пустоту
    if not token:
        return False
    
    # Проверка на наличие цифр
    if any(c.isdigit() for c in token):
        return False
    
    # Проверка на смесь алфавитов
    if has_mixed_alphabets(token):
        return False
    
    # Проверка на стоп-слова
    if token in stopwords:
        return False
    
    # Проверка, что токен состоит только из букв (одного алфавита)
    if not token.replace('-', '').isalpha():
        return False
    
    return True

def process_files():
    all_tokens = set()
    form_to_lemma = {}
    
    print("Чтение файлов...")

    # Чтение tokens_1.txt
    try:
        with open('tokens_1.txt', 'r', encoding='utf-8') as f:
            for line in f:
                token = line.strip().lower()
                if token:
                    all_tokens.add(token)
        print(f"Загружено токенов из tokens_1.txt: {len(all_tokens)}")
    except FileNotFoundError:
        print("Файл tokens_1.txt не найден")

    # Чтение lemmas_1.txt и lemmas_2.txt
    for filename in ['lemmas_1.txt', 'lemmas_2.txt']:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    
                    parts = line.split(':', 1)
                    if len(parts) != 2:
                        continue
                        
                    lemma, forms_str = parts
                    lemma = lemma.strip().lower()
                    
                    # Проверяем лемму на валидность
                    if is_valid_token(lemma):
                        all_tokens.add(lemma)
                        form_to_lemma[lemma] = lemma
                    
                    # Обрабатываем формы
                    forms = forms_str.strip().split()
                    for form in forms:
                        form_low = form.lower()
                        if is_valid_token(form_low):
                            all_tokens.add(form_low)
                            form_to_lemma[form_low] = lemma
            print(f"Загружено из {filename}")
        except FileNotFoundError:
            print(f"Файл {filename} не найден")

    print(f"Всего уникальных токенов до фильтрации: {len(all_tokens)}")

    # Фильтрация токенов
    clean_tokens = []
    invalid_tokens = []
    
    for token in all_tokens:
        if is_valid_token(token):
            clean_tokens.append(token)
        else:
            invalid_tokens.append(token)
    
    clean_tokens.sort()
    
    print(f"Валидных токенов после фильтрации: {len(clean_tokens)}")
    print(f"Отфильтровано 'мусорных' токенов: {len(invalid_tokens)}")
    if invalid_tokens:
        print("Примеры отфильтрованных токенов:", invalid_tokens[:10])

    # Группировка по леммам
    lemma_to_forms = defaultdict(list)
    unmatched_tokens = []
    
    for token in clean_tokens:
        if token in form_to_lemma:
            lemma = form_to_lemma[token]
        else:
            lemma = token
            unmatched_tokens.append(token)
        lemma_to_forms[lemma].append(token)
    
    print(f"Токенов, найденных в словаре лемм: {len(clean_tokens) - len(unmatched_tokens)}")
    print(f"Токенов НЕ найденных в словаре: {len(unmatched_tokens)}")

    # Сортировка лемм для вывода
    sorted_lemmas = sorted(lemma_to_forms.keys())

    # Запись файла с токенами
    with open('tokens_output.txt', 'w', encoding='utf-8') as f:
        for token in clean_tokens:
            f.write(token + '\n')
    print("Создан файл tokens_output.txt")

    # Запись файла с леммами (без дубликатов в строке)
    with open('lemmas_output.txt', 'w', encoding='utf-8') as f:
        for lemma in sorted_lemmas:
            # Убираем дубликаты и сортируем
            unique_forms = sorted(set(lemma_to_forms[lemma]))
            # Формируем строку: лемма и уникальные формы
            line = lemma + ' ' + ' '.join(unique_forms)
            f.write(line + '\n')
    print("Создан файл lemmas_output.txt")

    print("Обработка завершена успешно!")

if __name__ == "__main__":
    process_files()