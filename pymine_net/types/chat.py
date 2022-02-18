from typing import Union


class Chat:
    def __init__(self, chat: Union[str, dict]):
        if isinstance(chat, str):
            self.chat = {"text": chat}
        else:
            self.chat = chat
