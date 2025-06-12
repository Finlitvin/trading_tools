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


@dataclass
class Imbalance:
    type: Type
    start_time: datetime
    end_time: datetime
    gap_high: float
    gap_low: float


@dataclass
class OrderBlock:
    candle: Candle
    type: Type
    high: float
    low: float


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


def find_order_blocks(
    candles: list[Candle],
    imbalances: dict[datetime, Imbalance],
    tolerance: int = 1,
) -> list[OrderBlock]:
    order_blocks = []

    if len(candles) < 2:
        return order_blocks

    for cl, c1, c2, cr in zip(
        candles[0:], candles[1:], candles[2:], candles[3:]
    ):
        print(c1.date_time, c2.date_time)
        print(c1.color, c2.color)
        print(c2.open_, c1.close)
        print(c2.close, c1.open_)
        print("")
        if (
            (c1.color, c2.color) == (CandleColor.RED, CandleColor.GREEN)
            and c2.open_ <= c1.close + tolerance
            and c2.close >= c1.open_
        ):
            print(1)
            high = c1.high if c2.date_time in imbalances else c1.open_
            low = min(c1.low, c2.low)
            if low <= cl.low and low <= cr.low:
                print(2)
                order_blocks.append(
                    OrderBlock(
                        candle=c2,
                        type=Type.BULLISH,
                        high=high,
                        low=low,
                    )
                )

        if (
            (c1.color, c2.color) == (CandleColor.GREEN, CandleColor.RED)
            and c2.open_ >= c1.close - tolerance
            and c2.close <= c1.open_
        ):
            print(3)
            high = max(c1.high, c2.high)
            low = c1.low if c2.date_time in imbalances else c1.open_
            if high >= cl.high and high >= cr.high:
                print(4)
                order_blocks.append(
                    OrderBlock(
                        candle=c2,
                        type=Type.BEARISH,
                        high=high,
                        low=low,
                    )
                )
    return order_blocks


def find_imbalances(candles: list[Candle]) -> dict[datetime, Imbalance]:
    imbalances = {}

    if len(candles) < 3:
        return imbalances

    for c1, _, c3 in zip(candles[0:], candles[1:], candles[2:]):
        if c1.low > c3.high:
            imbalances[c1.date_time] = Imbalance(
                type=Type.BEARISH,
                start_time=c1.date_time,
                end_time=c3.date_time,
                gap_high=c1.low,
                gap_low=c3.high,
            )
        elif c1.high < c3.low:
            imbalances[c1.date_time] = Imbalance(
                type=Type.BULLISH,
                start_time=c1.date_time,
                end_time=c3.date_time,
                gap_high=c3.low,
                gap_low=c1.high,
            )

    return imbalances


def main():
    candles = parse_data(file_name=FILE_NAME)

    candles_60min = aggregate_data(candles, 60 * MINUTE)
    imbalances_60min = find_imbalances(candles_60min)
    # print(imbalances_60min)

    candles_15min = aggregate_data(candles, 15 * MINUTE)
    imbalances_15min = find_imbalances(candles_15min)
    # print(imbalances_15min)

    order_blocks_60min = find_order_blocks(candles_60min, imbalances_60min)
    print(order_blocks_60min)


if __name__ == "__main__":
    main()
