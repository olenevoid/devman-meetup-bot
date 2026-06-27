from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

from metup_bot.models import Question, Talk, User


@sync_to_async
def create_question(tg_id: int, talk: Talk, text: str) -> Question:
    author = User.objects.get(telegram_profile__telegram_id=tg_id)
    return Question.objects.create(talk=talk, author=author, text=text)


@sync_to_async
def get_questions_paginated(
    talk: Talk, page: int = 1, page_size: int = 5
) -> tuple[list[Question], int]:
    queryset = Question.objects.filter(talk=talk).order_by("-created_at")
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    return list(page_obj.object_list), paginator.num_pages


@sync_to_async
def get_question(question_id: int) -> Question | None:
    return Question.objects.filter(pk=question_id).first()


@sync_to_async
def mark_answered(question_id: int) -> Question | None:
    Question.objects.filter(pk=question_id).update(is_answered=True)
    return Question.objects.filter(pk=question_id).first()


@sync_to_async
def unanswered_count_for_user(tg_id: int) -> int:
    return Question.objects.filter(
        talk__speaker__telegram_profile__telegram_id=tg_id,
        talk__event__is_current=True,
        is_answered=False,
    ).count()
