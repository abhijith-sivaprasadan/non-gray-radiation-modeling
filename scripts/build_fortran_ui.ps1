$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ConsoleSource = Join-Path $Root "fortran_ui\radiation_portfolio_ui.f90"
$GuiSource = Join-Path $Root "fortran_ui\radiation_portfolio_gui.f90"
$ManifestResource = Join-Path $Root "fortran_ui\app.rc"
$BuildDir = Join-Path $Root "build"
$ConsoleExe = Join-Path $BuildDir "radiation_portfolio_ui.exe"
$GuiExe = Join-Path $BuildDir "radiation_portfolio_gui.exe"
$RootGuiExe = Join-Path $Root "radiation_portfolio_gui.exe"
$ManifestObj = Join-Path $BuildDir "app_manifest.o"

if (-not (Get-Command gfortran -ErrorAction SilentlyContinue)) {
    throw "gfortran was not found on PATH."
}
$WindresCmd = Get-Command windres -ErrorAction SilentlyContinue
if (-not $WindresCmd) {
    throw "windres was not found on PATH (expected alongside gfortran in the MinGW toolchain)."
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

# windres.exe's internal preprocessor invocation (it shells out to gcc/cpp via popen) breaks
# whenever any path involved - its own install dir, the .rc file, or --include-dir - contains a
# space: it silently produces no object file (exit 0, no error) or fails with fatal errors like
# "cc1.exe: fatal error: Radiation\: No such file or directory" from the space getting split as
# a separate argument. Both "C:\Program Files (x86)\..." (the toolchain) and this project's own
# "E:\Thermal Radiation Modeling\..." trigger it. Fix both: invoke windres via its short (8.3)
# path (so it resolves its own directory, and its co-located gcc.exe, space-free), and run it
# from a space-free temp directory with the .rc file copied alongside it.
Add-Type -TypeDefinition @"
using System.Text;
using System.Runtime.InteropServices;
public class RadiationPortfolioShortPath {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
    public static extern int GetShortPathName(string path, StringBuilder shortPath, int size);
}
"@ -ErrorAction SilentlyContinue
$ShortPathBuffer = New-Object System.Text.StringBuilder 260
[void][RadiationPortfolioShortPath]::GetShortPathName($WindresCmd.Source, $ShortPathBuffer, 260)
$WindresShortPath = $ShortPathBuffer.ToString()

$ResourceTempDir = Join-Path $env:TEMP "radiation_portfolio_fortran_build"
New-Item -ItemType Directory -Force -Path $ResourceTempDir | Out-Null
Copy-Item -Path $ManifestResource -Destination $ResourceTempDir -Force
Copy-Item -Path (Join-Path $Root "fortran_ui\app.manifest") -Destination $ResourceTempDir -Force
$TempManifestObj = Join-Path $ResourceTempDir "app_manifest.o"

Push-Location $ResourceTempDir
try {
    & $WindresShortPath "app.rc" -O coff -o "app_manifest.o"
} finally {
    Pop-Location
}
if (-not (Test-Path $TempManifestObj)) {
    throw "windres did not produce $TempManifestObj from $ManifestResource."
}
Copy-Item -Path $TempManifestObj -Destination $ManifestObj -Force
& gfortran -std=f2008 -Wall -Wextra -O2 -ffree-line-length-none -J $BuildDir -o $ConsoleExe $ConsoleSource
& gfortran -std=f2008 -Wall -Wextra -O2 -ffree-line-length-none -J $BuildDir -o $GuiExe $GuiSource $ManifestObj `
    -mwindows -luser32 -lgdi32 -lkernel32 -lshell32 -lcomctl32 -lgdiplus -ldwmapi

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
