# ***************************************************************
# Nom ......... : exercice_4_2_streamlit_exif_simple.py
# Rôle ........ : Créer une application Streamlit permettant :
#                 - de charger une photographie JPEG ;
#                 - de modifier plusieurs métadonnées EXIF ;
#                 - d'ajouter des coordonnées GPS ;
#                 - d'afficher ces coordonnées sur une carte ;
#                 - d'afficher plusieurs lieux visités sur une seconde carte.
# Auteur ...... : Suad Smajic
# Version ..... : V1.0 du 25/07/2026
# Licence ..... : Réalisé dans le cadre du cours
#                 Outils informatiques collaboratifs.
#
# Installation :
#     python -m pip install streamlit exif folium streamlit-folium
#
# Exécution :
#     streamlit run exercice_4_2_streamlit_exif_simple.py
# ***************************************************************


# -----------------------------
# Importation des bibliothèques
# -----------------------------

import streamlit as st

from exif import Image
from folium import Map, Marker, PolyLine
from streamlit_folium import st_folium


# -----------------------------
# Fonctions simples
# -----------------------------

def decimal_vers_dms(coordonnee):
    """
    Transforme une coordonnée décimale
    en degrés, minutes et secondes.
    """

    coordonnee = abs(coordonnee)

    degres = int(coordonnee)

    minutes_decimales = (coordonnee - degres) * 60
    minutes = int(minutes_decimales)

    secondes = (minutes_decimales - minutes) * 60

    return degres, minutes, secondes


def enregistrer_metadonnees(
    contenu_image,
    auteur,
    description,
    logiciel,
    fabricant,
    modele,
    date_originale,
    commentaire,
    latitude,
    longitude,
    altitude
):
    """
    Ajoute les métadonnées saisies
    dans une nouvelle copie de l'image.
    """

    image_exif = Image(contenu_image)

    # Métadonnées textuelles.
    image_exif.artist = auteur
    image_exif.image_description = description
    image_exif.software = logiciel
    image_exif.make = fabricant
    image_exif.model = modele
    image_exif.datetime_original = date_originale
    image_exif.user_comment = commentaire

    # Conversion de la latitude.
    latitude_dms = decimal_vers_dms(latitude)
    image_exif.gps_latitude = latitude_dms

    if latitude >= 0:
        image_exif.gps_latitude_ref = "N"
    else:
        image_exif.gps_latitude_ref = "S"

    # Conversion de la longitude.
    longitude_dms = decimal_vers_dms(longitude)
    image_exif.gps_longitude = longitude_dms

    if longitude >= 0:
        image_exif.gps_longitude_ref = "E"
    else:
        image_exif.gps_longitude_ref = "W"

    # Altitude.
    image_exif.gps_altitude = abs(altitude)

    if altitude >= 0:
        image_exif.gps_altitude_ref = 0
    else:
        image_exif.gps_altitude_ref = 1

    return image_exif.get_file()


# -----------------------------
# Configuration de la page
# -----------------------------

st.set_page_config(
    page_title="Photographie EXIF et cartes",
    page_icon="📷"
)

st.title("Photographie, métadonnées EXIF et cartes")

st.write(
    "Cette application permet de modifier plusieurs métadonnées "
    "d'une photographie JPEG et d'afficher des lieux sur des cartes."
)


# -----------------------------
# Chargement de la photographie
# -----------------------------

fichier = st.file_uploader(
    "Choisissez une photographie JPEG",
    type=["jpg", "jpeg"]
)

if fichier is None:
    st.info("Choisissez une photographie pour commencer.")
    st.stop()

contenu_image = fichier.read()

st.subheader("Photographie choisie")
st.image(contenu_image, caption=fichier.name)


# -----------------------------
# Formulaire EXIF
# -----------------------------

st.subheader("Modification des métadonnées")

with st.form("formulaire_exif"):

    auteur = st.text_input(
        "Auteur",
        value="Suad Smajic"
    )

    description = st.text_input(
        "Description de l'image",
        value="Photographie utilisée pour l'exercice 4.2"
    )

    logiciel = st.text_input(
        "Logiciel",
        value="Application Streamlit"
    )

    fabricant = st.text_input(
        "Fabricant de l'appareil",
        value=""
    )

    modele = st.text_input(
        "Modèle de l'appareil",
        value=""
    )

    date_originale = st.text_input(
        "Date et heure originales",
        value="2026:07:25 12:00:00"
    )

    commentaire = st.text_area(
        "Commentaire",
        value="Métadonnées modifiées dans le cadre du TP 4."
    )

    st.write("Coordonnées GPS à inscrire dans la photographie")

    latitude = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=28.0601,
        format="%.6f"
    )

    longitude = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=-16.7334,
        format="%.6f"
    )

    altitude = st.number_input(
        "Altitude en mètres",
        value=0.0
    )

    bouton = st.form_submit_button(
        "Créer la photographie modifiée"
    )


# -----------------------------
# Création de l'image modifiée
# -----------------------------

if bouton:

    try:
        image_modifiee = enregistrer_metadonnees(
            contenu_image,
            auteur,
            description,
            logiciel,
            fabricant,
            modele,
            date_originale,
            commentaire,
            latitude,
            longitude,
            altitude
        )

        st.success(
            "La photographie contenant les nouvelles "
            "métadonnées a été créée."
        )

        st.download_button(
            "Télécharger la photographie modifiée",
            data=image_modifiee,
            file_name="photographie_modifiee.jpg",
            mime="image/jpeg"
        )

    except Exception as erreur:

        st.error(
            "La photographie n'a pas pu être modifiée : "
            + str(erreur)
        )


# -----------------------------
# Première carte : photographie
# -----------------------------

st.subheader("Carte correspondant aux coordonnées GPS")

carte_photo = Map(
    location=[latitude, longitude],
    zoom_start=11
)

Marker(
    [latitude, longitude],
    popup="Emplacement de la photographie",
    tooltip="Photographie"
).add_to(carte_photo)

st_folium(
    carte_photo,
    height=450
)


# -----------------------------
# Deuxième carte : lieux visités
# -----------------------------

st.subheader("Carte de quelques lieux visités")

# Liste simple contenant mes points d'intérêt.
lieux = [
    {
        "nom": "Luxembourg",
        "latitude": 49.6116,
        "longitude": 6.1319
    },
    {
        "nom": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522
    },
    {
        "nom": "Francfort",
        "latitude": 50.1109,
        "longitude": 8.6821
    },
    {
        "nom": "Interlaken",
        "latitude": 46.6863,
        "longitude": 7.8632
    },
    {
        "nom": "Playa de las Americas",
        "latitude": 28.0601,
        "longitude": -16.7334
    }
]

carte_voyages = Map(
    location=[46.0, 3.0],
    zoom_start=4
)

coordonnees_lieux = []

for lieu in lieux:

    coordonnees = [
        lieu["latitude"],
        lieu["longitude"]
    ]

    coordonnees_lieux.append(coordonnees)

    Marker(
        coordonnees,
        popup=lieu["nom"],
        tooltip=lieu["nom"]
    ).add_to(carte_voyages)

PolyLine(
    coordonnees_lieux,
    tooltip="Ligne reliant les lieux"
).add_to(carte_voyages)

st_folium(
    carte_voyages,
    height=500
)
