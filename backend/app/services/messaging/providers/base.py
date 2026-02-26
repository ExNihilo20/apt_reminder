class MessageProviderError(Exception):
    pass


class BaseMessageProvider:
    def send(self, *, to: str, body: str) -> dict:
        raise NotImplementedError