## Prerequisites
- User must have `acli` installed with the [installation guide](https://developer.atlassian.com/cloud/acli/guides/install-linux/#install-binary-with-curl-on-linux). 
- User must authenticate with `acli` before running this skill, using `echo "<api_token>" | acli confluence auth login --token --email user@hpe.com --site zerto.atlassian.net` with `Api token` and following the prompts to connect to the Confluence instance.
- User must install pip dependencies for the markdown conversion script, using `pip install -r <skill-directory>/scripts/requirements.txt`