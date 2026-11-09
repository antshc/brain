import pytest

from atl_cli import config
from atl_cli.jira_client import get_jira


@pytest.mark.parametrize("found", ["5.0.5", "5.2.1"])
def test_supported_versions_pass(found):
    assert config.version_error(found) is None


@pytest.mark.parametrize("found", ["4.0.7", None])
def test_unsupported_version_exits_with_the_init_atl_message(monkeypatch, found):
    monkeypatch.setattr(config, "installed_version", lambda: found)

    with pytest.raises(SystemExit) as excinfo:
        get_jira({"site": "s.example", "email": "e", "token": "t"})

    assert str(excinfo.value) == f"atlassian-python-api >=5.0.5 required, found {found or 'none'}; follow Brain's plugins/atl/install/install.md in Copilot CLI"
