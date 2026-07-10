$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ConsoleSource = Join-Path $Root "fortran_ui\radiation_portfolio_ui.f90"
$GuiSource = Join-Path $Root "fortran_ui\radiation_portfolio_gui.f90"
$BuildDir = Join-Path $Root "build"
$ConsoleExe = Join-Path $BuildDir "radiation_portfolio_ui.exe"
$GuiExe = Join-Path $BuildDir "radiation_portfolio_gui.exe"
$RootGuiExe = Join-Path $Root "radiation_portfolio_gui.exe"

if (-not (Get-Command gfortran -ErrorAction SilentlyContinue)) {
    throw "gfortran was not found on PATH."
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
& gfortran -std=f2008 -Wall -Wextra -O2 -ffree-line-length-none -J $BuildDir -o $ConsoleExe $ConsoleSource
& gfortran -std=f2008 -Wall -Wextra -O2 -ffree-line-length-none -J $BuildDir -o $GuiExe $GuiSource -mwindows -luser32 -lgdi32 -lkernel32 -lshell32

$CompilerDir = Split-Path -Parent (Get-Command gfortran).Source
$RuntimeDlls = @(
    "libgfortran-5.dll",
    "libgcc_s_seh-1.dll",
    "libquadmath-0.dll",
    "libwinpthread-1.dll"
)

foreach ($Dll in $RuntimeDlls) {
    $SourceDll = Join-Path $CompilerDir $Dll
    if (Test-Path $SourceDll) {
        Copy-Item -Path $SourceDll -Destination $BuildDir -Force
        Copy-Item -Path $SourceDll -Destination $Root -Force
    }
}

Copy-Item -Path $GuiExe -Destination $RootGuiExe -Force

Write-Host "Built $ConsoleExe"
Write-Host "Built $GuiExe"
Write-Host "Copied launch-ready GUI to $RootGuiExe"
