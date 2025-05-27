from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


class CandleColor(Enum):
    GREEN = "GREEN"
    RED = "RED"


@dataclass
class Candle:
    date_time: datetime
    open_: float
    high: float
    low: float
    close: float
    volume: float
    colour: CandleColor = field(init=False)

    def set_colour(self) -> None:
        if self.close >= self.open_:
            self.colour = CandleColor.GREEN
        else:
            self.colour = CandleColor.RED

    def __post_init__(self) -> None:
        self.set_colour()
