@echo off
setlocal

set python=python.exe

%python% -m mypy pysqlexpr || exit /b
%python% -m flake8 pysqlexpr || exit /b
%python% -m mypy tests || exit /b
%python% -m flake8 tests || exit /b

:quit
