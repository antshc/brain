import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / 'page_view_json_to_text.py'
PAGE_RESPONSE_JSON = Path(__file__).parent / 'page_response.json'


def run_script(input_json: str, via_stdin: bool = False) -> subprocess.CompletedProcess:
    if via_stdin:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=input_json,
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        [sys.executable, str(SCRIPT), input_json],
        capture_output=True,
        text=True,
    )


class TestPageViewJsonToText:
    def test_extracts_text_from_page_response_json_argument(self):
        raw = PAGE_RESPONSE_JSON.read_text()
        result = run_script(raw)
        assert result.returncode == 0
        output = result.stdout
        assert 'General' in output
        assert 'Does the implementation meet the requirement' in output
        assert 'Any hard-coded secrets' in output

    def test_extracts_text_from_page_response_json_stdin(self):
        raw = PAGE_RESPONSE_JSON.read_text()
        result = run_script(raw, via_stdin=True)
        assert result.returncode == 0
        output = result.stdout
        assert 'General' in output
        assert 'Does the implementation meet the requirement' in output

    def test_output_contains_no_html_tags(self):
        raw = PAGE_RESPONSE_JSON.read_text()
        result = run_script(raw)
        assert result.returncode == 0
        assert '<' not in result.stdout
        assert '>' not in result.stdout

    def test_no_excessive_blank_lines(self):
        raw = PAGE_RESPONSE_JSON.read_text()
        result = run_script(raw)
        assert result.returncode == 0
        assert '\n\n\n' not in result.stdout

    def test_missing_input_exits_with_error(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            input='',
            env={**__import__('os').environ, 'PYTHONUNBUFFERED': '1'},
        )
        assert result.returncode != 0

    def test_invalid_json_raises_error(self):
        result = run_script('not valid json')
        assert result.returncode != 0
