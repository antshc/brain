from dataclasses import dataclass, field


@dataclass
class ExecutionRecord:
    pr_url: str
    count: int
    last_run: str
    last_threads: list[str] = field(default_factory=list)
