from enum import StrEnum, auto

from telegram import InlineKeyboardButton

NAME_SEPARATOR = "__"
PARAM_SEPARATOR = ","


class Callback(StrEnum):
    HOME = auto()
    BACK = auto()
    MENU = auto()

    SHOW_PROGRAM = auto()
    PROG_FULL = auto()
    PROG_PAGE = auto()

    ASK_SPEAKER = auto()

    NETWORKING = auto()
    NET_FILL_PROFILE = auto()
    NET_NEXT = auto()
    NET_REVEAL = auto()
    NET_LEAVE = auto()

    DONATE = auto()
    DON_PRESET = auto()
    DON_CUSTOM = auto()

    SPEAKER_CABINET = auto()
    SPK_START = auto()
    SPK_END = auto()
    SPK_LIST = auto()
    SPK_QUESTION = auto()
    SPK_ANSWER = auto()


class CallbackData:
    def __init__(self, name: Callback, params: dict | None = None):
        self.name: Callback = name
        self.params: dict = params or {}

    @property
    def param_string(self) -> str:
        if not self.params:
            return ""
        return PARAM_SEPARATOR.join(
            f"{name}={value}" for name, value in self.params.items()
        )

    def to_str(self) -> str:
        if self.param_string:
            return f"{self.name.value}{NAME_SEPARATOR}{self.param_string}"
        return self.name.value


class CallbackButton(InlineKeyboardButton):
    def __init__(self, text: str, callback_name: Callback, **params):
        callback_data = CallbackData(callback_name, params).to_str()
        super().__init__(text, callback_data=callback_data)


def get_pattern(callback_name: Callback) -> str:
    return f"^({callback_name.value})(?:__.*)?$"


def parse_callback_data_string(callback_data: str) -> CallbackData:
    parsed_callback = callback_data.split(NAME_SEPARATOR)
    callback_name = Callback(parsed_callback[0])
    callback_params = {}
    if len(parsed_callback) > 1:
        param_pairs = parsed_callback[1].split(PARAM_SEPARATOR)
        for param_pair in param_pairs:
            if param_pair:
                name, value = _parse_param_pair(param_pair)
                callback_params[name] = value
    return CallbackData(callback_name, callback_params)


def _parse_param_pair(param_pair: str) -> tuple:
    name, value = param_pair.split("=")
    if value.isnumeric():
        value = int(value)
    return name, value
