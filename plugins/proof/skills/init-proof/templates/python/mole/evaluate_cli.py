from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from proof.kit import Receipt, evaluate, exit_code
from proof.kit.capture import contract_digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Evaluate saved evidence without running the app or tests')
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--contract-sha256', required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--contract-module', default='proof.tools.contracts')
    parser.add_argument('--feature', action='append', default=[])
    parser.add_argument('--app', required=True)
    args = parser.parse_args(argv)
    try:
        if not args.contract_module.startswith('proof.'):
            raise ValueError('Contract module must belong to proof/')
        if contract_digest(Path('proof')) != args.contract_sha256:
            raise ValueError('Local contract code differs from reviewed digest')
        # Project contract imports must be pure; collectors live in separate modules.
        module = importlib.import_module(args.contract_module)
        receipt = evaluate(app=args.app, run_dir=args.run, revision=args.revision,
            contract_sha256=args.contract_sha256, manifest_sha256=args.manifest_sha256,
            contracts=module.CONTRACTS, features=args.feature)
    except Exception as exception:  # Project module import can raise arbitrary exceptions.
        from datetime import datetime, timezone
        receipt = Receipt('ERROR', args.revision, args.app, datetime.now(timezone.utc).isoformat(),
            error=f'{type(exception).__name__}: {exception}', next_steps=['Check approved contract and trusted evidence digests.'])
    data = json.dumps(receipt.to_json(), indent=2)
    try:
        args.run.mkdir(parents=True, exist_ok=True)
        # Preserve every evaluation, including errors, and leave the latest receipt available.
        history = args.run / 'receipts'
        history.mkdir(exist_ok=True)
        import uuid
        with (history / f'{uuid.uuid4().hex}.json').open('x') as handle:
            handle.write(data)
        (args.run / 'receipt.json').write_text(data)
    except OSError as exception:
        print(f'Could not save receipt: {exception}', file=sys.stderr)
        return 2
    print(data)
    return exit_code(receipt)


if __name__ == '__main__':
    sys.exit(main())
