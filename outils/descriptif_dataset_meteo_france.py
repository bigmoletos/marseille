# pylint: disable=all
import sys
from pathlib import Path  # permet l'import des fonctions siuées dans d'autres répertoires
# sys.path.append(str(Path(__file__).resolve().parent.parent))
# Ajoutez le répertoire parent du dossier 'Datasets' au sys.path pour accéder au package 'outils'
chemin_parent = Path(__file__).resolve().parents[2]
sys.path.append(str(chemin_parent))
import logging
from gestion_logging import reconfigurer_logging

# Configuration du logger
logger = logging.getLogger('colorlog_example')

# Création du dictionnaire descriptif pour le dataset Météo France
# Dictionnaire pour la description des colonnes
descriptif_dataset_meteo_france = {
    "NUM_POSTE": "Numéro Météo-France du poste sur 8 chiffres",
    "NOM_USUEL": "Nom usuel du poste",
    "LAT": "Latitude, négative au sud (degrés et millionièmes de degré)",
    "LON": "Longitude, négative à l’ouest de GREENWICH (degrés et millionièmes de degré)",
    "ALTI": "Altitude du pied de l'abri ou du pluviomètre si pas d'abri (m)",
    "AAAAMMJJHH": "Date de la mesure (année mois jour heure)",
    "RR1": "Quantité de précipitation tombée 1 heure (mm mm)",
    "DRR1": "Durée des précipitations (mn)",
    "FF": "Force du vent moyenné sur 10 mn, mesurée à 10 m (m/s)",
    "DD": "Direction de FF (rose de 360)",
    "FXY": "Valeur maximale de FF dans l’heure (m/s)",
    "DXY": "Direction de FXY (rose de 360)",
    "HXY": "Heure de FXY (hhmm)",
    "FXI": "Force maximale du vent instantané dans l’heure, mesurée à 10 m (m/s)",
    "DXI": "Direction de FXI (rose de 360)",
    "HXI": "Heure de FXI (hhmm)",
    "FF2": "Force du vent moyenné sur 10 mn, mesurée à 2 m (m/s)",
    "DD2": "Direction de FF2 (rose de 360)",
    "FXI2": "Force maximale du vent instantané dans l’heure, mesurée à 2 m (m/s)",
    "DXI2": "Direction de FXI2 (rose de 360)",
    "HXI2": "Heure de FXI2 (hhmm)",
    "FXI3S": "Force maximale du vent moyenné sur 3 secondes dans l’heure (m/s)",
    "DXI3S": "Direction de FXI3S (rose de 360)",
    "HXI3S": "Heure de FXI3S (hhmm)",
    "T": "Température sous abri instantanée (°C)",
    "TD": "Température du point de rosée (°C)",
    "TN": "Température minimale sous abri dans l’heure (°C)",
    "HTN": "Heure de TN (hhmm)",
    "TX": "Température maximale sous abri dans l’heure (°C)",
    "HTX": "Heure de TX (hhmm)",
    "DG": "Durée de gel sous abri (T ≤ 0°C) (mn)",
    "T10": "Température à 10 cm au-dessous du sol (°C)",
    "T20": "Température à 20 cm au-dessous du sol (°C)",
    "T50": "Température à 50 cm au-dessous du sol (°C)",
    "T100": "Température à 1 m au-dessous du sol (°C)",
    "TNSOL": "Température minimale à 10 cm au-dessus du sol (°C)",
    "TN50": "Température minimale à 50 cm au-dessus du sol (°C)",
    "TCHAUSSEE": "Température de surface mesurée sur herbe ou sur bitume (°C)",
    "DHUMEC": "Durée d’humectation (mn)",
    "UM": "Humidité relative instantanée sous abri (%)",
    "U2M": "Humidité relative à 2 m (%)",
    "PA": "Pression atmosphérique au niveau de la station (hPa)",
    "PANO": "Pression atmosphérique au niveau de la mer (hPa)",
    "RR3": "Quantité de précipitation tombée 3 heures (mm mm)",
    "RR6": "Quantité de précipitation tombée 6 heures (mm mm)",
    "RR12": "Quantité de précipitation tombée 12 heures (mm mm)",
    "RR24": "Quantité de précipitation tombée 24 heures (mm mm)",
    'Station Id': 'station',
    'Date Timestamp [UTC]': 'date',
    'Date Txt [UTC]': 'date_txt',
    ' Average Wind Speed [nds]': 'vitesse_vent_(nds)',
    'Min Wind Speed [nds]': 'vitesse_vent_mini_(nds)',
    'Max Wind Speed [nds]': 'vitesse_vent_max_(nds)',
    'Wind Direction [degree]': 'direction_(°)',
    'Wind Direction [txt]': 'direction_string_(txt)',
}

# POSTE,DATE,RR1,T,TD,TN,HTN,TX,HTX,DG,TNSOL,FF,DD,FXI,DXI,HXI,FXY,DXY,HXY,U,UN,HUN,UX,HUX,UABS,DHUMI40,DHUMI80,TSV,ENTH

# Dictionnaire pour la correspondance des noms de colonnes
correspondance_noms = {
    "NUM_POSTE": "station",
    "POSTE": "station",
    "NOM_USUEL": "nom_usuel_station",
    "LAT": "latitude",
    "LON": "longitude",
    "ALTI": "altitude",
    "AAAAMMJJHH": "date",
    "DATE": "date",
    "RR1": "precipitation_(mm)",
    "DRR1": "duration_des_precipitations_(mn)",
    "FF": "vitesse_vent_(m/s)",
    "DD": "Direction_(°)",
    "FXY": "vitesse_vent_max_(m/s)",
    "DXY": "direction_vent_max_(°)",
    "HXY": "heure_vent_max",
    "FXI": "vitesse_vent_max_at_10_m_(m/s)",
    "DXI": "direction_vent_max_at_10m_(°)",
    "HXI": "heure_vent_max_at_10m",
    "FF": "vitesse_vent_moyen_at_1_m_(m/s)",
    "FF2": "vitesse_vent_moyen_at_2_m_(m/s)",
    "DD2": "direction_vent_moyen_(°)",
    "FXI2": "vitesse_vent_max_at_2_m_(m/s)",
    "DXI2": "direction_vent_max_at_2_m_(°)",
    "HXI2": "heure_vent_max_at_2_m",
    "FXI3S": "vitesse_vent_moyen_sur_3s(m/s)",
    "DXI3S": "direction_vent_moyen_sur_3s_(°)",
    "HXI3S": "heure_vent_moyen_sur_3s",
    "T": "temperature_(°C)",
    "TD": "temperature_point_de_rosee_(°C)",
    "TN": "temperature_mini_(°C)",
    "HTN": "heure_tps_mini",
    "ENTH": "Enthalpie_énergie_totale_systeme_atmospherique",
    "TX": "temperature_maxi_(°C)",
    "TSV": "temperature_sol_(°C)",
    "HTX": "heure_tps_max",
    "DG": "duration_gel_(mn)",
    "T10": "temperature_at_10_cm_(°C)",
    "T20": "temperature_at_20_cm_(°C)",
    "T50": "temperature_at_50_cm_(°C)",
    "T100": "temperature_at_1_m_(°C)",
    "TNSOL": "temperature_mini_at_10cm_(°C)",
    "TN50": "temperature_mini_at_50cm_(°C)",
    "TCHAUSSEE": "temperature_surface_(°C)",
    "DHUMEC": "duration_d’humectation_(mn)",
    "UM": "humidity_max_(%)",
    "UN": "humidity_mini_(%)",
    "U": "humidity_(%)",
    "HUN": "heure_humidité",
    "UX": "humidity_max_(%)",
    "HUX": "heure_humidity_max_(%)",
    "DHUMI40": "humidity_sup_a_40%_(%)",
    "DHUMI80": "humidity_sup_a_80%_(%)",
    "UABS": "humidity_absolue_2_m_(%)",
    "U2M": "humidity_at_2_m_(%)",
    "PA": "pression_station_(hPa)",
    "PANO": "pression_mer(hPa)",
    "RR1": "precipitation_1_heures_(mm)",
    "RR3": "precipitation_3_heures_(mm)",
    "RR6": "precipitation_6_heures_(mm)",
    "RR12": "precipitation_12_heures_(mm)",
    "RR24": "precipitation_24_heures_(mm)",
    'Station Id': 'station',
    'Date Timestamp [UTC]': 'date',
    'Date Txt [UTC]': 'date_txt',
    ' Average Wind Speed [nds]': 'vitesse_vent_(nds)',
    'Min Wind Speed [nds]': 'vitesse_vent_mini_(nds)',
    'Max Wind Speed [nds]': 'vitesse_vent_max_(nds)',
    'Wind Direction [degree]': 'direction_(°)',
    'Wind Direction [txt]': 'direction_string_(txt)',
}
# HUX,UABS,DHUMI40,DHUMI80,TSV,ENTH
# POSTE: Identifiant du poste ou de la station météorologique.
# DATE: Date et heure de l'observation.
# RR1: Quantité de précipitation tombée en 1 heure (en millimètres).
# T: Température sous abri à 2 mètres du sol (en degrés Celsius).
# TD: Température du point de rosée (en degrés Celsius), indicateur de l'humidité absolue de l'air.
# TN: Température minimale sous abri dans les 24 dernières heures (en degrés Celsius).
# HTN: Heure de la température minimale.
# TX: Température maximale sous abri dans les 24 dernières heures (en degrés Celsius).
# HTX: Heure de la température maximale.
# DG: Durée de gel (en heures ou minutes) indiquant combien de temps la température est restée à 0°C ou en dessous.
# TNSOL: Température minimale à la surface du sol.
# FF: Vitesse moyenne du vent sur 10 minutes (en mètres par seconde).
# DD: Direction d'où vient le vent (en degrés à partir du nord vrai).
# FXI: Force maximale du vent instantané dans l’heure (en mètres par seconde).
# DXI: Direction de la force maximale du vent instantané.
# HXI: Heure de la force maximale du vent instantané.
# FXY: Force maximale du vent moyennée sur une période (souvent 10 minutes) dans l'heure (en mètres par seconde).
# DXY: Direction de la rafale de vent maximale.
# HXY: Heure de la rafale de vent maximale.
# U: Humidité relative sous abri à 2 mètres du sol (en pourcentage).
# UN: Valeur minimale de l'humidité relative.
# HUN: Heure de l'humidité relative minimale.
# UX: Valeur maximale de l'humidité relative.
# HUX: Heure de l'humidité relative maximale.
# UABS: Humidité absolue (en grammes d'eau par mètre cube d'air).
# DHUMI40: Durée d'humidité relative supérieure à 40%.
# DHUMI80: Durée d'humidité relative supérieure à 80%, indicateur potentiel de présence de brouillard ou de rosée.
# TSV: Température de surface de la végétation ou du sol.
# ENTH: Enthalpie, mesure de l'énergie totale du système atmosphérique, souvent utilisée en climatisation et traitement de l'air.


def expliquer_et_renommer_colonne(nom_colonne):
    """
    Fonction pour obtenir l'explication et le nouveau nom français d'une colonne du dataset Météo France, mobilis ou windsup.

    :param nom_colonne: Le nom de la colonne dans le dataset Météo France
    :return: Une tuple contenant l'explication de la colonne et son nouveau nom français

    >>> expliquer_et_renommer_colonne('T')
    ('Température sous abri instantanée (°C)', 'temperature_(°C)')
    """
    logger.debug(f"nom_colonne : {nom_colonne}")
    explication = descriptif_dataset_meteo_france.get(nom_colonne, "Nom de colonne inconnu")
    nouveau_nom = correspondance_noms.get(nom_colonne, "Nom français non fourni")
    logger.debug(f"nom_colonne : {nom_colonne} ***** Explication trouvée: {explication} **** Nouveau nom français: {nouveau_nom}")
    # logger.debug(f"Explication trouvée: {explication}")
    # logger.debug(f"Nouveau nom français: {nouveau_nom}")
    return explication, nouveau_nom


# Traitment des colonnes des datasets au pas de 6 min forunis par méteo france
# 13103001,20210101000000,0.000000,279.050000,60,2.400000,83
# 13103001,20210101000600,0.0,279.15,60,2.8,84
# 13103001,20210101001200,0.0,279.15,60,3.1,85
# 13103001,20210101001800,0.0,279.15,80,2.6,85
#concerne les stations ["13005003","13022003","13036003","13047001","13055029","13055029","13062002","13074003","13091002","13103001","13108004","13110003","13111002"]
legende_col_dataset_meteo_france_winds_6min_10colonnes = {
    "col0": "station",
    "col1": "date",
    "col2": "précipitations_(mm)",
    "col3": "temperature_(°K)",
    "col4": "direction_(°)",
    "col5": "vitesse_vent_(m/s)",
    "col6": "humidity_(%)",
    "col7": "insolation_(mn)",
    "col8": "rayonnement_(J/m²)",
    "col9": "inconnu",
}

# Traitment des colonnes des datasets au pas de 6 min forunis par méteo france
# 13092001,20210101003600,0.0,279.75
# 13092001,20210101003000,0.0,279.85
# 13092001,20210101000600,0.0,279.85
# 13092001,20210101005400,0.0,279.45
#  station 13028004,13030001,13031002,13055001,13092001
legende_col_dataset_meteo_france_winds_6min_4colonnes = {
    "col0": "station",
    "col1": "date",
    "col2": "précipitations_(mm)",
    "col3": "temperature_(°K)",
    "col4": "humidity_(%)",
    "col5": "inconnu",
}

# station 13056002
legende_col_dataset_meteo_france_winds_6min_station_13056002 = {
    "col0": "station",
    "col1": "date",
    "col2": "direction_(°)",
    "col3": "temperature_(°K)",
    "col4": "inconnu",
}

# Spécial station méteo 13054001
# 13054001 20210202101800 0.000000 286.750000 10 1.200000 67 5 120500
# 13054001 20210202102400 0.000000 286.950000 360 1.100000 67 3 110400
legende_col_dataset_meteo_france_winds_6min_station_13054001 = {
    "col0": "station",
    "col1": "date",
    "col2": "précipitations_(mm)",
    "col3": "temperature_(°K)",
    "col4": "direction_(°)",
    "col5": "vitesse_vent_(m/s)",
    "col6": "humidity_(%)",
    "col7": "insolation_(mn)",
    "col8": "rayonnement_(J/m²)",
    "col9": "inconnu",
}


def renommer_colonne_df_meteo_france_6min(nom_colonne, nom_station, nombre_colonnes_df):
    """
    Ajuste le nom d'une colonne en fonction du nom de la station et du nombre de colonnes du DataFrame.

    Args:
        nom_station (int): Identifiant de la station météo.
        nom_colonne (str): Nom actuel de la colonne.
        nombre_colonnes_df (int): Nombre de colonnes dans le DataFrame.
        legende_col_dataset_meteo_france_winds_6min_station_13054001 (dict): Légende pour la station 13054001.
        legende_col_dataset_meteo_france_winds_6min_10colonnes (dict): Légende pour les datasets de 10 colonnes.
        legende_col_dataset_meteo_france_winds_6min_6colonnes (dict): Légende pour les datasets de 6 colonnes.

    Returns:
        str: Nouveau nom de la colonne ajusté selon la légende appropriée.

    >>> ajuster_nom_colonne(13054001, 'temp', 7, {'temp': 'Température'}, {}, {})
    'Température'
    """
    logger.info(f"Nombre de colonnes : {nombre_colonnes_df}")
    logger.warning(f"\n nom_station:\n{nom_station} ")
    logger.critical(f"\n nom_colonne:\n{nom_colonne} ")
    nouveau_nom = "Nom de colonne inconnu"  # Valeur par défaut en cas de non correspondance

    # if nom_station == 13054001:
    #     logger.debug("Traitement de la colonne avec la légende pour la station 13054001")
    #     nouveau_nom = legende_col_dataset_meteo_france_winds_6min_station_13054001.get(nom_colonne, nouveau_nom)
    if nom_station == 13056002:
        logger.debug("Traitement de la colonne avec la légende pour la station 13056002")
        nouveau_nom = legende_col_dataset_meteo_france_winds_6min_station_13056002.get(nom_colonne, nouveau_nom)
    elif nom_station in [13054001, 13005003, 13022003, 13036003, 13047001, 13055029, 13062002, 13074003, 13091002, 13103001, 13108004, 13110003, 13111002]:
        logger.debug("Traitement de la colonne avec la légende pour les stations à 10 colonnes")
        nouveau_nom = legende_col_dataset_meteo_france_winds_6min_10colonnes.get(nom_colonne, nouveau_nom)
    elif nom_station in [13028004, 13030001, 13031002, 13055001, 13092001]:
        logger.debug("Traitement de la colonne avec la légende pour les stations à 4 colonnes")
        nouveau_nom = legende_col_dataset_meteo_france_winds_6min_4colonnes.get(nom_colonne, nouveau_nom)
    else:
        logger.critical(f"Dans la station: {nom_station}, le nombre de colonnes {nombre_colonnes_df} est inattendu pour le dataset")

    logger.info(f"Nom colonne : {nom_colonne} -> Nouveau nom français : {nouveau_nom}")
    return nouveau_nom


# def renommer_colonne_df_meteo_france_6min(nom_colonne, nom_station, nombre_colonnes_df):
#     """
#     Fonction pour obtenir le nom français d'une colonne du dataset Météo France au pas de 6 min. La conversion s'adapte
#     aux nombres de colonnes du dataset, en effet dans certaines stations Météo France n'ont que 4 colonnes d'autres 8,
#     par ailleurs la colonne direction du vent est parfois la 4ème colonne, parfois la 5ème.

#     :param nom_colonne: Le nom de la colonne dans le dataset Météo France
#     :param nombre_colonnes_df: le nombre de colonnes contenues dans le df
#     :return: le nom de la colonne en français et sans espace, ni accent

#     >>> renommer_colonne_df_meteo_france_6min('col2', 10)
#     'préciptations_(mm)'
#     """
#     logger.debug(f"Nombre de colonnes : {nombre_colonnes_df}")
#     nouveau_nom = "Nom de colonne inconnu"  # Valeur par défaut en cas de non correspondance

#     if nom_station == 13054001:
#         logger.debug("Traitement de la colonne avec la légende pour la station 13054001")
#         nouveau_nom = legende_col_dataset_meteo_france_winds_6min_station_13054001.get(nom_colonne, nouveau_nom)
#     # elif nombre_colonnes_df >= 7:
#     elif nom_station in [3005003, 13022003, 13036003, 13047001, 13055029, 13055029, 13062002, 13074003, 13091002, 13103001, 13108004, 13110003, 13111002]:
#         logger.debug("Traitement de la colonne avec la légende pour 10 colonnes")
#         nouveau_nom = legende_col_dataset_meteo_france_winds_6min_10colonnes.get(nom_colonne, nouveau_nom)
#     elif nombre_colonnes_df <= 6:
#         logger.debug("Traitement de la colonne avec la légende pour 6 colonnes")
#         nouveau_nom = legende_col_dataset_meteo_france_winds_6min_6colonnes.get(nom_colonne, nouveau_nom)
#     else:
#         logger.critical(f" Dans la station: {nom_station} , le nombre de colonnes {nombre_colonnes_df} est inattendu pour le dataset")

#     logger.info(f"Nom colonne : {nom_colonne} -> Nouveau nom français : {nouveau_nom}")
#     return nouveau_nom


# def renommer_colonne_df_meteo_france_6min(nom_colonne, nombre_colonnes_df):
#     """
#     Fonction pour obtenir le nom français d'une colonne du dataset Météo France au pas de 6 min. La conversion s'adapte aux nombre de colonnes du dataset, en effet dans certaines stations meteo france n'ont que 4 colonnes d'autres 8, par ailleurs la colonne direction du vent est parfois la 4 éme colonne, parfois la 5éme

#     :param nom_colonne: Le nom de la colonne dans le dataset Météo France
#     :param nombre_colonnes_df: le nom de colonnes contenues dans le df
#     :return: le nom de la colonne en francais et sans espace, ni accent

#     >>> expliquer_et_renommer_colonne('T')
#     (col2', 'préciptations_(mm)')
#     """
#     logger.critical(f"\n nombre de colonnes :\n{nombre_colonnes_df} ")
#     if nombre_colonnes_df >= 8:
#         logger.debug(f" traitement de la colonne avec la legende pour 10colonnes ")
#         logger.debug(f"nom_colonne : {nom_colonne}")
#         nouveau_nom = legende_col_dataset_meteo_france_winds_6min_10colonnes.get(nom_colonne, "Nom de colonne inconnu")
#         # nouveau_nom = correspondance_noms.get(nom_colonne, "Nom français non fourni")
#         logger.debug(f"nom_colonne : {nom_colonne}  **** Nouveau nom français: {nouveau_nom}")
#         # logger.debug(f"Explication trouvée: {explication}")
#         # logger.debug(f"Nouveau nom français: {nouveau_nom}")
#     elif nombre_colonnes_df <= 6:
#         logger.debug(f"ntraitement de la colonne avec la legende pour 6colonnes ")
#         logger.debug(f"nom_colonne : {nom_colonne}")
#         nouveau_nom = legende_col_dataset_meteo_france_winds_6min_6colonnes.get(nom_colonne, "Nom de colonne inconnu")
#         # nouveau_nom = correspondance_noms.get(nom_colonne, "Nom français non fourni")
#         logger.debug(f"nom_colonne : {nom_colonne}  **** Nouveau nom français: {nouveau_nom}")
#         # logger.debug(f"Explication trouvée: {explication}")
#         # logger.debug(f"Nouveau nom français: {nouveau_nom}")

#     return nouveau_nom
