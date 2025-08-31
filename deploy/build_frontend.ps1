# Frontend production build (PowerShell)
# Usage (from repo root):
#   pwsh -File deploy/build_frontend.ps1
#   PowerShell 5+: powershell.exe -ExecutionPolicy Bypass -File deploy/build_frontend.ps1

$ErrorActionPreference = 'Stop'

Write-Host "[build_frontend.ps1] Starting..."

Push-Location frontend
try {
  $env:NODE_ENV = 'production'
  if (-not (Test-Path '.env.production')) {
    Write-Error ".env.production not found in frontend/. Create it before building."
  }

  Write-Host "[build_frontend.ps1] Installing dependencies..."
  try {
    npm ci | Out-Null
  } catch {
    Write-Host "[build_frontend.ps1] npm ci failed, falling back to npm install"
    npm install | Out-Null
  }

  Write-Host "[build_frontend.ps1] Building Next.js app..."
  npm run build | Out-Null

  Write-Host "[build_frontend.ps1] Build complete. Output: frontend/.next"
}
finally {
  Pop-Location
}
