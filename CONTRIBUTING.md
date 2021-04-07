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

# Setup pre-commit
pre-commit install
```
