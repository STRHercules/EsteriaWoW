$ErrorActionPreference = 'Stop'
$buildScript = Join-Path $PSScriptRoot 'build-server.ps1'
$global:esteriaBuildTestExitCode = 0

function docker {
    $global:esteriaBuildTestArguments = @($args)
    $global:LASTEXITCODE = $global:esteriaBuildTestExitCode
}

function Assert-Arguments([string[]]$Expected) {
    if (($global:esteriaBuildTestArguments -join '|') -cne ($Expected -join '|')) {
        throw "Unexpected Docker arguments: $($global:esteriaBuildTestArguments -join ' ')"
    }
}

& $buildScript
Assert-Arguments @(
    'exec', 'housing-build', 'cmake', '--build', '/azerothcore/build', '--target', 'worldserver', '--parallel'
)

& $buildScript -Target authserver -Container test-builder
Assert-Arguments @(
    'exec', 'test-builder', 'cmake', '--build', '/azerothcore/build', '--target', 'authserver', '--parallel'
)

& $buildScript -Target dbimport -DryRun
Assert-Arguments @(
    'exec', 'housing-build', 'ninja', '-C', '/azerothcore/build', '-n', '-d', 'explain', 'dbimport'
)

$global:esteriaBuildTestExitCode = 7
$failed = $false
try {
    & $buildScript
}
catch {
    if ($_.Exception.Message -notlike '*exit 7*') { throw }
    $failed = $true
}
if (!$failed) { throw 'Docker failure was not reported.' }

Write-Output 'PASS: focused targets, dry run, and failure reporting (Docker mocked).'
