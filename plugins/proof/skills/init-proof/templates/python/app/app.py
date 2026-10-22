from __future__ import annotations

import os

from mole.config import AppConfig, StartConfig
# <surface: api>
from mole.config import ApiConfig
# </surface: api>
# <surface: web>
from mole.config import WebConfig
# </surface: web>

# The one file that says what this app is. The mole reads it; every value comes from the codebase, not a guess.
# Resolve each TODO(proof) from the repo (see the init-proof research checklist), then delete the marker.
APP = AppConfig(
    name={{APP_NAME_JSON}},
    # TODO(proof): the URL the app answers on locally. PROOF_URL overrides it.
    url=os.environ.get("PROOF_URL", "http://localhost:3000"),
    surfaces=[{{SURFACES_LIST}}],
    # TODO(proof): repo-relative folders whose changes alter the running build. The revision is derived from them.
    source_paths=["src"],
    feature_maps="{{SKILL_DIR}}/features",
    # TODO(proof): how `{{MOLE}} up --start` runs the app, and how it knows the app is ready (seeded, first render done).
    start=StartConfig(
        command="python3",
        args=["-m", "your_app"],
        # prerequisites=check_tools,  # a function that raises RuntimeError("What is missing and how to install it")
        # ready=lambda url: fetch(url).status == 200,  # fetch is in mole.runtime
        timeout_s=120,
    ),
    # <surface: api>
    api=ApiConfig(
        # TODO(proof): where the API answers. The default is the app URL; PROOF_API_URL overrides it.
        discover=lambda: os.environ.get("PROOF_URL", "http://localhost:3000"),
        # probe=lambda base_url: fetch(f"{base_url}/health").status == 200,
    ),
    # </surface: api>
    # <surface: web>
    web=WebConfig(
        # settle=lambda page: page.wait_for_load_state("load"),
        # snapshot=lambda page: {},  # what a user sees on this app's pages
    ),
    # </surface: web>
)
