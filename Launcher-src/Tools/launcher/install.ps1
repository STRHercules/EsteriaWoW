$ErrorActionPreference = 'Stop'

$here      = Split-Path -Parent $MyInvocation.MyCommand.Path
$nodeDir   = Join-Path $here 'node'
$mainDir   = Split-Path -Parent (Split-Path -Parent $here) 
$distDir   = Join-Path $mainDir 'dist'

$nodeVersion = '20.18.1'
$nodeZipName = "node-v$nodeVersion-win-x64.zip"
$nodeUrl     = "https://nodejs.org/dist/v$nodeVersion/$nodeZipName"
$nodeExe     = Join-Path $nodeDir "node-v$nodeVersion-win-x64\node.exe"

if (Test-Path $nodeExe) {
    Write-Host "Node.js already present at $nodeExe." -ForegroundColor Yellow
} else {
    if (-not (Test-Path $nodeDir)) { New-Item -ItemType Directory -Path $nodeDir | Out-Null }
    $zipPath = Join-Path $nodeDir $nodeZipName
    Write-Host "Downloading Node.js $nodeVersion (~30 MB)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $nodeUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "Extracting to $nodeDir..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $nodeDir -Force
    Remove-Item $zipPath
}

$nodeBinDir = Split-Path -Parent $nodeExe
$env:PATH   = "$nodeBinDir;$env:PATH"

Write-Host ""
Write-Host "node : $(& $nodeExe --version)" -ForegroundColor Green
Write-Host "npm  : $(& (Join-Path $nodeBinDir 'npm.cmd') --version)" -ForegroundColor Green

Write-Host ""
Write-Host "Building Electron launcher at $mainDir..." -ForegroundColor Cyan
Push-Location $mainDir
try {
    if (-not (Test-Path (Join-Path $mainDir 'node_modules'))) {
        Write-Host "[npm] install --ignore-scripts (JS packages only)" -ForegroundColor Cyan
        & (Join-Path $nodeBinDir 'npm.cmd') install --ignore-scripts --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

        Write-Host "[electron] install binary" -ForegroundColor Cyan
        & $nodeExe (Join-Path $mainDir 'node_modules\electron\install.js')
        if ($LASTEXITCODE -ne 0) { throw "electron install failed" }

        Write-Host "[electron-builder] install-app-deps (native modules)" -ForegroundColor Cyan
        & (Join-Path $mainDir 'node_modules\.bin\electron-builder.cmd') install-app-deps
        if ($LASTEXITCODE -ne 0) { throw "electron-builder install-app-deps failed" }
    } else {
        Write-Host "node_modules already exists - skipping npm install (delete it to force reinstall)." -ForegroundColor Yellow
    }

    Write-Host "[npm] run build (electron-vite)" -ForegroundColor Cyan
    & (Join-Path $nodeBinDir 'npm.cmd') run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

    Write-Host "[npm] run pack (electron-builder -> dist\)" -ForegroundColor Cyan
    & (Join-Path $nodeBinDir 'npm.cmd') run pack
    if ($LASTEXITCODE -ne 0) { throw "npm run pack failed" }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
if (Test-Path $distDir) {
    Get-ChildItem $distDir -Filter '*.exe' | ForEach-Object {
        $size = [math]::Round($_.Length / 1MB, 1)
        Write-Host "  $($_.FullName)  ($size MB)" -ForegroundColor Green
    }
}
Write-Host ""
