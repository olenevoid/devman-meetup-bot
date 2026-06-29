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
    profile = getattr(talk.speaker, "telegram_profile", None)
    username = profile.telegram_username if profile else ""
    if not username:
        username = talk.speaker.username
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
