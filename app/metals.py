import pandas as pd
import requests
from datetime import datetime

# ============================================================================
# OPTION 1: CME DataMine (Gratuit - Source officielle des futures)
# ============================================================================

def get_cme_futures_official(metal='GC'):
    """
    CME Group - Source officielle et gratuite des contrats futures
    """
    
    print(f"\n{'='*90}")
    print(f"  CME GROUP - CONTRATS FUTURES {metal}")
    print(f"{'='*90}\n")
    
    # URL de l'API publique CME
    url = f"https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/{metal}/G"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            contracts = []
            
            if 'quotes' in data:
                for quote in data['quotes']:
                    contract = {
                        'Contrat': quote.get('expirationMonth', 'N/A'),
                        'Code': quote.get('code', 'N/A'),
                        'Dernier_Prix': quote.get('last', 'N/A'),
                        'Variation': quote.get('change', 'N/A'),
                        'Settlement': quote.get('settle', 'N/A'),
                        'Volume': quote.get('volume', 'N/A'),
                        'Open_Interest': quote.get('openInterest', 'N/A'),
                        'Plus_Haut': quote.get('high', 'N/A'),
                        'Plus_Bas': quote.get('low', 'N/A')
                    }
                    contracts.append(contract)
                
                if contracts:
                    df = pd.DataFrame(contracts)
                    print(df.to_string(index=False))
                    return df
                else:
                    print("❌ Aucun contrat trouvé")
                    return None
            else:
                print(f"❌ Format de réponse inattendu")
                print(f"Réponse: {data}")
                return None
                
    except Exception as e:
        print(f"❌ Erreur CME: {e}")
        return None


# ============================================================================
# OPTION 2: Quandl/Nasdaq Data Link (Gratuit avec clé API)
# ============================================================================

def get_quandl_futures(metal='GC', api_key=None):
    """
    Quandl/Nasdaq Data Link - Données historiques futures
    Inscription gratuite: https://data.nasdaq.com/
    """
    
    if api_key is None:
        print("⚠️  Besoin d'une clé API Quandl (gratuite)")
        print("📝 Inscription: https://data.nasdaq.com/sign-up")
        return None
    
    metal_codes = {
        'GC': 'CHRIS/CME_GC',  # Or
        'SI': 'CHRIS/CME_SI',  # Argent
        'HG': 'CHRIS/CME_HG',  # Cuivre
        'PL': 'CHRIS/CME_PL'   # Platine
    }
    
    url = f"https://data.nasdaq.com/api/v3/datasets/{metal_codes[metal]}.json"
    params = {'api_key': api_key}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(
                data['dataset']['data'],
                columns=data['dataset']['column_names']
            )
            print(df.head(10))
            return df
        else:
            print(f"❌ Erreur: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur Quandl: {e}")
        return None


# ============================================================================
# OPTION 3: Alpha Vantage (Gratuit avec clé API)
# ============================================================================

def get_alphavantage_commodities(metal='GOLD', api_key=None):
    """
    Alpha Vantage - Données commodités
    Clé gratuite: https://www.alphavantage.co/support/#api-key
    """
    
    if api_key is None:
        print("⚠️  Besoin d'une clé API Alpha Vantage (gratuite)")
        print("📝 Inscription: https://www.alphavantage.co/support/#api-key")
        return None
    
    metal_map = {
        'GC': 'GOLD',
        'SI': 'SILVER',
        'HG': 'COPPER',
        'PL': 'PLATINUM'
    }
    
    commodity = metal_map.get(metal, 'GOLD')
    
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'COMMODITY',
        'symbol': commodity,
        'interval': 'daily',
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
        else:
            print(f"❌ Erreur: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur Alpha Vantage: {e}")
        return None


# ============================================================================
# OPTION 4: Si tu as Bloomberg Terminal
# ============================================================================

def get_bloomberg_futures(metal='GC'):
    """
    Bloomberg API (PAYANT - nécessite abonnement Bloomberg Terminal)
    """
    
    try:
        from xbbg import blp
        
        # Codes Bloomberg pour futures
        bloomberg_codes = {
            'GC': 'GC1 Comdty',  # Or front month
            'SI': 'SI1 Comdty',  # Argent
            'HG': 'HG1 Comdty',  # Cuivre
            'PL': 'PL1 Comdty'   # Platine
        }
        
        ticker = bloomberg_codes.get(metal)
        
        # Récupérer les données
        df = blp.bdp(ticker, ['PX_LAST', 'VOLUME', 'OPEN', 'HIGH', 'LOW'])
        print(df)
        
        # Pour plusieurs contrats
        contracts = [f'{metal}{i} Comdty' for i in range(1, 7)]  # 6 premiers contrats
        df_all = blp.bdp(contracts, ['PX_LAST', 'FUT_CONT_SIZE', 'VOLUME'])
        print(df_all)
        
        return df_all
        
    except ImportError:
        print("❌ Module xbbg non installé")
        print("💰 Bloomberg Terminal requis (~$24,000/an)")
        print("📦 Installation: pip install xbbg")
        return None
    except Exception as e:
        print(f"❌ Erreur Bloomberg: {e}")
        print("⚠️  Vérifiez que Bloomberg Terminal est ouvert et connecté")
        return None


# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*90)
    print("  OPTIONS POUR RÉCUPÉRER LES CONTRATS FUTURES")
    print("="*90)
    
    # OPTION 1: CME (GRATUIT - Recommandé)
    print("\n🔸 OPTION 1: CME Group (Gratuit - Source officielle)")
    cme_data = get_cme_futures_official('GC')
    print(cme_data)
    
    # OPTION 2: Quandl (GRATUIT avec inscription)
    print("\n\n🔸 OPTION 2: Quandl/Nasdaq Data Link")
    # quandl_data = get_quandl_futures('GC', api_key='VOTRE_CLE_ICI')
    print("⚠️  Nécessite une clé API gratuite: https://data.nasdaq.com/sign-up")
    
    # OPTION 3: Alpha Vantage (GRATUIT avec inscription)
    print("\n\n🔸 OPTION 3: Alpha Vantage")
    # av_data = get_alphavantage_commodities('GC', api_key='VOTRE_CLE_ICI')
    print("⚠️  Nécessite une clé API gratuite: https://www.alphavantage.co/support/#api-key")
    
    # OPTION 4: Bloomberg (PAYANT)
    print("\n\n🔸 OPTION 4: Bloomberg Terminal")
    print("💰 Abonnement requis: ~$24,000/an")
    print("🔧 Si vous avez Bloomberg, décommentez la ligne ci-dessous:")
    bloomberg_data = get_bloomberg_futures('GC')
    
    print("\n" + "="*90)
    print("  RECOMMANDATION: Utilisez CME Group (Option 1) - C'est gratuit et officiel!")
    print("="*90)