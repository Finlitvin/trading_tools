import csv
from dataclasses import replace
from datetime import datetime, timedelta

import config
from candle import Candle

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24


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
                    open_=row[1],
                    high=row[2],
                    low=row[3],
                    close=row[4],
                    volume=row[5],
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
            current_block = candle

    aggregated.append(current_block)

    return aggregated


def main():
    candles = parse_data(file_name=config.FILE_NAME)

    aggregate = aggregate_data(candles=candles, timeframe=1 * HOUR)

    print(aggregate)


if __name__ == "__main__":
    main()
