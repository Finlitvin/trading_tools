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
    color: CandleColor = field(init=False)

    def set_color(self) -> None:
        if self.close >= self.open_:
            self.color = CandleColor.GREEN
        else:
            self.color = CandleColor.RED

    def __post_init__(self) -> None:
        self.set_color()
