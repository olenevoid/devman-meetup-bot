from html import escape

ROLE_LABELS = {
    "guest": "гость",
    "speaker": "спикер",
    "organizer": "организатор",
}


def main_menu_text(roles: set[str]) -> str:
    visible = roles | {"guest"}
    labels = [ROLE_LABELS.get(r, r) for r in sorted(visible)]
    roles_str = ", ".join(labels)
    return (
        "🐍 PythonMeetup\n\n"
        "Привет! Помогу: программа, вопрос спикеру, "
        "найти собеседника, поддержать донатом.\n\n"
        f"Ваши роли: {roles_str}"
    )


def stub_text(name: str) -> str:
    return f"Раздел «{name}» в разработке."


def _safe(value) -> str:
    return escape(str(value))


def _format_time(value) -> str:
    if value is None:
        return ""
    return value.strftime("%H:%M")


def _speaker_handle(talk) -> str:
    return _user_handle(talk.speaker)


def _user_handle(user) -> str:
    profile = getattr(user, "telegram_profile", None)
    username = profile.telegram_username if profile else ""
    if not username:
        username = user.username
    return f"@{_safe(username)}"


def _talk_time_range(talk) -> str:
    start = _format_time(talk.scheduled_start)
    end = _format_time(talk.scheduled_end)
    if start and end:
        return f"{start}–{end}"
    return start


def _talk_meta(talk) -> str:
    handle = _speaker_handle(talk)
    time_range = _talk_time_range(talk)
    return " · ".join(part for part in (handle, time_range) if part)


_TALK_STATE_EMOJI = {
    "active": "🔴",
    "finished": "✅",
    "planned": "🟢",
}


def _talk_status_emoji(talk) -> str:
    return _TALK_STATE_EMOJI.get(talk.state, "🟢")


def ask_prompt(active_talk) -> str:
    handle = _speaker_handle(active_talk)
    title = _safe(active_talk.title)
    return (
        f"❓ Активный спикер: {handle}\n"
        f"Доклад: «{title}»\n\n"
        "Напиши вопрос одним сообщением."
    )


def no_active_speaker() -> str:
    return (
        "❌ Сейчас никто не выступает.\n"
        "Попробуй, когда начнётся следующий доклад."
    )


def question_sent(active_talk) -> str:
    handle = _speaker_handle(active_talk)
    return (
        f"✅ Вопрос отправлен {handle}.\n"
        "Он увидит его в разделе «Мои вопросы»."
    )


def speaker_cabinet_text(
    talk, active_talk, total: int, unanswered: int
) -> str:
    if talk is None:
        return (
            "🎤 Кабинет спикера\n\n"
            "У вас нет доклада на текущем мероприятии."
        )
    title = _safe(talk.title)
    state = talk.state
    if state == "active":
        header = f"🎤 «{title}» ● идёт"
    elif state == "finished":
        header = f"🎤 «{title}» ✓ завершён"
    else:
        header = f"🎤 Мой доклад: «{title}»"
    lines = [header]
    if state == "planned":
        if active_talk is not None and active_talk.pk != talk.pk:
            lines.append(
                f"Сейчас выступает " f"{_user_handle(active_talk.speaker)}."
            )
            lines.append("Начать можно после завершения.")
        else:
            lines.append("Статус: запланирован")
            lines.append("Вопросов пока нет — начни доклад")
    else:
        lines.append(f"Вопросов: {total}\nНеотвечено: {unanswered}")
    return "\n".join(lines)


def questions_list_text(talk, page: int, num_pages: int) -> str:
    title = _safe(talk.title)
    header = f"✉️ Вопросы к докладу «{title}»"
    if num_pages > 1:
        header += f" · стр. {page}/{num_pages}"
    return header


def question_detail_text(question) -> str:
    marker = "✅" if question.is_answered else "✉️"
    handle = _user_handle(question.author)
    time = _format_time(question.created_at)
    return f"{marker} от {handle} · {time}\n\n{_safe(question.text)}"


def _program_talk_block(marker: str, talk) -> str:
    title_line = f"{marker}: «{_safe(talk.title)}»"
    meta = _talk_meta(talk)
    if not meta:
        return title_line
    return f"{title_line}\n    {meta}"


def program_text(active_talk=None, next_talk=None) -> str:
    header = "📅 Программа"
    blocks = []
    if active_talk is not None:
        blocks.append(_program_talk_block("🔴 Сейчас", active_talk))
    if next_talk is not None:
        blocks.append(_program_talk_block("⏭ Дальше", next_talk))
    if not blocks:
        return f"{header}\n\nПрограмма пока пуста."
    return header + "\n\n" + "\n".join(blocks)


def full_program_text(page: int, num_pages: int, talks: list) -> str:
    header = "🗓 Программа"
    if num_pages > 1:
        header += f" · стр. {page}/{num_pages}"
    if not talks:
        return f"{header}\n\nПока запланированных докладов нет."
    lines = [header, ""]
    for talk in talks:
        handle = _speaker_handle(talk)
        start = _format_time(talk.scheduled_start)
        suffix = f" {start}" if start else ""
        emoji = _talk_status_emoji(talk)
        lines.append(f"{emoji} «{_safe(talk.title)}» — {handle}{suffix}")
    return "\n".join(lines)


def _profile_name(profile) -> str:
    name = (profile.user.first_name or "").strip()
    return _safe(name) if name else _user_handle(profile.user)


def networking_intro_text() -> str:
    return (
        "🤝 Нетворкинг\n\n"
        "Заполни анкету — бот покажет анкеты других гостей."
    )


def networking_no_profiles_text() -> str:
    return "🤝 Пока нет других анкет. Загляни позже."


def networking_all_viewed_text() -> str:
    return "🤝 Ты посмотрел все анкеты."


def networking_favorites_text(profiles: list) -> str:
    if not profiles:
        return "⭐ У тебя пока нет избранных анкет."
    lines = ["⭐ Избранное", ""]
    for profile in profiles:
        name = _profile_name(profile)
        contact = _safe(profile.contact or "")
        if contact:
            lines.append(f"👤 {name} · {contact}")
        else:
            lines.append(f"👤 {name}")
    return "\n".join(lines)


def networking_form_text(step: int) -> str:
    prompts = {
        1: "Шаг 1/3: расскажи о себе (короткое bio одним сообщением).",
        2: "Шаг 2/3: твой стек (например, Python/Django).",
        3: "Шаг 3/3: оставь контакт (@username или ссылка).",
    }
    return prompts[step]


def networking_card_text(profile) -> str:
    name = _profile_name(profile)
    stack = (profile.stack or "").strip()
    header = f"👤 {name}"
    if stack:
        header += f" · {_safe(stack)}"
    lines = [header]
    bio = (profile.bio or "").strip()
    if bio:
        lines.append(f"«{_safe(bio)}»")
    lines += ["", f"Контакт: {_safe(profile.contact)}"]
    return "\n".join(lines)
