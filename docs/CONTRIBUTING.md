# Taskflow contribution guide

## Requirements
- Python 3.7+
- Make

## Initial setup
I recommend using a virtual environment (eg. virtualenv or conda) when you develop Taskflow, since dependencies are very tightly locked and may conflict with your global environment.

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements.dev.txt

# Setup pre-commit. This enables the black linter to run at every commit
pre-commit install
```

Using `black` with `pre-commit` is a bit quirky, in that if you run `git commit` and there are files that get reformatted with `black`, the commit will fail each time. You'll need to run `git commit -a` again for the changes to apply.

## Running tests
Tests are run using the `make test`. Internally, it uses `pytest` with the `pytest-cov` plugin to calculate coverage.

## Requesting changes
As usual, if you wish to request changes in Taskflow, fork the repository and submit a pull request against the master branch. I will try to go through them as much as I am able. Please make sure that your code is properly formatted with `black` (by enabling the commit hook) and all tests have passed.
