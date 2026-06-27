# Разработка бота

Гайд по коду в `tg_bot/`. БД-часть (модели, миграции, сервисы) отдельно.

## Структура `tg_bot/`

```
tg_bot/
├── handlers/
│   ├── states.py             # enum состояний диалога
│   ├── state_machines.py     # проводка ConversationHandler (не трогать)
│   ├── main_menu.py
│   ├── program.py
│   ├── ask_speaker.py
│   ├── networking.py
│   ├── donation.py
│   └── speaker_cabinet.py
├── callbacks.py              # enum Callback + CallbackButton
├── keyboards.py              # сборка клавиатур
├── strings.py                # все тексты
├── messaging.py              # edit_current / replace_current
├── validators.py             # валидация ввода
├── payment.py                # YooKassa
└── settings.py               # env-переменные
```

## Поток запроса

```
Telegram update
    ↓
handler  →  await service  →  models
    ↓
render через messaging.*
```

Хендлер принимает update, вызывает сервис, рендерит ответ. Логика и БД — в сервисах.

## Где что писать

| Задача | Файл |
|---|---|
| Логика экрана | `handlers/<flow>.py` |
| Текст сообщения | `strings.py` |
| Кнопка / клавиатура | `keyboards.py` |
| Новое callback-имя | `callbacks.py` → enum `Callback` |
| Состояние диалога | `handlers/states.py` |
| Чтение / запись в БД | `metup_bot/services/<domain>.py` |

## Заполнение плейсхолдера

Все хендлеры уже есть как плейсхолдеры с правильной сигнатурой. Тело показывает «🚧 в разработке». Задача — заменить тело на реализацию.

1. Откройте нужный `handlers/<flow>.py`
2. Найдите функцию по имени из задачи
3. Замените тело на реализацию
4. Сохраните сигнатуру и `return State.X` — проводка зависит от этого
5. `state_machines.py` **не трогайте**

### Шаблон хендлера

```python
from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import questions

from tg_bot import keyboards, strings
from tg_bot.callbacks import parse_callback_data_string
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current


async def show_question(
    update: Update, context: CallbackContext
) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    question_id = data.params["id"]
    question = await questions.get_question(question_id)
    await edit_current(
        update,
        text=strings.question_detail(question),
        keyboard=keyboards.question_actions(question),
    )
    return State.MAIN_MENU
```

## Вывод сообщений (`messaging.py`)

В чате всегда одно сообщение бота. Навигация его редактирует, новые экраны — заменяют.

### `edit_current(update, text, keyboard=None)`

Редактирует текущее сообщение. Только когда есть `update.callback_query` — то есть в `CallbackQueryHandler`.

```python
await edit_current(
    update,
    text=strings.program_text(),
    keyboard=keyboards.program_actions(),
)
```

### `replace_current(update, context, text, keyboard=None)`

Удаляет прошлое сообщение бота и присылает новое. В `MessageHandler` и `CommandHandler` — там, где `callback_query` нет. `context` нужен, чтобы хранить `message_id` текущего сообщения.

```python
await replace_current(
    update,
    context,
    text=strings.question_sent(),
    keyboard=keyboards.menu_only(),
)
```

### Когда что

| Триггер | Функция |
|---|---|
| Тап по inline-кнопке | `edit_current` |
| Текстовое сообщение | `replace_current` |
| Команда (`/start`) | `replace_current` |

`edit_current` без `callback_query` упадёт. Если не уверены — проверьте `update.callback_query is not None`.

## Конвенции

- **Кнопки** — только через `CallbackButton` и enum `Callback`. Никаких строк в `callback_data` руками.
- **Тексты** — только в `strings.py`.
- **Сервисы** — вызывайте через `await` (они обёрнуты `@sync_to_async`). `metup_bot.models` в `tg_bot` не импортируйте — только через сервисы.
- **Состояния** — enum `State` в `handlers/states.py`.
- **`state_machines.py`** — проводка готова. Меняется только при добавлении новых состояний или потоков, по договорённости.

## Callback с параметрами

```python
# Создание кнопки с параметром
CallbackButton("Открыть", Callback.SPK_QUESTION, id=12)
# → callback_data = "spk_question__id=12"

# Чтение параметра в хендлере
data = parse_callback_data_string(update.callback_query.data)
question_id = data.params["id"]
```

Для маршрутизации используется `get_pattern(Callback.SPK_QUESTION)` — regex, ловит callback с любыми параметрами.

## Запуск

```
python manage.py migrate
python manage.py runbot
```

Откройте бота в Telegram → `/start`.

Админка (для тестовых данных), отдельный терминал:
```
python manage.py createsuperuser
python manage.py runserver
```
→ http://localhost:8000/admin/
