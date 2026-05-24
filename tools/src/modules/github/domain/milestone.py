from dataclasses import dataclass


@dataclass
class Milestone:
    id: str
    title: str
    description: str
    url: str
