import csv
from dataclasses import replace
from datetime import timedelta
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from config import FILE_NAME, MINUTE


class Type(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


@dataclass
class Imbalance:
    type: Type
    start_time: datetime
    end_time: datetime
    gap_high: float
    gap_low: float


@dataclass
class OrderBlock:
    type: Type
    start_time: datetime
    end_time: datetime
    high: float
    low: float


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


def convert_datetime(date_time: str) -> datetime:
    return datetime.strptime(date_time, "%Y%m%d %H%M%S")


def parse_data(file_name: str) -> list[Candle]:
    data = []

    with open(file_name) as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 6:
                continue
            data.append(
                Candle(
                    date_time=convert_datetime(row[0]),
                    open_=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                )
            )
    return data


def aggregate_data(candles: list[Candle], timeframe: int) -> list[Candle]:
    if not candles:
        return []

    aggregated = []
    timeframe = timedelta(minutes=timeframe)
    current_candle = replace(candles[0])

    for candle in candles[1:]:
        if candle.date_time < current_candle.date_time + timeframe:
            current_candle.high = max(current_candle.high, candle.high)
            current_candle.low = min(current_candle.low, candle.low)
            current_candle.close = candle.close
            current_candle.volume += candle.volume
        else:
            aggregated.append(current_candle)
            current_candle = replace(candle)

    aggregated.append(current_candle)

    return aggregated


def find_order_blocks(candles: list[Candle]) -> list[OrderBlock]:
    if len(candles) < 2:
        return []

    order_blocks = []
    prev = candles[0]

    for current in candles[1:]:
        is_bullish = current.close > prev.high
        is_bearish = current.close < prev.low
        high_volume = current.volume > 1.5 * prev.volume

        if is_bullish and high_volume:
            order_blocks.append(
                OrderBlock(
                    type=Type.BULLISH,
                    date_time=current.date_time,
                    price=prev.high,
                    volume=current.volume,
                )
            )

        elif is_bearish and high_volume:
            order_blocks.append(
                OrderBlock(
                    type=Type.BEARISH,
                    date_time=current.date_time,
                    price=prev.low,
                    volume=current.volume,
                )
            )

        prev = replace(current)

    return order_blocks


def find_imbalances(candles: list[Candle]) -> list[Imbalance]:
    imbalances = []

    if len(candles) < 3:
        return imbalances

    for c1, _, c3 in zip(candles[0:], candles[1:], candles[2:]):
        if c1.low > c3.high:
            imbalances.append(
                Imbalance(
                    type=Type.BEARISH,
                    start_time=c1.date_time,
                    end_time=c3.date_time,
                    gap_high=c1.low,
                    gap_low=c3.high,
                )
            )
        elif c1.high < c3.low:
            imbalances.append(
                Imbalance(
                    type=Type.BULLISH,
                    start_time=c1.date_time,
                    end_time=c3.date_time,
                    gap_high=c3.low,
                    gap_low=c1.high,
                )
            )

    return imbalances


def main():
    candles = parse_data(file_name=FILE_NAME)

    candles_60min = aggregate_data(candles=candles, timeframe=60 * MINUTE)
    imbalances_60min = find_imbalances(candles_60min)
    print(imbalances_60min)

    candles_15min = aggregate_data(candles=candles, timeframe=15 * MINUTE)
    imbalances_15min = find_imbalances(candles_15min)
    print(imbalances_15min)


if __name__ == "__main__":
    main()
