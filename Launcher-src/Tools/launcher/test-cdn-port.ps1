$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Read-ProjectFile([string]$relativePath) {
  return Get-Content -Raw -LiteralPath (Join-Path $root $relativePath)
}

function Assert-Contains([string]$relativePath, [string]$expected) {
  $content = Read-ProjectFile $relativePath
  if (-not $content.Contains($expected)) {
    throw "$relativePath does not contain: $expected"
  }
}

Assert-Contains '.env.example' 'MAIN_VITE_SERVER_URL=http://127.0.0.1:7384'
Assert-Contains '.env.production' 'MAIN_VITE_SERVER_URL=http://127.0.0.1:7384'
Assert-Contains 'src/common/config.ts' "http://127.0.0.1:7384"
Assert-Contains 'server/src/index.ts' 'const port = 7384;'
Assert-Contains 'server/src/index.ts' "app.use('/launcher-updates', express.static(LauncherUpdatesDir));"
Assert-Contains 'server/Dockerfile' 'EXPOSE 7384'
Assert-Contains 'server/Dockerfile' 'LAUNCHER_UPDATES_DIR=/srv/launcher-updates'
Assert-Contains 'electron-builder.yml' 'icon: build/icon.png'

foreach ($relativePath in @('README.md', 'BUILD.md', 'CDN-SETUP-WINDOWS10.md')) {
  $content = Read-ProjectFile $relativePath
  if ($content.Contains('5000')) {
    throw "$relativePath still references the old CDN port 5000"
  }
}

Write-Output 'CDN port contract passed.'
