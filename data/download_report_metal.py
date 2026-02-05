#%%
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import zipfile
import os
import cot_reports as cot
import glob
#%%
############################
### LME
########################
# Positions by metals


def telecharger_rapport_lme(metal="aluminum"):
    # ... (Ta configuration "actifs" reste la même) ...
    actifs = {
        "aluminum": {"folder": "ah-aluminium", "code": "ah"},
        "lead":     {"folder": "pb-lead", "code": "pb"},
        "nickel":   {"folder": "ni-nickel", "code": "ni"},
        "tin":      {"folder": "sn-tin", "code": "sn"},
        "copper":   {"folder": "ca-copper", "code": "ca"},
        "zinc":     {"folder": "zs-zinc", "code": "zs"},
        "cobalt":   {"folder": "co-cobalt", "code": "co"},
        "steel":    {"folder": "sc-steel-scrap", "code": "sc"},
    }

    if metal.lower() not in actifs:
        print(f"❌ Métal '{metal}' non configuré.")
        return None

    info = actifs[metal.lower()]
    code = info['code']

    # --- CORRECTION 1 : LE CHEMIN ABSOLU ---
    # On récupère le dossier où se trouve CE script (dossier 'data')
    dossier_script = os.path.dirname(os.path.abspath(__file__))
    
    # On construit le pattern de recherche DANS ce dossier
    nom_pattern = f"mifid-weekly-cotr-report--{code}--*.xls"
    chemin_pattern = os.path.join(dossier_script, nom_pattern)
    
    # On cherche les fichiers
    fichiers_existants = glob.glob(chemin_pattern)
    
    date_locale_max = None
    fichier_local = None

    # Recherche du fichier local le plus récent
    if fichiers_existants:
        for fichier_path in fichiers_existants:
            try:
                # On extrait juste le nom du fichier pour la date
                nom_seul = os.path.basename(fichier_path)
                date_str = nom_seul.split('--')[-1].replace('.xls', '')
                date_fichier = datetime.strptime(date_str, "%d%m%Y")
                
                if date_locale_max is None or date_fichier > date_locale_max:
                    date_locale_max = date_fichier
                    fichier_local = fichier_path  # On garde le chemin complet !
            except:
                continue

    if fichier_local:
        # Juste pour l'affichage, on montre la date
        print(f"📁 Local : {os.path.basename(fichier_local)} ({date_locale_max.strftime('%d/%m/%Y')})")

    # --- TENTATIVE DE TÉLÉCHARGEMENT ---
    base_url = f"https://www.lme.com/-/media/files/data/cotrs/{info['folder']}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    date_test = datetime.now()

    # On essaie sur les 5 derniers jours pour être sûr (au lieu de 2)
    for i in range(5):
        # Si on a un fichier local et que la date testée est plus vieille ou égale, inutile de continuer
        if date_locale_max and date_test <= date_locale_max:
            print(f"✅ Fichier local à jour.")
            return fichier_local  # <--- On renvoie le fichier local existant

        date_str = date_test.strftime("%d%m%Y")
        nom_fichier_web = f"mifid-weekly-cotr-report--{code}--{date_str}.xls"
        full_url = f"{base_url}{nom_fichier_web}"
        
        # Le chemin où on va sauvegarder le nouveau fichier
        chemin_sauvegarde = os.path.join(dossier_script, nom_fichier_web)

        try:
            response = requests.get(full_url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"⬇️  Téléchargement : {nom_fichier_web}")
                
                # Suppression des anciens SEULEMENT si on a réussi à en télécharger un nouveau
                for ancien in fichiers_existants:
                    try:
                        os.remove(ancien)
                    except:
                        pass

                # Ecriture du nouveau fichier dans le bon dossier
                with open(chemin_sauvegarde, 'wb') as f:
                    f.write(response.content)
                
                return chemin_sauvegarde # <--- On renvoie le chemin du NOUVEAU fichier
        except:
            pass
        
        # On recule d'un jour
        date_test -= timedelta(days=1)

    # --- CORRECTION 2 : LE FALLBACK (FILET DE SÉCURITÉ) ---
    # Si on sort de la boucle sans avoir trouvé de nouveau fichier sur le web
    if fichier_local:
        print(f"ℹ️  Pas de nouveau fichier web, utilisation du local.")
        return fichier_local # <--- C'est ICI que ça sauvait ton programme
    
    print(f"❌ Aucun fichier trouvé (ni local, ni web).")
    return None


def tester_tous_les_metaux():
    """
    Test mis à jour avec les nouveaux métaux
    """
    print("=" * 80)
    print("🚀 DÉBUT DU TEST - TÉLÉCHARGEMENT DES RAPPORTS LME")
    print("=" * 80)
    print()
    
    # ✅ Liste mise à jour (sans lithium qui n'a pas de rapport)
    metaux = [
        "aluminum",
        "copper",      # ✅ Corrigé
        "zinc",        # ✅ Corrigé
        "lead",
        "nickel",
        "tin",
        "cobalt",      # ✅ Corrigé
        "steel_scrap", # ✅ Nouveau
        "steel_hrc_china",  # ✅ Nouveau
    ]
    
    resultats = {
        "succès": [],
        "échecs": []
    }
    
    for metal in metaux:
        print("\n" + "-" * 80)
        print(f"🔧 Traitement de : {metal.upper()}")
        print("-" * 80)
        
        try:
            fichier = telecharger_rapport_lme(metal)
            
            if fichier:
                resultats["succès"].append((metal, fichier))
                print(f"✅ {metal.upper()} : OK")
            else:
                resultats["échecs"].append(metal)
                print(f"❌ {metal.upper()} : ÉCHEC")
                
        except Exception as e:
            resultats["échecs"].append(metal)
            print(f"💥 {metal.upper()} : ERREUR - {e}")
        
        import time
        time.sleep(1)
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TÉLÉCHARGEMENTS")
    print("=" * 80)
    
    print(f"\n✅ SUCCÈS ({len(resultats['succès'])} métaux) :")
    for metal, fichier in resultats["succès"]:
        print(f"   • {metal.upper():20} → {fichier}")
    
    if resultats["échecs"]:
        print(f"\n❌ ÉCHECS ({len(resultats['échecs'])} métaux) :")
        for metal in resultats["échecs"]:
            print(f"   • {metal.upper()}")
    
    print(f"\n📈 TAUX DE RÉUSSITE : {len(resultats['succès'])}/{len(metaux)} " +
          f"({len(resultats['succès'])/len(metaux)*100:.1f}%)")
    print("=" * 80)
    
    return resultats

def traiter_rapport_cotr(nom_fichier):
    # 1. On lit le fichier (skiprows=7 ou 8 selon le fichier, on va tester 7 ici)
    df = pd.read_excel(nom_fichier, skiprows=7, engine='xlrd')

    # 2. On définit les colonnes en fonction de ce qu'on voit dans ton fichier
    # On force 13 noms car il y a souvent une colonne vide au début + les 12 de données
    noms_colonnes = [
        'ID_Col', 'Notation', 'Unite', 
        'Bank_Long', 'Bank_Short', 
        'Funds_Long', 'Funds_Short', 
        'Other_Fin_Long', 'Other_Fin_Short', 
        'Commercial_Long', 'Commercial_Short', 
        'Compliance_Long', 'Compliance_Short'
    ]

    # Sécurité : On ajuste si le nombre de colonnes diffère
    if len(df.columns) == len(noms_colonnes):
        df.columns = noms_colonnes
    else:
        # Si décalage, on nomme par index pour ne pas planter
        df.columns = [f"Col_{i}" for i in range(len(df.columns))]
        # On essaie de retrouver nos petits manuellement
        df = df.rename(columns={df.columns[5]: 'Funds_Long', df.columns[6]: 'Funds_Short'})

    # 3. On cherche la ligne "Total" (elle est dans la colonne 'Unite' ou la 3ème colonne)
    # Dans ton fichier, "Total" est sous la colonne du milieu
    df_clean = df[df.iloc[:, 2].astype(str).str.contains('Total', na=False)].copy()

    df_clean.drop(["ID_Col","Notation","Unite"],axis=1,inplace=True)
    df_clean.drop(df.index[-1],axis=0,inplace=True)
    df_clean.reset_index(inplace=True)
    df_clean.drop(["index"],axis=1,inplace=True)
    df_clean.index = ["Number of positions", "Change since the previous repport", "Percentage of the total open interest (%)"]
    return df_clean


#################"""
# CME
#%%

def get_full_cme_data_direct(commodity_name):
    """
    Version FINALE CORRIGÉE avec tous les noms exacts du fichier CME
    """
    # ✅ MAPPING DÉFINITIF avec les noms EXACTS du fichier CME
    mapping = {
        "gold": "GOLD - COMMODITY EXCHANGE INC.",
        "silver": "SILVER - COMMODITY EXCHANGE INC.",
        "copper": "COPPER- #1 - COMMODITY EXCHANGE INC.",  # ✅ Corrigé (espace après le tiret)
        "platinum": "PLATINUM - NEW YORK MERCANTILE EXCHANGE",
        "palladium": "PALLADIUM - NEW YORK MERCANTILE EXCHANGE",
        "steel": "STEEL-HRC - COMMODITY EXCHANGE INC.",
        
        # Bonus : Steel européen
        "steel_euro": "NORTH EURO HOT-ROLL COIL STEEL - COMMODITY EXCHANGE INC."
    }
    
    name_lower = commodity_name.lower()
    if name_lower not in mapping:
        print(f"❌ Commodité '{commodity_name}' non configurée.")
        print(f"💡 Commodités disponibles : {', '.join(mapping.keys())}")
        return None

    url = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_2025.zip"
    
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            fname = z.namelist()[0]
            with z.open(fname) as f:
                df_all = pd.read_csv(f, low_memory=False)
        
        # Nettoyage des colonnes
        df_all.columns = df_all.columns.str.strip()
        
        # Filtrage avec le nom EXACT
        search_term = mapping[name_lower]
        full_df = df_all[df_all['Market_and_Exchange_Names'] == search_term].copy()
        
        if full_df.empty:
            print(f"⚠️ Aucun résultat pour {search_term}")
            return None

        # Gestion de la date
        date_col = [c for c in full_df.columns if 'Date' in c]
        if date_col:
            full_df.rename(columns={date_col[0]: 'Date_Rapport'}, inplace=True)
            full_df['Date_Rapport'] = pd.to_datetime(full_df['Date_Rapport'], errors='coerce')
        
        return full_df

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        return None

colonnes_importantes_cme = [
        'Date_Rapport',  # ou 'Report_Date_as_YYYY-MM-DD'
        'Market_and_Exchange_Names',
        'Open_Interest_All',
        
        # Positions des différents types de traders
        'Prod_Merc_Positions_Long_All',
        'Prod_Merc_Positions_Short_All',
        'Swap_Positions_Long_All',
        'Swap_Positions_Short_All',
        'M_Money_Positions_Long_All',
        'M_Money_Positions_Short_All',
        'Other_Rept_Positions_Long_All',
        'Other_Rept_Positions_Short_All',
        'NonRept_Positions_Long_All',
        'NonRept_Positions_Short_All',
        
        # Net positions
        'Prod_Merc_Positions_Spread_All',
        'M_Money_Positions_Spread_All',
    ]

# %%
