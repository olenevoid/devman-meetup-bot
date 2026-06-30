from enum import Enum, auto


class State(Enum):
    MAIN_MENU = auto()
    IN_ASK_SPEAKER = auto()
    IN_NETWORKING = auto()
    IN_DONATION = auto()
    ASK_AWAIT_QUESTION = auto()
    NET_FORM_BIO = auto()
    NET_FORM_STACK = auto()
    NET_FORM_CONTACT = auto()
    NET_MATCHING = auto()
    NET_FAVORITES = auto()
    DON_AWAIT_AMOUNT = auto()
