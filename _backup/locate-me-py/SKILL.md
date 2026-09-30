---
name: locate-me-py
description: Locate me.txt in the repository containing this installed skill, independent of cwd or nested Git repositories, using a minimal inline Python one-liner instead of a separate script file. Use when a script-free, Python-based variant of locate-me is needed.
---

# Locate Me Py

Run python script from this skill's base directory.

```python
import json, os; 
from pathlib import Path; 
print(json.dumps({'harnessLocation': str(Path(os.getcwd()).parents[2]), 'atlassian': json.loads(Path('.atlassian.json.user').read_text())}))
```

Return the printed JSON. Report a exit code when the `.atlassian.json.user` file is not found.
