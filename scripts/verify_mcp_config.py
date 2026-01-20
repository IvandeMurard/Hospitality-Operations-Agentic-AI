"""Vérifier que la configuration MCP utilise le bon nom de package"""

import os
import json
from pathlib import Path

CONFIG_FILE = Path(os.getenv('APPDATA')) / 'Claude' / 'claude_desktop_config.json'

if not CONFIG_FILE.exists():
    print("[ERREUR] Fichier de configuration non trouvé")
    exit(1)

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

server_package = config['mcpServers']['obsidian']['args'][1]

print(f"Serveur configuré: {server_package}")
print(f"Correct: {server_package == '@mauricio.wolff/mcp-obsidian'}")

if server_package == '@mauricio.wolff/mcp-obsidian':
    print("[OK] Configuration correcte!")
else:
    print(f"[ERREUR] Nom incorrect. Attendu: @mauricio.wolff/mcp-obsidian")
