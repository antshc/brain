# The engine's own checks (maps in step with the registry, surfaces valid) live in the engine.
from .engine.selftest import *  # noqa: F401,F403

# Add unit tests for your surface adapters below, with a fake `fetcher` for the API adapter, for example:
#   from .features.surfaces import api_surface
