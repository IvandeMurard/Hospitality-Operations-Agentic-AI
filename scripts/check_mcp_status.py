"""
Vérification rapide du statut MCP Obsidian
"""

import os
import json
from pathlib import Path

CONFIG_FILE = Path(os.getenv('APPDATA')) / 'Claude' / 'claude_desktop_config.json'
LOG_FILE = Path(os.getenv('APPDATA')) / 'Claude' / 'logs' / 'mcp-server-obsidian.log'
VAULT_PATH = r"C:\Users\IVAN\OneDrive\Documents\Agentic AI Hospitality"

print("=" * 70)
print("STATUT MCP OBSIDIAN")
print("=" * 70)

# Vérifier la configuration
print("\n1. CONFIGURATION:")
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if 'mcpServers' in config and 'obsidian' in config['mcpServers']:
            print("  [OK] Configuration presente")
            obsidian_config = config['mcpServers']['obsidian']
            print(f"  [OK] Command: {obsidian_config.get('command')}")
            args = obsidian_config.get('args', [])
            if args:
                # Identifier le serveur utilisé (premier arg = package, dernier arg = vault)
                # Supporte les deux formats : avec ou sans -y
                server_package = None
                for arg in args:
                    if arg.startswith("@") or arg.startswith("mcp-obsidian"):
                        server_package = arg
                        break
                
                if server_package:
                    print(f"  [OK] Serveur: {server_package}")
                    if "@mauricio.wolff/mcp-obsidian" in server_package:
                        print("  [OK] Serveur complet (create/write/patch notes supportes)")
                        if "@latest" in server_package:
                            print("  [OK] Version: latest (recommandee)")
                    elif "@bitbonsai/mcp-obsidian" in server_package:
                        print("  [ERREUR] Nom de package incorrect (utiliser @mauricio.wolff/mcp-obsidian)")
                    elif "mcp-obsidian" in server_package:
                        print("  [ATTENTION] Ancien serveur (read/search seulement)")
                else:
                    print(f"  [ATTENTION] Serveur non identifie dans args: {args}")
                
                # Le vault est toujours le dernier argument
                vault_path = args[-1] if args else 'N/A'
                print(f"  [OK] Vault: {vault_path}")
        else:
            print("  [ERREUR] Configuration obsidian manquante")
    except Exception as e:
        print(f"  [ERREUR] {e}")
else:
    print("  [ERREUR] Fichier de configuration non trouve")

# Vérifier le vault
print("\n2. VAULT OBSIDIAN:")
vault = Path(VAULT_PATH)
if vault.exists():
    print(f"  [OK] Vault existe: {VAULT_PATH}")
    if (vault / '.obsidian').exists():
        print("  [OK] Dossier .obsidian trouve (vault valide)")
else:
    print(f"  [ERREUR] Vault non trouve: {VAULT_PATH}")

# Vérifier les logs
print("\n3. LOGS MCP:")
if LOG_FILE.exists():
    try:
        content = LOG_FILE.read_text(encoding='utf-8', errors='ignore')
        lines = content.splitlines()
        print(f"  [OK] Fichier de log trouve ({len(lines)} lignes)")
        
        # Chercher des messages clés
        if "Server started and connected successfully" in content:
            print("  [OK] Serveur demarre et connecte avec succes")
        if "MCP Obsidian Server running" in content:
            print("  [OK] Serveur MCP Obsidian en cours d'execution")
        if "tools/list" in content:
            print("  [OK] Outils MCP disponibles")
            # Chercher les outils disponibles dans les logs
            if "create_note" in content or "write_note" in content:
                print("  [OK] Outils d'ecriture disponibles (create_note/write_note)")
            if "read_notes" in content:
                print("  [OK] Outil de lecture disponible (read_notes)")
            if "search_notes" in content:
                print("  [OK] Outil de recherche disponible (search_notes)")
        
        # Vérifier la version du protocole
        import re
        protocol_match = re.search(r'"protocolVersion"\s*:\s*"([^"]+)"', content)
        if protocol_match:
            protocol_version = protocol_match.group(1)
            print(f"  [INFO] Version protocole: {protocol_version}")
            if protocol_version == "2025-06-18":
                print("  [OK] Protocole compatible avec Claude Desktop!")
            elif protocol_version >= "2024-11-05":
                print(f"  [ATTENTION] Version {protocol_version} - peut fonctionner")
            else:
                print(f"  [ERREUR] Version trop ancienne: {protocol_version}")
        
        # Afficher les dernières lignes
        print(f"\n  Dernieres lignes du log:")
        for line in lines[-5:]:
            if line.strip():
                print(f"    {line[:100]}")
    except Exception as e:
        print(f"  [ERREUR] Impossible de lire le log: {e}")
else:
    print("  [INFO] Fichier de log non trouve (normal si Claude Desktop n'a pas encore demarre le serveur)")

print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print("""
Le serveur MCP Obsidian semble etre configure et fonctionnel selon les logs.

Pour verifier dans Claude Desktop:
1. Ouvrez Claude Desktop
2. Allez dans Settings > Developer
3. Verifiez que "obsidian" apparait dans la liste des serveurs MCP
4. Verifiez le statut (devrait etre "Connected" ou "Running")

Pour tester les outils MCP:
- Lecture: "Peux-tu lire la note [nom] de mon vault Obsidian?"
- Recherche: "Peux-tu chercher des notes sur [sujet] dans mon vault Obsidian?"
- Creation: "Peux-tu creer une note [nom] avec le contenu [contenu]?"
- Ecriture: "Peux-tu modifier la note [nom] pour ajouter [contenu]?"
""")
