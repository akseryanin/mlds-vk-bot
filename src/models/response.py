from dataclasses import dataclass


@dataclass
class Response:
    Id: int
    UserId: int
    Metric: str
    MetricValue: list[int]
    Increment: float
