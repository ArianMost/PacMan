from src.config.config import Config


class Game:
    def __init__(self, config: Config) -> None:
        ...

    def run(self) -> None:
        ...

    def handle_events(self) -> None:
        ...

    def render(self) -> None:
        ...
