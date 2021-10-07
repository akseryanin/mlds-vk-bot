from dataclasses import dataclass
from datetime import datetime


@dataclass()
class Response:
    Id: int
    UserId: int
    Metric: str
    MetricValue: list[int]
    Increment: float
    IsDone: bool
    CountPosts: int
    TimeFilterNeeded: bool
    DateTimeStart: datetime
    DateTimeEnd: datetime

