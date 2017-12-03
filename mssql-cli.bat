@echo off
setlocal
REM Set the python io encoding to UTF-8 by default if not set.
IF "%PYTHONIOENCODING%"=="" (
    SET PYTHONIOENCODING="UTF-8"
)
SET PYTHONPATH=%~dp0;%PYTHONPATH%
python -m mssqlcli.main %*

endlocal