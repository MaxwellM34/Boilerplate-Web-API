$venvPath = Join-Path $PWD ".venv"
$env:WATCHFILES_IGNORE_PATHS = $venvPath

uvicorn main:app --reload `
  --reload-dir auth `
  --reload-dir config `
  --reload-dir models `
  --reload-dir routers `
  --reload-dir main.py `
  --reload-include "*.py"
