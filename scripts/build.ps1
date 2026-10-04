$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        & $py.Source -3 scripts/render_data.py
    } else {
        throw "Python 3 is required to generate the structured content."
    }
} else {
    & $python.Source scripts/render_data.py
}
if ($LASTEXITCODE -ne 0) { throw "Content generation failed (exit $LASTEXITCODE)." }

$quarto = if ($env:QUARTO_BIN) { $env:QUARTO_BIN } else { (Get-Command quarto -ErrorAction SilentlyContinue).Source }
if (-not $quarto) {
    throw "Quarto 1.9.38 is required. Set QUARTO_BIN or add quarto to PATH."
}

& $quarto render
if ($LASTEXITCODE -ne 0) { throw "Quarto rendering failed (exit $LASTEXITCODE). Output was not validated or published." }

if ($python) {
    & $python.Source scripts/validate.py
} else {
    & $py.Source -3 scripts/validate.py
}
if ($LASTEXITCODE -ne 0) { throw "Site validation failed (exit $LASTEXITCODE)." }
