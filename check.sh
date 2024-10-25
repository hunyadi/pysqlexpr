set -e

PYTHON=python3

# Run static type checker and verify formatting guidelines
$PYTHON -m mypy pysqlexpr
$PYTHON -m flake8 pysqlexpr
$PYTHON -m mypy tests
$PYTHON -m flake8 tests
