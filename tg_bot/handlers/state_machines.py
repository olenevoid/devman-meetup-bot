from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from tg_bot.callbacks import Callback, get_pattern
from tg_bot.handlers import (
    ask_speaker,
    donation,
    main_menu,
    networking,
    program,
    speaker_cabinet,
)
from tg_bot.handlers.states import State


def get_ask_speaker_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT, ask_speaker.receive_question),
        ],
        states={},
        map_to_parent={State.MAIN_MENU: State.MAIN_MENU},
        fallbacks=[
            CallbackQueryHandler(
                main_menu.show_main_menu, get_pattern(Callback.MENU)
            ),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
    )


def get_networking_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                networking.show_bio_form,
                get_pattern(Callback.NET_FILL_PROFILE),
            ),
            CallbackQueryHandler(
                networking.show_favorites,
                get_pattern(Callback.NET_FAVORITES),
            ),
        ],
        states={
            State.NET_FORM_BIO: [
                MessageHandler(filters.TEXT, networking.receive_bio),
            ],
            State.NET_FORM_STACK: [
                MessageHandler(filters.TEXT, networking.receive_stack),
            ],
            State.NET_FORM_CONTACT: [
                MessageHandler(filters.TEXT, networking.receive_contact),
            ],
            State.NET_MATCHING: [
                CallbackQueryHandler(
                    networking.skip,
                    get_pattern(Callback.NET_NEXT),
                ),
                CallbackQueryHandler(
                    networking.favorite,
                    get_pattern(Callback.NET_FAVORITE),
                ),
                CallbackQueryHandler(
                    main_menu.show_main_menu,
                    get_pattern(Callback.NET_LEAVE),
                ),
            ],
            State.NET_FAVORITES: [
                CallbackQueryHandler(
                    main_menu.show_main_menu,
                    get_pattern(Callback.MENU),
                ),
            ],
        },
        map_to_parent={State.MAIN_MENU: State.MAIN_MENU},
        fallbacks=[
            CallbackQueryHandler(
                main_menu.show_main_menu, get_pattern(Callback.MENU)
            ),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
    )


def get_donation_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                donation.preset_amount, get_pattern(Callback.DON_PRESET)
            ),
            CallbackQueryHandler(
                donation.input_custom_amount,
                get_pattern(Callback.DON_CUSTOM),
            ),
        ],
        states={
            State.DON_AWAIT_AMOUNT: [
                MessageHandler(filters.TEXT, donation.receive_custom_amount),
            ],
        },
        map_to_parent={State.MAIN_MENU: State.MAIN_MENU},
        fallbacks=[
            CallbackQueryHandler(
                main_menu.show_main_menu, get_pattern(Callback.MENU)
            ),
        ],
        per_message=False,
        per_chat=True,
        per_user=True,
    )


def get_root_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", main_menu.start)],
        states={
            State.MAIN_MENU: [
                CallbackQueryHandler(
                    program.enter, get_pattern(Callback.SHOW_PROGRAM)
                ),
                CallbackQueryHandler(
                    program.show_full, get_pattern(Callback.PROG_FULL)
                ),
                CallbackQueryHandler(
                    program.page, get_pattern(Callback.PROG_PAGE)
                ),
                CallbackQueryHandler(
                    ask_speaker.enter,
                    get_pattern(Callback.ASK_SPEAKER),
                ),
                CallbackQueryHandler(
                    networking.enter, get_pattern(Callback.NETWORKING)
                ),
                CallbackQueryHandler(
                    donation.enter, get_pattern(Callback.DONATE)
                ),
                CallbackQueryHandler(
                    donation.check_payment,
                    get_pattern(Callback.DON_CHECK),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.enter,
                    get_pattern(Callback.SPEAKER_CABINET),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.start_talk,
                    get_pattern(Callback.SPK_START),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.end_talk,
                    get_pattern(Callback.SPK_END),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.list_questions,
                    get_pattern(Callback.SPK_LIST),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.show_question,
                    get_pattern(Callback.SPK_QUESTION),
                ),
                CallbackQueryHandler(
                    speaker_cabinet.mark_answered,
                    get_pattern(Callback.SPK_ANSWER),
                ),
                CallbackQueryHandler(
                    main_menu.show_main_menu,
                    get_pattern(Callback.MENU),
                ),
                CallbackQueryHandler(
                    main_menu.show_main_menu,
                    get_pattern(Callback.HOME),
                ),
                get_ask_speaker_conversation(),
                get_networking_conversation(),
                get_donation_conversation(),
            ],
            State.IN_ASK_SPEAKER: [get_ask_speaker_conversation()],
            State.IN_NETWORKING: [get_networking_conversation()],
            State.IN_DONATION: [get_donation_conversation()],
        },
        fallbacks=[CommandHandler("start", main_menu.start)],
        per_message=False,
        per_chat=True,
        per_user=True,
    )
