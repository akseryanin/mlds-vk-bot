from dataclasses import dataclass


@dataclass
class Request:
    Id: int
    UserId: int
    Metric: str
