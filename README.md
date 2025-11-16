# geocaching_mystery_snippets
Snippets which help(ed) to solve some www.geocaching.com mystery caches.
Mainly early prototype code to get things done (quick and dirty).

## Setup
### System
For clipboarding in `webscraper_powertrail`, you will need:
```bash
sudo apt-get install xclip
```

### uv
Use `uv` to install/sync all required modules:
```bash
uv sync
```

To run code / `IPython` / `jupyter lab` in this environment:
```bash
uv run python <SCRIPT.py>

uv run ipython

uv run jupyter lab
```

To add a package:
```bash
uv add <PACKAGE_NAME>
```
