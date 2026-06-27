# MeetUp Bot

Telegram-бот для организации митапов. MVP-версия.

## ⚙️ Технический стек

- **Язык**: Python 3.12+
- **Библиотека**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **База данных**: Django ORM + SQLite (как БД для MVP)
- **Документация**: проектная документация хранится в папке `docs/`

## 🚀 Разработка (рекомендованный Workflow)

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

4. **Pull Request:** откройте PR на GitHub в веб-интерфейсе
   (`base: main` ← `compare: feature/<имя-задачи>`). Дайте
   осмысленный заголовок и краткое описание того, что сделано.


   Готово — мёржите PR кнопкой *Merge pull request*

5. **Завершение:** после merge Pull Request'а обновите локальный
   `main` и удалите локальную ветку

> 💡 Мелкие правки (hotfix) — опечатки, точечные багфиксы — можно делать напрямую в `main` без отдельной ветки.

## 🧪 Демо-база данных

Команда `create_demo_db` создаёт с нуля базу с демонстрационными данными
для ручного тестирования бота:

- текущая БД (если есть) переименовывается в резервную копию вида
  `db_backup_YYYYMMDD_HHMMSS.sqlite3` — данные не теряются;
- создаётся новая пустая БД и применяются миграции;
- загружается фикстура `metup_bot/fixtures/demo_data.json`
  (лежит в git и редактируется вручную).

```bash
./venv/bin/python manage.py create_demo_db
# без подтверждения (например, для скриптов):
./venv/bin/python manage.py create_demo_db --no-input
# загрузить другую фикстуру:
./venv/bin/python manage.py create_demo_db --fixture other.json
```

Демо-пользователи (пароль у всех — `demopass123`):

| Логин     | Роль      | Дополнительно               |
|-----------|-----------|-----------------------------|
| organizer | organizer | superuser, вход в `/admin`  |
| alice     | speaker   | активный доклад сейчас      |
| bob       | speaker   |                             |
| eve       | speaker   |                             |
| carol     | guest     |                             |

Ещё гости (без докладов): `dave`, `frank`, `grace`, `heidi`, `ivan`, `judy`.
Каждый спикер ведёт ровно один доклад; доклады и вопросы — на русском.

Отдельный суперпользователь для входа в `/admin`: логин `admin`, пароль `AdminAdmin`.

> ⚠️ Не запускайте команду в проде: она заменяет файл базы данных.

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
