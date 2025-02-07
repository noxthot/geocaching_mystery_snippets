# geocaching_mystery_snippets
Snippets which help(ed) to solve some www.geocaching.com mystery caches.
Mainly early prototype code to get things done (quick and dirty).

## Setup
### System
For clipboarding in `webscraper_powertrail`, you will need:
```bash
sudo apt-get install xclip
```

### PDM
Use `pdm` to install/sync all required modules:
```bash
pdm sync
```

To run code / `IPython` / `jupyter lab` in this environment:
```bash
pdm run python <SCRIPT.py>

pdm run ipython

pdm run jupyter lab
```

To add a package:
```bash
pdm add <PACKAGE_NAME>
```
