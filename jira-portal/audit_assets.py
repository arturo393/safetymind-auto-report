import requests
from bs4 import BeautifulSoup
import sys

def audit_assets(url):
    print(f"🔍 Iniciando Auditoría de Activos en: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fallo crítico: La página raíz devolvió {response.status_code}")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        assets = []
        
        # Extraer Scripts
        for script in soup.find_all('script'):
            if script.get('src'):
                assets.append(script.get('src'))
        
        # Extraer CSS
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                assets.append(link.get('href'))
        
        print(f"📦 Detectados {len(assets)} activos estáticos. Verificando integridad...")
        
        errors = 0
        for asset in assets:
            asset_url = asset if asset.startswith('http') else f"{url.rstrip('/')}/{asset.lstrip('/')}"
            res = requests.head(asset_url)
            if res.status_code >= 400:
                print(f"❌ ERROR {res.status_code}: {asset_url}")
                errors += 1
            else:
                print(f"✅ OK: {asset_url}")
        
        if errors > 0:
            print(f"⚠️ Resumen: Se encontraron {errors} errores de carga.")
            return False
        
        print("🟢 Integridad de activos nominal.")
        return True

    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
    success = audit_assets(base_url)
    sys.exit(0 if success else 1)
