from .item import Item


class Goal(Item):
    def __init__(self, runtime, variation: str):
        super().__init__(runtime, f"assets/img/representations/goal/{variation}.png")
