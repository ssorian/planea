# Instalador de la skill «planea» para Windows (PowerShell 5.1 o 7+).
# Uso:
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 [-Destino pi|claude|agents|todos|RUTA] [-Enlace] [-SinDependencias] [-Desinstalar]
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/ssorian/planea/main/install.ps1))) [-Destino claude]
[CmdletBinding()]
param(
  [string]$Destino = "",
  [switch]$Enlace,
  [switch]$SinDependencias,
  [switch]$Desinstalar
)
$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/ssorian/planea.git"
$Nombre = "planea"

function Get-Carpeta([string]$d) {
  switch ($d) {
    "pi"     { return Join-Path $HOME ".pi\agent\skills" }
    "claude" { return Join-Path $HOME ".claude\skills" }
    "agents" { return Join-Path $HOME ".agents\skills" }
    default  { return $d }
  }
}

$destinos = @()
if ([string]::IsNullOrEmpty($Destino)) {
  foreach ($d in "pi", "claude", "agents") {
    $c = Get-Carpeta $d
    if (Test-Path $c -PathType Container) { $destinos += $c }
  }
  if ($destinos.Count -eq 0) { $destinos = @(Get-Carpeta "pi") }
} elseif ($Destino -eq "todos") {
  $destinos = @((Get-Carpeta "pi"), (Get-Carpeta "claude"), (Get-Carpeta "agents"))
} else {
  $destinos = @(Get-Carpeta $Destino)
}

if ($Desinstalar) {
  foreach ($base in $destinos) {
    $obj = Join-Path $base $Nombre
    if (Test-Path $obj) {
      $item = Get-Item $obj -Force
      if ($item.LinkType) { $item.Delete() } else { Remove-Item $obj -Recurse -Force }
      Write-Host "Eliminada: $obj"
    }
  }
  return
}

# Localizar el código: clon local o descarga temporal.
$origen = $null
$tmp = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "skills\$Nombre\SKILL.md"))) {
  $origen = Join-Path $PSScriptRoot "skills\$Nombre"
} else {
  if ($Enlace) { throw "-Enlace requiere ejecutar el instalador desde un clon local." }
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ("planea-" + [guid]::NewGuid())
  if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone --depth 1 -q $RepoUrl (Join-Path $tmp "planea")
  } else {
    New-Item -ItemType Directory -Path $tmp | Out-Null
    $zip = Join-Path $tmp "planea.zip"
    Invoke-WebRequest "https://github.com/ssorian/planea/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
    Expand-Archive $zip -DestinationPath $tmp
    Rename-Item (Join-Path $tmp "planea-main") "planea"
  }
  $origen = Join-Path $tmp "planea\skills\$Nombre"
}

function Install-Dependencias([string]$skill) {
  if ($SinDependencias) { return }
  $gestor = $null
  if (Get-Command bun -ErrorAction SilentlyContinue) { $gestor = @("bun", "install") }
  elseif (Get-Command npm -ErrorAction SilentlyContinue) { $gestor = @("npm", "install", "--no-audit", "--no-fund") }
  else { Write-Warning "No hay bun ni npm; los kits no tendrán dependencias."; return }
  foreach ($kit in @("kit-recursos")) {
    $dir = Join-Path $skill "assets\$kit"
    if (Test-Path (Join-Path $dir "package.json")) {
      Write-Host "Instalando dependencias de $kit…"
      Push-Location $dir
      try { & $gestor[0] $gestor[1..($gestor.Length - 1)] | Out-Null } finally { Pop-Location }
    }
  }
}

try {
  $primero = $true
  foreach ($base in $destinos) {
    New-Item -ItemType Directory -Force -Path $base | Out-Null
    $obj = Join-Path $base $Nombre
    if (Test-Path $obj) {
      $item = Get-Item $obj -Force
      $skillMd = Join-Path $obj "SKILL.md"
      if ($item.LinkType) { $item.Delete() }
      elseif ((Test-Path $skillMd) -and (Select-String -Path $skillMd -Pattern "^name: $Nombre$" -Quiet)) { Remove-Item $obj -Recurse -Force }
      else { throw "$obj existe y no es una instalación de $Nombre; no se sobrescribe." }
    }
    if ($Enlace) {
      # Unión de directorio: no requiere modo de desarrollador ni permisos de administrador.
      New-Item -ItemType Junction -Path $obj -Target $origen | Out-Null
      if ($primero) { Install-Dependencias $origen }
    } else {
      New-Item -ItemType Directory -Path $obj | Out-Null
      Get-ChildItem $origen -Force | Where-Object { $_.Name -notin @("node_modules", "dist") } | ForEach-Object {
        Copy-Item $_.FullName -Destination $obj -Recurse -Force
      }
      Get-ChildItem $obj -Recurse -Directory -Force | Where-Object { $_.Name -in @("node_modules", "dist") } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
      Install-Dependencias $obj
    }
    $primero = $false
    Write-Host "Instalada: $obj"
  }
} finally {
  if ($tmp -and (Test-Path $tmp)) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host "Requisitos detectados:"
foreach ($h in "bun", "python", "py", "pdftoppm") {
  $ok = [bool](Get-Command $h -ErrorAction SilentlyContinue)
  Write-Host ("  {0} {1}" -f ($(if ($ok) { "OK" } else { "--" })), $h)
}
$nav = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { $_ -and (Test-Path $_) }
if ($nav) { Write-Host "  OK navegador: $($nav[0])" } else { Write-Warning "Sin Chrome ni Edge no se pueden generar PDF ni capturas." }
