from dataclasses import dataclass


@dataclass
class Milestone:
    id: str
    number: int
    title: str
    description: str
    url: str
