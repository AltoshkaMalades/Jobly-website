$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$backupScript = Join-Path $projectRoot 'backup.sh'
$logFile = Join-Path $projectRoot 'backups/backup_schedule.log'
$logDir = Split-Path $logFile -Parent

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -Path $logFile -Value "[$timestamp] Starting backup"

$gitBash = 'C:\Program Files\Git\bin\bash.exe'
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue

try {
    if (Test-Path $gitBash) {
        & $gitBash $backupScript 2>&1 | Tee-Object -FilePath $logFile -Append
    }
    elseif ($wsl) {
        & $wsl.Source bash $backupScript 2>&1 | Tee-Object -FilePath $logFile -Append
    }
    else {
        $message = 'Neither Git Bash nor wsl.exe was found.'
        Add-Content -Path $logFile -Value $message
        throw $message
    }

    $completedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $logFile -Value "[$completedAt] Backup completed"
}
catch {
    $failedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $logFile -Value "[$failedAt] Backup failed: $($_.Exception.Message)"
    throw
}
