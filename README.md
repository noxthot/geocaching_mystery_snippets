# geocaching_mystery_snippets
Snippets which help(ed) to solve some www.geocaching.com mystery caches.
Mainly early prototype code to get things done (quick and dirty).

## Setup
### Conda
Use conda to install all required modules (default environment: `geocaching_mystery_snippets`):
```
conda env create -f environment.yml
```

In case you already got the environment and only need to update to the latest `environment.yml` use:
```
conda activate geocaching_mystery_snippets
conda env update --file environment.yml --prune
```

After manually adding a package, update the `environment.yml` using this command:
```
conda env export --name geocaching_mystery_snippets > environment.yml
```