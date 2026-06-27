from enum import Enum, auto


class State(Enum):
    MAIN_MENU = auto()
    ASK_INPUT_QUESTION = auto()
    NET_INPUT_BIO = auto()
    NET_INPUT_STACK = auto()
    NET_INPUT_CONTACT = auto()
    NET_MATCHING = auto()
    DON_INPUT_AMOUNT = auto()
