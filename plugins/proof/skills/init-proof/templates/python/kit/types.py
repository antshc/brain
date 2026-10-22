from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, Protocol, TypeVar
from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

T = TypeVar("T")

# A surface is one way a feature reaches a user: `web` is the app in a real Chrome, `api` is HTTP.
Surface = Literal["web", "api"]
# PASS and FAIL describe the app; ERROR says the evidence cannot be trusted; NOT_REACHED follows an earlier stop.
Verdict = Literal["PASS", "FAIL", "ERROR", "NOT_REACHED"]
ReceiptVerdict = Literal["PASS", "FAIL", "ERROR"]


class SurfaceError(Exception):
    def __init__(self, surface: Surface, message: str, next_step: str) -> None:
        super().__init__(f"{surface}: {message}")
        self.surface = surface
        self.next_step = next_step


class HttpAnswer(Protocol):
    @property
    def status(self) -> int: ...

    @property
    def body(self) -> str: ...


# GET a URL; raises OSError when nothing answers. The caller injects it so the kit stays free of the runner.
Fetch = Callable[[str], HttpAnswer]
Settle = Callable[[Page], None]


@dataclass(frozen=True)
class Var(Generic[T]):
    """A typed key for a value one flow leaves for a later flow of the same scenario."""

    name: str


@dataclass(frozen=True)
class EventWindow:
    """What the page reported between two checkpoints of one scenario."""

    console: tuple[dict[str, Any], ...] = ()
    network: tuple[dict[str, Any], ...] = ()
    page_errors: tuple[str, ...] = ()


def settle_on_load(page: Page) -> None:
    page.wait_for_load_state("load")


@dataclass
class FlowContext:
    """What a flow works with. Interactive `flow` and proving `run` build the same context, so a flow behaves the same in both."""

    page: Page
    app_url: str
    api_url: str | None
    fetch: Fetch
    surfaces: tuple[Surface, ...] = ("web",)
    settle: Settle = field(default=settle_on_load)
    # Replaced before each checkpoint with what happened since the previous one.
    window: EventWindow = field(default_factory=EventWindow)
    variables: dict[str, Any] = field(default_factory=dict)

    def set(self, variable: Var[T], value: T) -> None:
        self.variables[variable.name] = value

    def get(self, variable: Var[T]) -> T:
        if variable.name not in self.variables:
            raise ValueError(f'Scenario variable "{variable.name}" was not set. A flow before this one must set it.')
        value: T = self.variables[variable.name]
        return value

    def url(self, path: str = "/") -> str:
        return urljoin(self.app_url, path)

    def goto(self, path: str = "/") -> None:
        target = self.url(path)
        try:
            self.page.goto(target, wait_until="load", timeout=15_000)
        except PlaywrightError as exception:
            raise SurfaceError("web", f"Can't open {target}: {str(exception).splitlines()[0]}.", "Is the app up and the build fresh?") from exception
        self.settle(self.page)


Observations = Mapping[str, Any]


@dataclass(frozen=True)
class Assessment:
    passed: bool
    expected: Any
    actual: Any
    # What to tell the reader when this fails; defaults to the expected/actual pair.
    hint: str | None = None


class EvidenceAdapter(Protocol):
    """Reads one kind of evidence. `name` keys the observation, `label` is how the feature map names it, `suffix` is the artifact's extension."""

    @property
    def name(self) -> str: ...

    @property
    def label(self) -> str: ...

    @property
    def suffix(self) -> str: ...

    # JSON-able data (or bytes for a binary artifact). Observe only: never navigate or mutate.
    def capture(self, context: FlowContext) -> Any: ...


@dataclass(frozen=True)
class ProofCheck:
    """One fact the scenario asserts, the evidence that proves it, and how to read that evidence."""

    id: str
    evidence: tuple[EvidenceAdapter, ...]
    assess: Callable[[Observations], Assessment]


@dataclass(frozen=True)
class Flow:
    """A reusable user journey. It may navigate and act; it never judges."""

    id: str
    run: Callable[[FlowContext], None]


@dataclass(frozen=True)
class FlowStep:
    flow: Flow


@dataclass(frozen=True)
class ProofStep:
    checks: tuple[ProofCheck, ...]


ScenarioStep = FlowStep | ProofStep


@dataclass(frozen=True)
class Scenario:
    # `feature.sub-feature.scenario`
    id: str
    steps: tuple[ScenarioStep, ...]
    surfaces: tuple[Surface, ...]

    @property
    def feature(self) -> str:
        return self.id.split(".")[0]

    @property
    def sub_feature(self) -> str:
        return ".".join(self.id.split(".")[:2])

    @property
    def checks(self) -> tuple[ProofCheck, ...]:
        return tuple(check for step in self.steps if isinstance(step, ProofStep) for check in step.checks)

    @property
    def flows(self) -> tuple[Flow, ...]:
        return tuple(step.flow for step in self.steps if isinstance(step, FlowStep))


@dataclass(frozen=True)
class SubFeature:
    id: str
    scenarios: tuple[Scenario, ...]


@dataclass(frozen=True)
class Feature:
    """A named area of the app: its sub-features and scenarios, the surfaces it is proved on, and the files it must be re-proved for."""

    id: str
    sub_features: tuple[SubFeature, ...]
    # Repo-relative path prefixes whose changes this feature must be re-proved for.
    touches: tuple[str, ...]
    surfaces: tuple[Surface, ...]

    @property
    def scenarios(self) -> tuple[Scenario, ...]:
        return tuple(scenario for sub in self.sub_features for scenario in sub.scenarios)


@dataclass(frozen=True)
class EvidenceRef:
    check: str
    source: str
    label: str
    # Relative to the receipt's artifact folder.
    artifact: str
    captured_at: str
    step: int

    def to_json(self) -> dict[str, Any]:
        return {"check": self.check, "source": self.source, "label": self.label, "artifact": self.artifact, "capturedAt": self.captured_at, "step": self.step}


@dataclass(frozen=True)
class ProofResult:
    check: str
    step: int
    verdict: Verdict
    expected: Any = None
    actual: Any = None
    evidence: tuple[EvidenceRef, ...] = ()
    hint: str | None = None
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {"check": self.check, "step": self.step, "verdict": self.verdict, "expected": self.expected, "actual": self.actual}
        data["evidence"] = [reference.to_json() for reference in self.evidence]
        if self.hint:
            data["hint"] = self.hint
        if self.error:
            data["error"] = self.error
        return data


@dataclass(frozen=True)
class TraceEntry:
    step: int
    kind: Literal["flow", "proof"]
    id: str
    status: Literal["done", "failed", "not_reached"]

    def to_json(self) -> dict[str, Any]:
        return {"step": self.step, "kind": self.kind, "id": self.id, "status": self.status}


@dataclass
class Receipt:
    """What one scenario run found. A PASS means every check has its own persisted evidence for this revision."""

    verdict: ReceiptVerdict
    scenario: str
    revision: str | None
    app: str
    at: str
    surfaces: list[Surface]
    results: list[ProofResult] = field(default_factory=list)
    trace: list[TraceEntry] = field(default_factory=list)
    artifacts: str | None = None
    # Where the observations came from: a fresh isolated visitor on one revision.
    provenance: dict[str, Any] = field(default_factory=dict)
    page_errors: list[str] = field(default_factory=list)
    screenshot: str | None = None
    error: str | None = None
    next_steps: list[str] = field(default_factory=list)

    @property
    def sub_feature(self) -> str:
        return ".".join(self.scenario.split(".")[:2])

    @property
    def feature(self) -> str:
        return self.scenario.split(".")[0]

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "verdict": self.verdict,
            "scenario": self.scenario,
            "feature": self.feature,
            "subFeature": self.sub_feature,
            "revision": self.revision,
            "app": self.app,
            "at": self.at,
            "surfaces": self.surfaces,
            "trace": [entry.to_json() for entry in self.trace],
            "checks": [result.to_json() for result in self.results],
            "provenance": self.provenance,
        }
        if self.artifacts:
            data["artifacts"] = self.artifacts
        data["pageErrors"] = self.page_errors
        if self.screenshot:
            data["screenshot"] = self.screenshot
        if self.error:
            data["error"] = self.error
        data["next"] = self.next_steps
        return data
