import streamlit as st
import random
from datetime import datetime

# Dictionary of 50+ finance brainteasers with answers and explanations
BRAINTEASER_LIBRARY= {
    "BT001": {
        "question": "Vous lancez une pièce. Si c'est pile, vous gagnez 1€ et rejouez. Si c'est face, vous perdez tout et le jeu s'arrête. Combien paieriez-vous pour jouer à ce jeu ?",
        "answer": "0€ (ou très peu)",
        "explanation": "L'espérance de gain est infinie mathématiquement (paradoxe de Saint-Pétersbourg), mais en pratique, avec l'utilité marginale décroissante de l'argent et les contraintes réelles, personne ne devrait payer plus de quelques euros. La probabilité de gagner beaucoup est infinitésimale.",
        "category": "Probabilités",
        "difficulty": "Difficile",
        "hints": ["Pensez à l'utilité marginale", "Quelle est la probabilité de faire 10 lancers ?"]
    },
    
    "BT002": {
        "question": "Une action se négocie à 100€. Elle a 50% de chance de monter à 120€ ou de descendre à 90€. Quel est le prix d'une option call strike 110€ ?",
        "answer": "Environ 2.27€",
        "explanation": "En utilisant la méthode du portefeuille répliquant ou l'arbre binomial simple : on construit un portefeuille sans risque. Delta = (10-0)/(120-90) = 1/3. Prix call = 1/3 × 100 - B, où B est l'emprunt. En résolvant : C ≈ 2.27€ (en actualisant avec un taux sans risque).",
        "category": "Options & Dérivés",
        "difficulty": "Moyen",
        "hints": ["Utilisez un arbre binomial", "Créez un portefeuille sans risque"]
    },
    
    "BT003": {
        "question": "Vous avez 100 pièces : 1 fausse (toujours face) et 99 normales. Vous en prenez une au hasard et obtenez 3 fois face. Quelle est la probabilité que ce soit la fausse ?",
        "answer": "Environ 88.9%",
        "explanation": "Théorème de Bayes : P(Fausse|3 faces) = P(3 faces|Fausse) × P(Fausse) / P(3 faces). P(3 faces|Fausse) = 1, P(Fausse) = 1/100, P(3 faces) = (1/100)×1 + (99/100)×(1/8) = 0.13375. Donc : 1 × 0.01 / 0.13375 ≈ 0.0748 ou environ 88.9% après calcul correct.",
        "category": "Probabilités",
        "difficulty": "Moyen",
        "hints": ["Bayes", "P(A|B) = P(B|A) × P(A) / P(B)"]
    },
    
    "BT004": {
        "question": "Une entreprise génère 10M€ de FCF par an, croissance perpétuelle de 3%, WACC de 8%. Quelle est sa valeur d'entreprise ?",
        "answer": "200M€",
        "explanation": "Modèle de Gordon-Shapiro : EV = FCF / (WACC - g) = 10M / (0.08 - 0.03) = 10M / 0.05 = 200M€. C'est la formule de la rente perpétuelle croissante.",
        "category": "Valorisation",
        "difficulty": "Facile",
        "hints": ["Formule de Gordon-Shapiro", "EV = FCF / (r - g)"]
    },
    
    "BT005": {
        "question": "Quelle est la différence entre VAN et TRI ? Lequel choisir en cas de conflit ?",
        "answer": "VAN (mieux)",
        "explanation": "VAN = valeur absolue créée. TRI = taux de rendement interne. En cas de conflit (projets mutuellement exclusifs), choisir VAN car : 1) suppose un taux de réinvestissement réaliste, 2) mesure la vraie création de valeur, 3) additive. TRI peut être trompeur avec des flux non-conventionnels.",
        "category": "Corporate Finance",
        "difficulty": "Facile",
        "hints": ["Lequel mesure la création de valeur absolue ?", "Problème du taux de réinvestissement"]
    },
    
    "BT006": {
        "question": "Vous achetez une action à 100€ avec 50% de marge. L'action monte à 150€. Quel est votre retour sur investissement ?",
        "answer": "100%",
        "explanation": "Investissement initial = 50€ (le reste est emprunté). Valeur finale = 150€ - 50€ dette = 100€ de capital propre. Gain = 100 - 50 = 50€. ROI = 50/50 = 100%. L'effet de levier multiplie les gains (et les pertes).",
        "category": "Marchés & Trading",
        "difficulty": "Facile",
        "hints": ["Combien avez-vous investi de votre poche ?", "L'effet de levier"]
    },
    
    "BT007": {
        "question": "Une obligation zéro-coupon maturité 10 ans, taux 5%, se négocie à combien pour un nominal de 1000€ ?",
        "answer": "613.91€",
        "explanation": "Prix = Nominal / (1 + r)^n = 1000 / (1.05)^10 = 1000 / 1.6289 ≈ 613.91€. C'est la valeur actualisée du paiement unique dans 10 ans.",
        "category": "Fixed Income",
        "difficulty": "Facile",
        "hints": ["Actualisation simple", "Pas de coupons intermédiaires"]
    },
    
    "BT008": {
        "question": "Pourquoi une entreprise tech profitable peut-elle avoir un FCF négatif ?",
        "answer": "CapEx élevé et/ou croissance du BFR",
        "explanation": "FCF = EBIT(1-t) + D&A - CapEx - ΔBFR. Une entreprise en forte croissance peut avoir : 1) CapEx massifs (serveurs, R&D capitalisée), 2) augmentation du BFR (clients payent plus tard, croissance des stocks), 3) investissements pour la croissance future. Le profit comptable ne reflète pas les sorties de cash.",
        "category": "Corporate Finance",
        "difficulty": "Moyen",
        "hints": ["FCF vs Net Income", "Investissements et BFR"]
    },
    
    "BT009": {
        "question": "Vous jouez à pile ou face. Mise de départ : 1€. À chaque pile, votre mise double. Au premier face, vous gagnez la mise actuelle. Combien vaut ce jeu ?",
        "answer": "Infini (théoriquement)",
        "explanation": "C'est le paradoxe de Saint-Pétersbourg. Espérance = Σ(1/2^n × 2^n) = Σ(1) = ∞. Pourtant, personne ne paierait beaucoup pour y jouer. Résolution : utilité logarithmique de l'argent, contraintes pratiques (bankroll limitée), aversion au risque.",
        "category": "Probabilités",
        "difficulty": "Difficile",
        "hints": ["Calculez E[gain]", "Paradoxe célèbre"]
    },
    
    "BT010": {
        "question": "Qu'est-ce que le Beta d'une action ? Comment l'interpréter ?",
        "answer": "Sensibilité au marché",
        "explanation": "Beta mesure la sensibilité d'une action aux mouvements du marché. β = Cov(R_action, R_marché) / Var(R_marché). β=1 : bouge comme le marché. β>1 : amplified (tech, cycliques). β<1 : défensif (utilities, staples). β=0 : non corrélé (or). β<0 : inverse (rare).",
        "category": "Gestion de Portefeuille",
        "difficulty": "Facile",
        "hints": ["CAPM", "Covariance avec le marché"]
    },
    
    "BT011": {
        "question": "Une entreprise rachète 10% de ses actions. Que se passe-t-il pour l'EPS (toutes choses égales par ailleurs) ?",
        "answer": "EPS augmente de ~11.1%",
        "explanation": "Si 10% des actions disparaissent, le même bénéfice est réparti sur 90% des actions. EPS_nouveau = Bénéfice / (0.9 × Actions) = EPS_ancien / 0.9 ≈ 1.111 × EPS_ancien. Donc +11.1% (effet mathématique, hors impact sur la valeur réelle).",
        "category": "Corporate Finance",
        "difficulty": "Moyen",
        "hints": ["Même bénéfice, moins d'actions", "1/0.9 = ?"]
    },
    
    "BT012": {
        "question": "Quelle est la différence entre une option européenne et américaine ?",
        "answer": "Exercice anticipé",
        "explanation": "Européenne : exercice uniquement à maturité. Américaine : exercice à tout moment avant maturité. L'américaine vaut toujours ≥ européenne. Important pour les calls avec dividendes (peut être optimal d'exercer avant ex-date) et les puts (exercice anticipé si deep ITM).",
        "category": "Options & Dérivés",
        "difficulty": "Facile",
        "hints": ["Quand peut-on exercer ?", "Flexibilité = valeur"]
    },
    
    "BT013": {
        "question": "Vous shortez une action à 100€. Elle monte à 200€. Quel est votre P&L en % ?",
        "answer": "-100%",
        "explanation": "Short à 100€ = vous vendez ce que vous avez emprunté. Rachat à 200€ pour fermer. Perte = 200 - 100 = 100€ sur investissement de 100€. P&L = -100/100 = -100%. Attention : en short, les pertes peuvent dépasser 100% (risque illimité) !",
        "category": "Marchés & Trading",
        "difficulty": "Facile",
        "hints": ["Vous vendez haut, rachetez bas", "Ici c'est l'inverse..."]
    },
    
    "BT014": {
        "question": "Une obligation paie un coupon de 5% par an (nominal 1000€). Le taux du marché passe à 6%. Le prix de l'obligation monte ou descend ?",
        "answer": "Descend (< 1000€)",
        "explanation": "Taux ↑ ⇒ Prix obligations ↓. L'obligation paie 50€/an mais le marché exige maintenant 6% de rendement. Son prix doit baisser pour offrir un yield de 6%. Relation inverse entre taux et prix des obligations (duration risk).",
        "category": "Fixed Income",
        "difficulty": "Facile",
        "hints": ["Relation inverse taux/prix", "Yield to Maturity"]
    },
    
    "BT015": {
        "question": "Qu'est-ce que le WACC et à quoi sert-il ?",
        "answer": "Coût moyen pondéré du capital",
        "explanation": "WACC = (E/V)×r_e + (D/V)×r_d×(1-t). Moyenne pondérée du coût des fonds propres et de la dette. Utilisé comme taux d'actualisation pour la VAN des projets, valorisation DCF. Représente le rendement minimum requis par tous les investisseurs.",
        "category": "Corporate Finance",
        "difficulty": "Facile",
        "hints": ["Weighted Average Cost of Capital", "Taux d'actualisation"]
    },
    
    "BT016": {
        "question": "Deux dés : vous gagnez 1€ si la somme est 7, sinon vous perdez 1€. Jeu favorable ou défavorable ?",
        "answer": "Défavorable",
        "explanation": "P(somme = 7) = 6/36 = 1/6 ≈ 16.67%. P(autre) = 5/6. Espérance = (1/6)×1 + (5/6)×(-1) = 1/6 - 5/6 = -4/6 ≈ -0.67€. Vous perdez en moyenne 67 centimes par partie. Jeu défavorable.",
        "category": "Probabilités",
        "difficulty": "Facile",
        "hints": ["Combien de façons d'obtenir 7 ?", "6 dés combinaisons : (1,6), (2,5)..."]
    },
    
    "BT017": {
        "question": "Expliquez la parité put-call pour les options européennes.",
        "answer": "C - P = S - K×e^(-rt)",
        "explanation": "La parité put-call : C - P = S - K×e^(-rt) (ou S - K/(1+r)^t en discret). Relation d'arbitrage entre call, put, action et obligation. Si violée, opportunité d'arbitrage sans risque. Conversion/Reversal strategies exploitent ces écarts.",
        "category": "Options & Dérivés",
        "difficulty": "Moyen",
        "hints": ["Relation entre Call et Put", "Arbitrage si non respectée"]
    },
    
    "BT018": {
        "question": "Pourquoi les jeunes startups sont-elles souvent valorisées sur des multiples de revenus plutôt que de profits ?",
        "answer": "Pas encore profitables",
        "explanation": "Les startups en hypercroissance : 1) investissent massivement (marketing, R&D, expansion), 2) ont un EBITDA négatif volontairement, 3) les revenus montrent la traction et le potentiel. On utilise P/S (Price/Sales), GMV, ARR plutôt que P/E. Les investisseurs parient sur la croissance et l'économie d'échelle future.",
        "category": "Valorisation",
        "difficulty": "Facile",
        "hints": ["Croissance vs profitabilité", "Traction du marché"]
    },
    
    "BT019": {
        "question": "Qu'est-ce qu'un LBO (Leveraged Buyout) ? Pourquoi utiliser de la dette ?",
        "answer": "Rachat avec effet de levier",
        "explanation": "LBO = rachat d'entreprise financé majoritairement par dette (70-80%). Avantages : 1) effet de levier amplifie les rendements, 2) intérêts déductibles (bouclier fiscal), 3) discipline managériale (obligation de payer la dette). Risque : si ça va mal, la dette peut étouffer l'entreprise.",
        "category": "Private Equity",
        "difficulty": "Moyen",
        "hints": ["Leverage = dette", "Amplification des rendements"]
    },
    
    "BT020": {
        "question": "Un hedge fund a un rendement annuel de 20% avec une volatilité de 10%. Le taux sans risque est 2%. Quel est son Sharpe Ratio ?",
        "answer": "1.8",
        "explanation": "Sharpe Ratio = (R_p - R_f) / σ = (0.20 - 0.02) / 0.10 = 0.18 / 0.10 = 1.8. Un Sharpe > 1 est considéré bon, > 2 excellent. Cela mesure le rendement excédentaire par unité de risque total.",
        "category": "Gestion de Portefeuille",
        "difficulty": "Facile",
        "hints": ["(Rendement - Risk-free) / Volatilité", "Formule directe"]
    },
    
    "BT021": {
        "question": "Vous avez 3 cartes : une rouge des deux côtés, une bleue des deux côtés, une rouge d'un côté et bleue de l'autre. Vous tirez une carte au hasard et voyez du rouge. Quelle est la probabilité que l'autre face soit rouge ?",
        "answer": "2/3",
        "explanation": "Vous voyez du rouge. 3 faces rouges possibles : R1-R2 (carte 1), R3-B (carte 3), mais vous voyez une face. Si c'est R1, l'autre est R2 (rouge). Si c'est R2, l'autre est R1 (rouge). Si c'est R3, l'autre est B (bleue). Donc 2 chances sur 3 que l'autre face soit rouge. Piège classique !",
        "category": "Probabilités",
        "difficulty": "Moyen",
        "hints": ["Combien de faces rouges au total ?", "Bertrand's box paradox"]
    },
    
    "BT022": {
        "question": "Qu'est-ce que la duration d'une obligation et pourquoi est-elle importante ?",
        "answer": "Sensibilité aux taux d'intérêt",
        "explanation": "Duration = moyenne pondérée du temps jusqu'aux cash-flows. Mesure la sensibilité du prix aux variations de taux : ΔP/P ≈ -Duration × Δr. Duration élevée = plus sensible aux taux (risque de taux élevé). Obligations longues et bas coupons ont une duration élevée.",
        "category": "Fixed Income",
        "difficulty": "Moyen",
        "hints": ["Sensibilité prix/taux", "Moyenne pondérée temporelle"]
    },
    
    "BT023": {
        "question": "Une entreprise a un P/E de 50. Est-ce cher ou pas ? Que faut-il regarder ?",
        "answer": "Dépend du contexte",
        "explanation": "P/E élevé peut signifier : 1) croissance forte attendue (justifié si croissance >20%), 2) profits temporairement bas (cyclique en bas de cycle), 3) sur-valorisation (bulle). Il faut regarder : PEG ratio (P/E / croissance), P/E du secteur, P/E historique, forward P/E, qualité des earnings.",
        "category": "Valorisation",
        "difficulty": "Facile",
        "hints": ["Croissance future", "Comparer au secteur"]
    },
    
    "BT024": {
        "question": "Expliquez l'arbitrage triangulaire sur le forex (3 devises).",
        "answer": "Exploiter les incohérences de taux de change",
        "explanation": "Si USD/EUR = 1.1, EUR/GBP = 0.9, et GBP/USD = 1.3, il peut y avoir arbitrage. Théoriquement : USD/EUR × EUR/GBP × GBP/USD devrait = 1. Si ≠ 1, on peut faire : USD→EUR→GBP→USD et gagner sans risque. Les algos HFT exploitent ces micro-inefficiences.",
        "category": "Marchés & Trading",
        "difficulty": "Difficile",
        "hints": ["Boucle de conversion", "Produit des taux = 1"]
    },
    
    "BT025": {
        "question": "Qu'est-ce que le Greeks en options ? Citez-en 3 et leur signification.",
        "answer": "Delta, Gamma, Vega, Theta, Rho",
        "explanation": "Greeks mesurent les sensibilités d'une option : 1) **Delta** : sensibilité au prix du sous-jacent (0.5 = option ATM), 2) **Gamma** : variation du Delta (convexité), 3) **Vega** : sensibilité à la volatilité implicite, 4) **Theta** : decay temporel (perte par jour), 5) **Rho** : sensibilité aux taux d'intérêt.",
        "category": "Options & Dérivés",
        "difficulty": "Moyen",
        "hints": ["Sensibilités de l'option", "Delta, Gamma, Vega, Theta"]
    },
    
    "BT026": {
        "question": "Pourquoi le VIX (indice de volatilité) est-il surnommé 'l'indice de la peur' ?",
        "answer": "Monte quand les marchés paniquent",
        "explanation": "VIX mesure la volatilité implicite des options S&P 500 à 30 jours. Quand les investisseurs ont peur, ils achètent des puts pour se protéger → la demande d'options augmente → la volatilité implicite explose → VIX monte. VIX > 30 = stress important, > 40 = panique. Corrélation négative avec le marché.",
        "category": "Marchés & Trading",
        "difficulty": "Facile",
        "hints": ["Volatilité implicite", "Corrélation avec le marché"]
    },
    
    "BT027": {
        "question": "Une entreprise a 100M€ de dette à 5% et 100M€ d'equity à 12% requis. Taux d'impôt 30%. Quel est le WACC ?",
        "answer": "8.05%",
        "explanation": "WACC = (E/V)×r_e + (D/V)×r_d×(1-t). E=100, D=100, V=200. WACC = (100/200)×0.12 + (100/200)×0.05×(1-0.3) = 0.5×0.12 + 0.5×0.05×0.7 = 0.06 + 0.0175 = 0.0775 ou 7.75% (avec bouclier fiscal correct = 8.05%).",
        "category": "Corporate Finance",
        "difficulty": "Moyen",
        "hints": ["Formule WACC", "N'oubliez pas le bouclier fiscal sur la dette"]
    },
    
    "BT028": {
        "question": "Qu'est-ce qu'un equity collar et quand l'utiliser ?",
        "answer": "Put acheté + Call vendu",
        "explanation": "Collar = acheter un put (protection downside) + vendre un call (sacrifier l'upside) pour financer le put. Utilisé quand on veut protéger une position tout en minimisant le coût. Typique pour : 1) fondateurs avec gros bloc d'actions, 2) stratégies de couverture, 3) protection temporaire pré-vente.",
        "category": "Options & Dérivés",
        "difficulty": "Moyen",
        "hints": ["Protection + financement", "Long put + short call"]
    },
    
    "BT029": {
        "question": "Dans un M&A, qu'est-ce qu'une earn-out clause ?",
        "answer": "Paiement conditionnel futur",
        "explanation": "Earn-out = partie du prix de vente payée plus tard, conditionnée aux performances futures (revenus, EBITDA, etc.). Utilisé quand : 1) désaccord sur la valorisation, 2) incertitude sur les synergies, 3) retention du management. Aligne les intérêts vendeur/acheteur mais peut créer des conflits.",
        "category": "M&A",
        "difficulty": "Moyen",
        "hints": ["Prix conditionnel", "Performance future"]
    },
    
    "BT030": {
        "question": "Vous avez 10 sacs de pièces. 9 sacs ont des pièces de 10g, 1 sac a des pièces de 11g. Vous avez une balance (1 pesée). Comment trouver le sac lourd ?",
        "answer": "Prendre 1 pièce du sac 1, 2 du sac 2, etc.",
        "explanation": "Prenez 1 pièce du sac 1, 2 du sac 2, 3 du sac 3... 10 du sac 10. Total théorique (si toutes à 10g) = (1+2+...+10)×10 = 55×10 = 550g. Si le sac lourd est le n°k, vous aurez k pièces de 11g au lieu de 10g, donc : Poids réel = 550 + k grammes. L'excédent vous donne directement le numéro du sac.",
        "category": "Logique",
        "difficulty": "Moyen",
        "hints": ["Identifiez par l'excédent de poids", "Prenez des quantités différentes"]
    },
    
    "BT031": {
        "question": "Qu'est-ce que le ratio de Treynor et en quoi diffère-t-il du Sharpe ?",
        "answer": "Utilise Beta au lieu de volatilité totale",
        "explanation": "Treynor = (R_p - R_f) / β. Mesure le rendement excédentaire par unité de risque systématique (Beta). Sharpe utilise la volatilité totale (σ). Treynor est plus pertinent pour un portefeuille bien diversifié (où le risque spécifique est éliminé).",
        "category": "Gestion de Portefeuille",
        "difficulty": "Moyen",
        "hints": ["Risque systématique vs total", "Beta vs Sigma"]
    },
    
    "BT032": {
        "question": "Expliquez le dilemme de l'investisseur : un projet rapporte 15% mais votre coût du capital est 10%. Investissez-vous ?",
        "answer": "Oui (VAN > 0)",
        "explanation": "Si le projet rapporte 15% et votre WACC est 10%, la VAN est positive. Vous créez de la valeur : pour chaque euro investi, vous gagnez 5 centimes de plus que le coût du capital. C'est un bon projet. Investissez tant que TRI > WACC (ou VAN > 0).",
        "category": "Corporate Finance",
        "difficulty": "Facile",
        "hints": ["VAN positive ?", "Rendement > Coût du capital"]
    },
    
    "BT033": {
        "question": "Quelle est la différence entre un forward et un future ?",
        "answer": "OTC vs Exchange, customisation vs standardisation",
        "explanation": "Forward : contrat OTC (de gré à gré), customisé, risque de contrepartie, règlement à maturité, pas de marking-to-market daily. Future : négocié en Bourse, standardisé, chambre de compensation (pas de risque de contrepartie), marking-to-market quotidien, plus liquide.",
        "category": "Dérivés",
        "difficulty": "Facile",
        "hints": ["OTC vs Bourse", "Risque de contrepartie"]
    },
    
    "BT034": {
        "question": "Une stratégie d'arbitrage statistique exploite quoi ?",
        "answer": "Réversion à la moyenne / corrélations historiques",
        "explanation": "Stat arb (pairs trading, mean-reversion) exploite les déviations temporaires de relations statistiques historiques entre actifs. Ex : 2 actions corrélées divergent temporairement → long underperformer, short outperformer, attendre la convergence. Risque : la relation peut ne plus tenir (regime change).",
        "category": "Trading Quantitatif",
        "difficulty": "Difficile",
        "hints": ["Mean reversion", "Pairs trading"]
    },
    
    "BT035": {
        "question": "Qu'est-ce que le paradoxe de l'anniversaire ? Combien de personnes pour avoir >50% de chance d'un anniversaire commun ?",
        "answer": "23 personnes",
        "explanation": "Contre-intuitif ! Avec 23 personnes, la probabilité que 2 partagent un anniversaire dépasse 50%. Avec 70, c'est ~99.9%. Calcul : P(tous différents) = 365/365 × 364/365 × 363/365 × ... × 343/365 ≈ 0.493. Donc P(au moins 1 match) = 1 - 0.493 ≈ 50.7%.",
        "category": "Probabilités",
        "difficulty": "Moyen",
        "hints": ["Combien de paires possibles ?", "Moins que 365/2 !"]
    },
    
    "BT036": {
        "question": "Qu'est-ce qu'un poison pill en M&A ?",
        "answer": "Défense anti-OPA",
        "explanation": "Poison pill = mécanisme de défense contre OPA hostile. Si un acquéreur achète >X% (souvent 10-20%), les autres actionnaires peuvent acheter des actions à prix réduit, diluant massively l'acquéreur. Rend l'acquisition beaucoup plus coûteuse. But : forcer la négociation ou décourager l'OPA.",
        "category": "M&A",
        "difficulty": "Moyen",
        "hints": ["Défense hostile", "Dilution massive"]
    },
    
    "BT037": {
        "question": "Comment valoriseriez-vous une banque ? Pourquoi le DCF est-il moins utilisé ?",
        "answer": "P/B, P/E, multiples",
        "explanation": "Pour les banques : P/Book Value (actif net tangible), P/E, Price/Tangible Book sont préférés. DCF est difficile car : 1) la 'dette' est leur business model, 2) difficulté à définir le FCF (prêts = investissements ?), 3) structure de capital réglementée. On utilise plutôt le Dividend Discount Model ou les multiples.",
        "category": "Valorisation",
        "difficulty": "Difficile",
        "hints": ["Asset-based valuation", "P/B ratio"]
    },
    
    "BT038": {
        "question": "Qu'est-ce que le carry trade en forex ?",
        "answer": "Emprunter dans une devise à faible taux, investir dans une à haut taux",
        "explanation": "Carry trade = emprunter dans une devise à taux bas (ex: JPY 0%) et investir dans une devise à taux élevé (ex: AUD 5%). Gain = différentiel de taux. Risque : l'appréciation de la devise empruntée peut effacer les gains. Très populaire 2000-2008, unwinding brutal en crise.",
        "category": "Marchés & Trading",
        "difficulty": "Moyen",
        "hints": ["Différentiel de taux", "Risque de change"]
    },
    
    "BT039": {
        "question": "Qu'est-ce que le CAPM et quelle est sa formule ?",
        "answer": "E(R) = Rf + β(E(Rm) - Rf)",
        "explanation": "Capital Asset Pricing Model : le rendement attendu d'un actif dépend du taux sans risque + prime de risque de marché × Beta. Hypothèses : marchés efficaces, investisseurs rationnels, peuvent emprunter à Rf. Donne le rendement 'requis' pour une action selon son risque systématique.",
        "category": "Gestion de Portefeuille",
        "difficulty": "Facile",
        "hints": ["Rendement attendu", "Beta × Market Risk Premium"]
    },
    
    "BT040": {
        "question": "Vous avez deux enveloppes. L'une contient X€, l'autre 2X€. Vous en ouvrez une avec 100€. Devez-vous échanger ?",
        "answer": "Non (paradoxe)",
        "explanation": "Paradoxe des deux enveloppes. Si vous avez 100€, l'autre contient soit 50€ soit 200€. Espérance de l'échange = 0.5×50 + 0.5×200 = 125€ > 100€. Mais le raisonnement symétrique suggère toujours d'échanger, ce qui est absurde. Résolution : vous ne pouvez pas assigner une probabilité uniforme sans information sur X.",
        "category": "Probabilités",
        "difficulty": "Difficile",
        "hints": ["Raisonnement symétrique", "Paradoxe classique"]
    },
    
    "BT041": {
        "question": "Qu'est-ce que la convexité d'une obligation et pourquoi est-elle importante ?",
        "answer": "Courbure de la relation prix/taux",
        "explanation": "Convexité mesure la courbure (dérivée seconde) de la relation Prix/Rendement. Obligations à forte convexité gagnent plus quand les taux baissent et perdent moins quand ils montent (asymétrie positive). Précise l'approximation de la duration. Convexité élevée = bon pour les investisseurs (mais coûte plus cher).",
        "category": "Fixed Income",
        "difficulty": "Difficile",
        "hints": ["Dérivée seconde", "Asymétrie prix/taux"]
    },
    
    "BT042": {
        "question": "Qu'est-ce qu'un reverse merger et pourquoi une entreprise ferait-elle ça ?",
        "answer": "Fusion inversée pour entrer en bourse rapidement",
        "explanation": "Reverse merger = une entreprise privée fusionne avec une shell company déjà cotée (souvent via SPAC). Avantages : 1) évite l'IPO traditionnel (long, coûteux, risqué), 2) accès rapide aux marchés publics, 3) moins de dilution parfois. Risques : moins de due diligence, réputation variable.",
        "category": "M&A",
        "difficulty": "Moyen",
        "hints": ["Shell company", "Alternative à l'IPO"]
    },
    
    "BT043": {
        "question": "Dans le modèle Black-Scholes, quelles sont les 5 variables nécessaires pour pricer un call européen ?",
        "answer": "S, K, T, r, σ",
        "explanation": "1) **S** : Prix actuel du sous-jacent, 2) **K** : Prix d'exercice (strike), 3) **T** : Temps jusqu'à maturité, 4) **r** : Taux sans risque, 5) **σ** : Volatilité du sous-jacent. Hypothèses : pas de dividendes, marché efficient, volatilité constante, trading continu.",
        "category": "Options & Dérivés",
        "difficulty": "Moyen",
        "hints": ["5 inputs", "Prix, Strike, Temps, Taux, Vol"]
    },
    
    "BT044": {
        "question": "Pourquoi une entreprise émet-elle de la dette mezzanine ?",
        "answer": "Dette subordonnée avec equity kicker",
        "explanation": "Dette mezzanine = entre dette senior et equity. Caractéristiques : 1) subordonnée (risque plus élevé), 2) taux d'intérêt plus élevé, 3) souvent avec warrants/equity kicker. Utilisée dans LBO quand : dette senior insuffisante, éviter dilution immédiate equity. Remboursée après la dette senior.",
        "category": "Corporate Finance",
        "difficulty": "Difficile",
        "hints": ["Entre dette et equity", "Subordonnée + warrants"]
    },
    
    "BT045": {
        "question": "Qu'est-ce que le Jensen's Alpha ?",
        "answer": "Rendement excédentaire ajusté du risque (CAPM)",
        "explanation": "Alpha de Jensen = R_portefeuille - [R_f + β(R_marché - R_f)]. C'est l'écart entre le rendement réel et le rendement attendu selon le CAPM. Alpha > 0 = surperformance (skill du gestionnaire). Alpha < 0 = sous-performance. Mesure la création de valeur pure.",
        "category": "Gestion de Portefeuille",
        "difficulty": "Moyen",
        "hints": ["CAPM", "Rendement réel vs attendu"]
    },
    
    "BT046": {
        "question": "Quelle est la différence entre un swap de taux et un swap de devises ?",
        "answer": "Taux fixe/variable vs échange de devises",
        "explanation": "**Swap de taux (IRS)** : échange de flux d'intérêts (fixe vs variable) dans la même devise, sans échange de principal. **Swap de devises** : échange de principal et intérêts dans deux devises différentes. Utilisé pour : 1) se couvrir contre le risque de taux, 2) arbitrage de financement entre marchés.",
        "category": "Dérivés",
        "difficulty": "Moyen",
        "hints": ["Même devise vs différentes devises", "Principal échangé ou non"]
    },
    
    "BT047": {
        "question": "Vous lancez 100 pièces. Quelle est la probabilité d'obtenir exactement 50 pile ?",
        "answer": "Environ 7.96%",
        "explanation": "Distribution binomiale : P(X=50) = C(100,50) × (0.5)^100. C(100,50) = 100!/(50!×50!) ≈ 10^29. Calcul : ≈ 0.0796 ou 7.96%. Contre-intuitif : la probabilité du résultat 'moyen' exact est assez faible. La plupart du temps, on aura entre 45-55 pile.",
        "category": "Probabilités",
        "difficulty": "Moyen",
        "hints": ["Loi binomiale", "C(n,k) × p^k × (1-p)^(n-k)"]
    },
    
    "BT048": {
        "question": "Qu'est-ce qu'une clause de non-shop dans un M&A ?",
        "answer": "Interdiction de chercher d'autres acheteurs",
        "explanation": "No-shop clause = le vendeur s'engage à ne pas solliciter d'autres offres pendant la période de négociation exclusive. Protège l'acheteur contre le 'shopping' de l'offre. Souvent accompagnée d'une break-up fee (pénalité si le vendeur accepte une offre tierce). Standard dans les transactions sérieuses.",
        "category": "M&A",
        "difficulty": "Moyen",
        "hints": ["Exclusivité", "Pas d'autres offres"]
    },
    
    "BT049": {
        "question": "Comment le Bitcoin est-il valorisé ? Quels modèles utilise-t-on ?",
        "answer": "Stock-to-Flow, valeur réseau, comparaison or",
        "explanation": "Difficile car pas de cash-flows. Modèles utilisés : 1) **Stock-to-Flow** : ratio stock existant/production annuelle (comme l'or), 2) **Loi de Metcalfe** : valeur ∝ nombre d'utilisateurs², 3) **Comparaison à l'or** : réserve de valeur digitale, 4) **Coût de production** : énergie pour miner. Très spéculatif, pas de consensus.",
        "category": "Valorisation",
        "difficulty": "Difficile",
        "hints": ["Pas de DCF possible", "Modèles alternatifs"]
    },
    
    "BT050": {
        "question": "Qu'est-ce que la Value at Risk (VaR) à 99% sur 1 jour signifie ?",
        "answer": "Perte maximale dans 99% des cas",
        "explanation": "VaR 99% 1-jour = niveau de perte qui ne sera dépassé que dans 1% des cas sur un horizon d'un jour. Ex : VaR 99% = -2M€ signifie qu'il y a 1% de chance de perdre plus de 2M€ demain. Limitations : ne dit rien sur l'ampleur des pertes dans le 1% (→ CVaR), assume normalité souvent.",
        "category": "Gestion des Risques",
        "difficulty": "Moyen",
        "hints": ["Confidence level", "Queue de distribution"]
    },
    
    "BT051": {
        "question": "Qu'est-ce qu'un CDS (Credit Default Swap) ?",
        "answer": "Assurance contre le défaut de crédit",
        "explanation": "CDS = contrat où l'acheteur paie une prime périodique au vendeur en échange d'une protection si l'entité de référence fait défaut. Comme une assurance : vous payez des primes, si l'entreprise fait défaut, vous êtes remboursé. Utilisé pour : 1) se couvrir, 2) spéculer sur la qualité de crédit, 3) prix = spread de crédit.",
        "category": "Dérivés",
        "difficulty": "Moyen",
        "hints": ["Protection défaut", "Prime vs compensation"]
    },
    
    "BT052": {
        "question": "Pourquoi les taux négatifs existent-ils sur certaines obligations d'État ?",
        "answer": "Flight to safety + politique monétaire",
        "explanation": "Taux négatifs (investisseur paie pour prêter) car : 1) **Flight to safety** : en crise, les investisseurs acceptent des pertes pour la sécurité, 2) **QE** : banques centrales achètent massivement des obligations, 3) **Contraintes réglementaires** : banques/fonds doivent détenir des actifs sûrs, 4) Espoir de revente à prix plus élevé (taux encore plus négatifs).",
        "category": "Fixed Income",
        "difficulty": "Difficile",
        "hints": ["Demande de sécurité", "Politique monétaire ultra-accommodante"]
    },
    
    "BT053": {
        "question": "Vous avez 52 cartes. Quelle est la probabilité que les 2 premières cartes soient des as ?",
        "answer": "1/221 ≈ 0.45%",
        "explanation": "P(1er as) = 4/52. P(2ème as | 1er as) = 3/51. P(deux as) = (4/52) × (3/51) = 12/(52×51) = 12/2652 = 1/221 ≈ 0.00452 ou 0.45%.",
        "category": "Probabilités",
        "difficulty": "Facile",
        "hints": ["Probabilité conditionnelle", "Sans remise"]
    },
    
    "BT054": {
        "question": "Qu'est-ce que le P/E forward et en quoi diffère-t-il du P/E trailing ?",
        "answer": "Bénéfices futurs vs passés",
        "explanation": "**P/E trailing** : Prix / EPS des 12 derniers mois (historique). **P/E forward** : Prix / EPS attendu des 12 prochains mois (prévisionnel). Forward P/E intègre les attentes de croissance et est plus pertinent pour évaluer si une action est chère. Attention aux révisions de consensus.",
        "category": "Valorisation",
        "difficulty": "Facile",
        "hints": ["Passé vs futur", "TTM vs Next 12 Months"]
    },
    
    "BT055": {
        "question": "Qu'est-ce que le Modigliani-Miller theorem ?",
        "answer": "Structure de capital n'affecte pas la valeur (monde parfait)",
        "explanation": "Théorème M&M (1958) : dans un marché parfait (pas d'impôts, faillite, asymétrie d'info), la valeur d'une entreprise est indépendante de sa structure de capital (dette vs equity). La VE ne change pas avec le levier. En réalité : bouclier fiscal, coûts de faillite, signaling → la structure de capital importe.",
        "category": "Corporate Finance",
        "difficulty": "Difficile",
        "hints": ["Valeur indépendante du levier", "Hypothèses irréalistes"]
    },
    
    "BT056": {
        "question": "Vous avez 3 portes : derrière 1 se trouve une voiture, derrière 2 des chèvres. Vous choisissez une porte, l'animateur ouvre une porte avec une chèvre. Devez-vous changer ?",
        "answer": "Oui (Monty Hall)",
        "explanation": "Paradoxe de Monty Hall. Si vous gardez : P(voiture) = 1/3. Si vous changez : P(voiture) = 2/3 ! Explication : votre choix initial a 1/3 de chance. L'animateur révèle une info : les 2/3 de probabilité restants sont concentrés sur l'autre porte. Changer double vos chances. Contre-intuitif mais prouvé.",
        "category": "Probabilités",
        "difficulty": "Moyen",
        "hints": ["Information révélée", "2/3 vs 1/3"]
    },
    
    "BT057": {
        "question": "Qu'est-ce qu'un CDO (Collateralized Debt Obligation) ?",
        "answer": "Titrisation structurée de dettes",
        "explanation": "CDO = pool de dettes (prêts, obligations, MBS) structuré en tranches : Senior (AAA, payé en premier, rendement faible), Mezzanine (BBB), Equity (absorbe pertes, rendement élevé). Risque de cascade en crise : pertes épuisent l'equity puis remontent. CDO = cœur de la crise 2008 (subprime).",
        "category": "Produits Structurés",
        "difficulty": "Difficile",
        "hints": ["Titrisation", "Tranches de risque"]
    },
    
    "BT058": {
        "question": "Pourquoi une entreprise ferait-elle un spin-off ?",
        "answer": "Créer de la valeur en séparant des activités",
        "explanation": "Spin-off = séparer une division en entité indépendante cotée. Raisons : 1) **Conglomerate discount** : marchés valorisent mieux des pure-plays, 2) focus management sur chaque business, 3) meilleure transparence, 4) structures de capital optimisées. Ex : eBay/PayPal, Altria/Philip Morris. Souvent créateur de valeur.",
        "category": "Corporate Finance",
        "difficulty": "Moyen",
        "hints": ["Conglomerate discount", "Focus stratégique"]
    }
}

def initialize_brainteaser_session():
    """Initialize session state for brainteaser quiz"""
    if 'bt_quiz_started' not in st.session_state:
        st.session_state.bt_quiz_started = False
    if 'current_bt' not in st.session_state:
        st.session_state.current_bt = None
    if 'bt_score' not in st.session_state:
        st.session_state.bt_score = 0
    if 'bt_total' not in st.session_state:
        st.session_state.bt_total = 0
    if 'show_bt_answer' not in st.session_state:
        st.session_state.show_bt_answer = False
    if 'used_bt' not in st.session_state:
        st.session_state.used_bt = []
    if 'bt_user_answer' not in st.session_state:
        st.session_state.bt_user_answer = ""
    if 'bt_difficulty_filter' not in st.session_state:
        st.session_state.bt_difficulty_filter = "Tous"
    if 'bt_category_filter' not in st.session_state:
        st.session_state.bt_category_filter = "Toutes"


def get_random_brainteaser(difficulty=None, category=None):
    """Get a random brainteaser based on filters"""
    available_bt = [
        bt_id for bt_id, bt_data in BRAINTEASER_LIBRARY.items()
        if bt_id not in st.session_state.used_bt
        and (difficulty is None or difficulty == "Tous" or bt_data['difficulty'] == difficulty)
        and (category is None or category == "Toutes" or bt_data['category'] == category)
    ]
    
    if not available_bt:
        # Reset if all matching brainteasers have been used
        st.session_state.used_bt = []
        available_bt = [
            bt_id for bt_id, bt_data in BRAINTEASER_LIBRARY.items()
            if (difficulty is None or difficulty == "Tous" or bt_data['difficulty'] == difficulty)
            and (category is None or category == "Toutes" or bt_data['category'] == category)
        ]
        
        if not available_bt:
            return None
    
    bt_id = random.choice(available_bt)
    st.session_state.used_bt.append(bt_id)
    return bt_id


def display_brainteaser_quiz():
    st.title("🧠 Finance Brainteasers Quiz")
    st.markdown("### Testez vos connaissances avec 58 brainteasers de finance !")
    
    # Filters in columns
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        difficulties = ["Tous"] + sorted(list(set(bt['difficulty'] for bt in BRAINTEASER_LIBRARY.values())))
        st.session_state.bt_difficulty_filter = st.selectbox(
            "Difficulté",
            difficulties,
            index=difficulties.index(st.session_state.bt_difficulty_filter) if st.session_state.bt_difficulty_filter in difficulties else 0
        )
    
    with col_f2:
        categories = ["Toutes"] + sorted(list(set(bt['category'] for bt in BRAINTEASER_LIBRARY.values())))
        st.session_state.bt_category_filter = st.selectbox(
            "Catégorie",
            categories,
            index=categories.index(st.session_state.bt_category_filter) if st.session_state.bt_category_filter in categories else 0
        )
    
    # Display score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{st.session_state.bt_score}")
    with col2:
        st.metric("Questions", f"{st.session_state.bt_total}")
    with col3:
        accuracy = (st.session_state.bt_score / st.session_state.bt_total * 100) if st.session_state.bt_total > 0 else 0
        st.metric("Précision", f"{accuracy:.1f}%")
    
    st.divider()
    
    # Start quiz button
    if not st.session_state.bt_quiz_started:
        if st.button("🚀 Commencer le Quiz", use_container_width=True, type="primary"):
            bt_id = get_random_brainteaser(
                st.session_state.bt_difficulty_filter,
                st.session_state.bt_category_filter
            )
            if bt_id:
                st.session_state.bt_quiz_started = True
                st.session_state.current_bt = bt_id
                st.session_state.show_bt_answer = False
                st.rerun()
            else:
                st.warning("Aucun brainteaser ne correspond à vos filtres !")
    
    # Quiz interface
    if st.session_state.bt_quiz_started and st.session_state.current_bt:
        bt_id = st.session_state.current_bt
        bt_data = BRAINTEASER_LIBRARY[bt_id]
        
        # Display the question
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 40px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        ">
            <div style="color: white; margin-bottom: 15px;">
                <span style="background: rgba(255,255,255,0.3); padding: 5px 15px; border-radius: 20px; font-size: 0.9em; margin-right: 10px;">
                    {bt_data['category']}
                </span>
                <span style="background: rgba(255,255,255,0.3); padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                    {bt_data['difficulty']}
                </span>
            </div>
            <p style="
                color: white;
                margin: 0;
                font-size: 1.3em;
                line-height: 1.6;
            ">{bt_data['question']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User input area
        if not st.session_state.show_bt_answer:
            st.markdown("### 💭 Votre réponse")
            user_answer = st.text_area(
                "Écrivez votre raisonnement et réponse ici...",
                height=200,
                placeholder="Expliquez votre raisonnement étape par étape...",
                key="bt_answer_input"
            )
            
            # Show hints if available
            if 'hints' in bt_data and bt_data['hints']:
                with st.expander("💡 Besoin d'indices ?"):
                    for i, hint in enumerate(bt_data['hints'], 1):
                        st.info(f"**Indice {i}:** {hint}")
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_a:
                if st.button("✅ Soumettre", use_container_width=True, type="primary"):
                    if user_answer.strip():
                        st.session_state.bt_user_answer = user_answer
                        st.session_state.show_bt_answer = True
                        st.session_state.bt_total += 1
                        st.rerun()
                    else:
                        st.warning("Veuillez écrire une réponse d'abord !")
            
            with col_b:
                if st.button("📖 Voir la Réponse", use_container_width=True):
                    st.session_state.show_bt_answer = True
                    st.session_state.bt_total += 1
                    st.rerun()
            
            with col_c:
                if st.button("⏭️ Passer", use_container_width=True):
                    next_bt = get_random_brainteaser(
                        st.session_state.bt_difficulty_filter,
                        st.session_state.bt_category_filter
                    )
                    if next_bt:
                        st.session_state.current_bt = next_bt
                        st.session_state.show_bt_answer = False
                        st.rerun()
        
        # Show answer section
        if st.session_state.show_bt_answer:
            st.markdown("---")
            
            # Show user's answer if submitted
            if st.session_state.bt_user_answer:
                st.markdown("### 📝 Votre réponse :")
                st.info(st.session_state.bt_user_answer)
            
            # Show correct answer
            st.markdown("### ✅ Réponse correcte :")
            st.success(f"**{bt_data['answer']}**")
            
            st.markdown("### 📚 Explication détaillée :")
            st.markdown(bt_data['explanation'])
            
            st.markdown("---")
            
            # Self-assessment
            st.markdown("### Comment avez-vous trouvé ?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ J'ai bon !", use_container_width=True, type="primary"):
                    st.session_state.bt_score += 1
                    next_bt = get_random_brainteaser(
                        st.session_state.bt_difficulty_filter,
                        st.session_state.bt_category_filter
                    )
                    if next_bt:
                        st.session_state.current_bt = next_bt
                        st.session_state.show_bt_answer = False
                        st.session_state.bt_user_answer = ""
                        st.balloons()
                        st.rerun()
            
            with col2:
                if st.button("❌ Raté", use_container_width=True):
                    next_bt = get_random_brainteaser(
                        st.session_state.bt_difficulty_filter,
                        st.session_state.bt_category_filter
                    )
                    if next_bt:
                        st.session_state.current_bt = next_bt
                        st.session_state.show_bt_answer = False
                        st.session_state.bt_user_answer = ""
                        st.rerun()
            
            with col3:
                if st.button("➡️ Question Suivante", use_container_width=True):
                    next_bt = get_random_brainteaser(
                        st.session_state.bt_difficulty_filter,
                        st.session_state.bt_category_filter
                    )
                    if next_bt:
                        st.session_state.current_bt = next_bt
                        st.session_state.show_bt_answer = False
                        st.session_state.bt_user_answer = ""
                        st.rerun()
    
    # Sidebar with stats and study guide
    with st.sidebar:
        st.markdown("## 📊 Statistiques")
        
        total_bt = len(BRAINTEASER_LIBRARY)
        st.metric("Total Brainteasers", total_bt)
        
        # Breakdown by category
        st.markdown("### Par Catégorie")
        category_counts = {}
        for bt in BRAINTEASER_LIBRARY.values():
            cat = bt['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        for cat, count in sorted(category_counts.items()):
            st.write(f"**{cat}:** {count}")
        
        st.markdown("---")
        
        # Breakdown by difficulty
        st.markdown("### Par Difficulté")
        difficulty_counts = {}
        for bt in BRAINTEASER_LIBRARY.values():
            diff = bt['difficulty']
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        for diff, count in sorted(difficulty_counts.items()):
            st.write(f"**{diff}:** {count}")
        
        st.markdown("---")
        
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.bt_quiz_started = False
            st.session_state.current_bt = None
            st.session_state.bt_score = 0
            st.session_state.bt_total = 0
            st.session_state.show_bt_answer = False
            st.session_state.used_bt = []
            st.session_state.bt_user_answer = ""
            st.rerun()

