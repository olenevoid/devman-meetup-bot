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
