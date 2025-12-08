"""
Script de test pour vérifier les connexions Claude et Qdrant
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from utils.claude_client import ClaudeClient
from utils.qdrant_client import QdrantManager


async def test_claude():
    """Test de la connexion Claude"""
    print("\n" + "="*60)
    print("TEST DE LA CONNEXION CLAUDE API")
    print("="*60)
    
    try:
        async with ClaudeClient() as client:
            print("[OK] Client Claude créé avec succès")
            result = await client.test_connection()
            
            if result["status"] == "success":
                print(f"[OK] Connexion réussie!")
                print(f"  Modèle: {result.get('model', 'N/A')}")
                print(f"  Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"[ERROR] Erreur de connexion: {result.get('message', 'Unknown error')}")
                return False
    except ValueError as e:
        print(f"[ERROR] Erreur de configuration: {e}")
        print("  Assurez-vous d'avoir défini ANTHROPIC_API_KEY dans votre fichier .env")
        return False
    except Exception as e:
        print(f"[ERROR] Erreur inattendue: {type(e).__name__}: {e}")
        return False


async def test_qdrant():
    """Test de la connexion Qdrant"""
    print("\n" + "="*60)
    print("TEST DE LA CONNEXION QDRANT")
    print("="*60)
    
    try:
        manager = QdrantManager()
        print(f"[OK] Client Qdrant créé avec succès (mode: {manager.mode})")
        
        result = await manager.test_connection()
        
        if result["status"] == "success":
            print(f"[OK] Connexion réussie!")
            print(f"  Mode: {result.get('mode', 'N/A')}")
            print(f"  Collections: {result.get('collections', 0)}")
            print(f"  Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Erreur de connexion: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"[ERROR] Erreur inattendue: {type(e).__name__}: {e}")
        return False


async def main():
    """Fonction principale de test"""
    print("\n" + "="*60)
    print("TESTS DE CONNEXION DES APIs")
    print("="*60)
    
    results = {}
    
    # Test Claude
    results["claude"] = await test_claude()
    
    # Test Qdrant
    results["qdrant"] = await test_qdrant()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"Claude API:  {'[OK] SUCCÈS' if results['claude'] else '[ERROR] ÉCHEC'}")
    print(f"Qdrant:      {'[OK] SUCCÈS' if results['qdrant'] else '[ERROR] ÉCHEC'}")
    
    if all(results.values()):
        print("\n[SUCCESS] Tous les tests sont passés avec succès!")
        return 0
    else:
        print("\n[WARNING] Certains tests ont échoué. Vérifiez votre configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

