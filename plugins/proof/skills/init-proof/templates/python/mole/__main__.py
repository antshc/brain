from __future__ import annotations

import sys

if len(sys.argv) > 1 and sys.argv[1] == 'evaluate':
    from .evaluate_cli import main
    sys.exit(main(sys.argv[2:]))
else:
    from .mole import main
    sys.exit(main())
