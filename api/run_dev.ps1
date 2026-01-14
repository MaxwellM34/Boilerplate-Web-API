$venvPath = Join-Path $PWD ".venv"
$env:WATCHFILES_IGNORE_PATHS = $venvPath

$uvicornArgs = @(
  "main:app",
  "--reload",
  "--reload-dir", ".",
  "--reload-include", "*.py",
  "--reload-exclude", ".venv"
)

& uvicorn @uvicornArgs
