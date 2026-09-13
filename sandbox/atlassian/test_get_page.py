import unittest

from sandbox.atlassian.get_page import confluence_api_url, require_environment


class ConfluenceApiUrlTests(unittest.TestCase):
    def test_uses_v2_page_endpoint(self):
        assert confluence_api_url("https://antshc.atlassian.net", "131406") == (
            "https://antshc.atlassian.net/wiki/api/v2/pages/131406?body-format=storage"
        )

    def test_accepts_a_site_url_that_already_includes_wiki(self):
        assert confluence_api_url("https://antshc.atlassian.net/wiki", "131406") == (
            "https://antshc.atlassian.net/wiki/api/v2/pages/131406?body-format=storage"
        )

    def test_missing_environment_value_names_only_the_key(self):
        with self.assertRaisesRegex(SystemExit, "ATLASSIAN_EMAIL"):
            require_environment("ATLASSIAN_EMAIL")
