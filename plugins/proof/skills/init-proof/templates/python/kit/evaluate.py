from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .evidence import Evidence, EvidenceError
from .matchers import same
from .types import Check, CheckFn, Receipt, Surface


@dataclass(frozen=True)
class EvaluationKit:
    evidence: Evidence
    check: CheckFn
    surfaces: list[Surface]


@dataclass(frozen=True)
class Contract:
    prove: Callable[[EvaluationKit], None]
    required_checks: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    surfaces: tuple[Surface, ...] = ('api',)


def evaluate(*, app: str, run_dir: Path, revision: str, contract_sha256: str,
             manifest_sha256: str, contracts: Mapping[str, Contract],
             features: Sequence[str] = ()) -> Receipt:
    selected = list(dict.fromkeys(features)) or list(contracts)
    receipt = Receipt('ERROR', revision, app, datetime.now(timezone.utc).isoformat(),
                      features=selected, surfaces=[])
    try:
        if not selected or any(name not in contracts for name in selected):
            raise EvidenceError('Select known nonempty contracts')
        evidence = Evidence(run_dir, revision=revision, contract_sha256=contract_sha256,
                            manifest_sha256=manifest_sha256)
        for name in selected:
            contract = contracts[name]
            if (not contract.required_checks or len(set(contract.required_checks)) != len(contract.required_checks)
                    or not contract.surfaces or any(s not in ('api', 'web') for s in contract.surfaces)):
                raise EvidenceError(f'Invalid contract declaration: {name}')
            for artifact in contract.required_artifacts:
                evidence.read(artifact)
        for name in selected:
            contract = contracts[name]
            observed: Counter[str] = Counter()

            def check(name: str, actual: object, expected: object, hint: str | None = None) -> None:
                observed[name] += 1
                if observed[name] > 1:
                    raise EvidenceError(f'Duplicate check: {name}')
                receipt.checks.append(Check(name, same(actual, expected), expected, actual, hint))

            contract.prove(EvaluationKit(evidence, check, list(contract.surfaces)))
            missing = [check_name for check_name in contract.required_checks if observed[check_name] != 1]
            if missing:
                raise EvidenceError(f'Missing required checks for {name}: {missing}')
            assert receipt.surfaces is not None
            receipt.surfaces = list(dict.fromkeys([*receipt.surfaces, *contract.surfaces]))
        receipt.verdict = 'PASS' if all(check.passed for check in receipt.checks) else 'FAIL'
        receipt.next_steps = (['These checks passed on this revision.'] if receipt.verdict == 'PASS'
                              else [check.hint or f'Fix {check.name}' for check in receipt.checks if not check.passed])
        receipt.next_steps.extend(f'Supplementary evidence unavailable: {name}' for name in evidence.missing_optional)
    except Exception as exception:  # A project contract may raise anything; preserve partial observations.
        receipt.error = f'{type(exception).__name__}: {exception}'
        receipt.next_steps = [receipt.error, 'Recapture complete evidence for the approved contract and final revision.']
    return receipt
