# MeetUp Bot

Telegram-бот для организации митапов. MVP-версия.

## ⚙️ Технический стек

- **Язык**: Python 3.12+
- **Библиотека**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **База данных**: Django ORM + SQLite (как БД для MVP)
- **Документация**: проектная документация хранится в папке `docs/`

## 🚀 Использование (рекомендованный Workflow)

1. **Актуальность:** всегда начинайте работу с подтягивания свежих изменений из основной ветки:

    ```
    git checkout main
    git pull origin main
    ```

2. **Разработка:** создавайте отдельную ветку под каждую задачу (kebab-case):

    ```
    git checkout -b feature/<имя-задачи>
    ```

3. **Коммит и пуш:**

    ```
    git add .
    git commit -m "<что сделано>"
    git push -u origin feature/<имя-задачи>
    ```

4. **Завершение:** после вашего Pull Request (merge), удаляйте локальную ветку:

    ```
    git checkout main
    git pull origin main
    git branch -d feature/<имя-задачи>
    ```

> 💡 Мелкие правки (hotfix) — опечатки, точечные багфиксы — можно делать напрямую в `main` без отдельной ветки.

## 🔧 Переносы строк (Line Endings)

В репозитории принудительно используется `LF` для всех текстовых файлов
(см. `.gitattributes` и `.editorconfig`). Это гарантирует единое поведение
на Windows, Linux и macOS и убирает фантомные diff'ы из-за `CRLF`/`LF`.

- **Новые клоны** работают сразу, ничего настраивать не нужно — `.gitattributes`
  перекрывает локальные настройки `core.autocrlf`.
- **Существующие клоны**: после подтягивания обновлённого `.gitattributes`
  выполните один раз:

    ```
    git add --renormalize .
    git commit -m "Normalize line endings to LF"
    ```

- Windows-специфичные скрипты (`.bat`, `.cmd`) остаются на `CRLF`.
