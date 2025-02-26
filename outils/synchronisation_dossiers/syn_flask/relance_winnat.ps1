<#
.SYNOPSIS
    Redémarre le service Windows NAT (winnat) avec des privilèges administrateur.

.DESCRIPTION
    Ce script PowerShell vérifie d'abord s'il est exécuté avec des privilèges administrateur.
    Si ce n'est pas le cas, il se relance automatiquement en tant qu'administrateur.
    Une fois les privilèges obtenus, il arrête puis redémarre le service winnat.

    Le service Windows NAT (Network Address Translation) est un composant crucial qui :
    - Permet la traduction d'adresses réseau entre différents réseaux
    - Gère le routage des paquets entre les conteneurs Docker et l'hôte Windows
    - Facilite la communication entre les applications conteneurisées et le réseau local

    Pourquoi redémarrer winnat ?
    - Résout les problèmes de connexion avec les conteneurs Docker
    - Rétablit la communication réseau après des modifications de configuration
    - Libère les ports bloqués ou en état "TIME_WAIT"
    - Corrige les erreurs de liaison de ports (port binding errors)

    Erreurs courantes résolues par le redémarrage :
    - "port is already allocated"
    - "cannot start service [...] ports are not available"
    - "The process cannot access the file because it is being used by another process"
    - Erreurs de connexion entre conteneurs
    - Timeouts lors des requêtes réseau

.NOTES
    Nom du fichier    : relance_winnat.ps1
    Auteur           : bigmoletos
    Date de création : 2024-02-21
    Version          : 1.0

    Prérequis:
    - Windows 10/11
    - PowerShell 5.1 ou supérieur
    - Droits administrateur
    - Docker Desktop pour Windows (si utilisation avec Docker)

    Impact du redémarrage :
    - Interruption temporaire des connexions réseau des conteneurs
    - Durée moyenne du redémarrage : 5-10 secondes
    - Peut nécessiter le redémarrage des conteneurs affectés

.EXAMPLE
    .\relance_winnat.ps1
    Lance le script et redémarre le service winnat.

.OUTPUTS
    Messages de statut colorés indiquant la progression et le résultat du redémarrage.
    - Jaune : Arrêt du service en cours
    - Vert : Démarrage du service en cours
    - Cyan : Confirmation de succès
    - Rouge : Erreurs éventuelles

.LINK
    https://learn.microsoft.com/fr-fr/powershell/module/nettcpip/get-netnat
    https://docs.docker.com/desktop/networking/
#>

# Vérification des privilèges administrateur
# Si le script n'est pas exécuté en tant qu'administrateur, on le relance avec élévation
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Warning "Relancer le script en tant qu'administrateur..."
    # Relance le script avec des privilèges élevés
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Arrêt du service winnat
Write-Host "Arrêt du service winnat..." -ForegroundColor Yellow
try {
    net stop winnat
    Write-Host "Service winnat arrêté avec succès" -ForegroundColor Yellow
} catch {
    Write-Host "Erreur lors de l'arrêt du service winnat: $_" -ForegroundColor Red
    exit 1
}

# Attente courte pour assurer la libération complète des ressources
Start-Sleep -Seconds 2

# Démarrage du service winnat
Write-Host "Démarrage du service winnat..." -ForegroundColor Green
try {
    net start winnat
    Write-Host "Service winnat démarré avec succès" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors du démarrage du service winnat: $_" -ForegroundColor Red
    exit 1
}

# Confirmation de fin d'exécution
Write-Host "Le service winnat a été redémarré avec succès." -ForegroundColor Cyan
Write-Host "Les connexions réseau des conteneurs devraient maintenant fonctionner correctement." -ForegroundColor Cyan