[CmdletBinding()]
param(
    [ValidateSet('worldserver', 'authserver', 'dbimport')]
    [string]$Target = 'worldserver',
    [string]$Container = 'housing-build',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

if ($DryRun) {
    $dockerArguments = @('exec', $Container, 'ninja', '-C', '/azerothcore/build', '-n', '-d', 'explain', $Target)
}
else {
    $dockerArguments = @(
        'exec', $Container, 'cmake', '--build', '/azerothcore/build', '--target', $Target, '--parallel'
    )
}

& docker @dockerArguments
if ($LASTEXITCODE -ne 0) {
    throw "Build command failed in '$Container' (exit $LASTEXITCODE)."
}
