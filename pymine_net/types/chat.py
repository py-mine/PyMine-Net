from typing import Union


class Chat:
    def __init__(self, data: Union[str, dict]):
        if isinstance(data, str):
            self.data = {"text": data}
        else:
            self.data = data
