#!/usr/bin/env python
import time

# Based on https://stackoverflow.com/a/34325723/388951
class ProgressBar:
    def __init__(self, *, decimals=1, width=80, fill='█'):
        self.decimals = decimals
        self.width = width
        self.fill = fill

    def __enter__(self):
        self.print(0, 1, 'Processing…')
        return self

    def __exit__(self, a, b, c):
        print()

    def print(self, num: int, den: int, msg: str) -> None:
        percent = (f'{{0:.{self.decimals}f}}').format(100 * num / den)
        filledLength = int(self.width * num // den)
        bar = self.fill * filledLength + '-' * (self.width - filledLength)
        print(f'\r|{bar}| {percent}% {msg}', end = '\r')


class FakeProgressBar:
    def __init__(self, *, decimals=1, width=80, fill='█'):
        pass

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def print(self, num: int, den: int, msg: str) -> None:
        pass


if __name__ == '__main__':
    with ProgressBar(width=80) as progress:
        for i in range(0, 10):
            time.sleep(0.5)
            progress.print(i + 1, 10, f'Item number {i+1}')
