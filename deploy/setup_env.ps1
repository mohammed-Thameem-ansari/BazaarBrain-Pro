<#
Setup environment files for local dev.
- Copies .env.example to .env if missing
- Creates frontend/.env.local with NEXT_PUBLIC_* vars

Usage (PowerShell):
  ./deploy/setup_env.ps1 -ApiBaseUrl http://localhost:8000 -SupabaseUrl https://xyz.supabase.co -SupabaseAnonKey sk_...
#>
param(
  [string]$ApiBaseUrl = "http://localhost:8000",
  [string]$SupabaseUrl = "",
  [string]$SupabaseAnonKey = ""
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Join-Path $root ".."
Set-Location $repo

# Root .env
if (!(Test-Path ".env")) {
  if (Test-Path ".env.example") {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
  } else {
    Write-Host ".env.example not found; skipping root .env creation"
  }
}

# Frontend .env.local
$frontendDir = Join-Path $repo "frontend"
$frontendEnv = Join-Path $frontendDir ".env.local"
$lines = @(
  "NEXT_PUBLIC_SUPABASE_URL=$SupabaseUrl",
  "NEXT_PUBLIC_SUPABASE_KEY=$SupabaseAnonKey",
  "NEXT_PUBLIC_API_BASE_URL=$ApiBaseUrl"
)
$lines -join "`r`n" | Out-File -FilePath $frontendEnv -Encoding utf8
Write-Host "Wrote frontend .env.local"
