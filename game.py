# LENTO-/RAHTIPELI

# Huom! funktiot tuolla
import flight_lib
from flight_lib import raha, lentokone_di


import random
import mysql.connector
from geopy import distance

yhteys = mysql.connector.connect (
host='127.0.0.1',
port= 3306,
database='rahtipeli',
user='pythonuser',  # HUOM käyttäjä: pythonuser
password='salainen-sana',  # HUOM salasana
autocommit=True,
collation='utf8mb3_general_ci'
)
kursori = yhteys.cursor()

### Keskeiset muttujat:

# Tämänhetkisen sijainnin arvot on sanakirjassa.
# Jos haluaa esimerkiksi käyttää sijainnin nimeä 
# (Helsinki-Vantaa...) tulee käyttää sijainti["nimi"]
sijainti = {
    "ident": "EFHK", # Tämänhetkinen ICAO-koodi, lähtöpaikka
    "deg": (60.3172, 24.963301), # Tämänhetkiseen sijainnin lat, long
    "nimi": "Helsinki-Vantaa Airport"
}

kantama = 300  # Määrittää miten kauas kone kulkee (km)
valinnanvara = 5  # Määrittää miten monta kenttää tarjotaan per vuoro

#importtaa flight raha yksikön


# Pelin aloitus
print("Tässä pelin loredump, selitys, avaus, yms")
print("..........")
print("kirjoita help saadaksesi listan komennoista kun peli on alkanut")
input("paina [ENTER] jataaksesi")

suunta_valittu = False


### Pelin "main" loop tässä
while True: 
    # "stats_prompt" näyttää pelaajalle hyödyllistä infoa.
    stats_prompt = f"""x------------------------------------------------x
|   Raha:       {(str(raha["euroa"])+'€').ljust(33)}|
|   Sijainti:   {sijainti["nimi"].ljust(33)}|
|   Lentokone:  {lentokone_di["tyyppi"].ljust(33)}|
x------------------------------------------------x"""
    #Koneen päivitys kysely

    # Tässä kartta. huom: eu_map_marked(long, lat) ottaa long ja lat arvot
    # argumentteina ja palauttaa kartan merkijonona jossa punainen
    # X merkitsee long ja lat arvojen ylimalkaisen sijainnin
    jatkuu = False
    if suunta_valittu == False:
        print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
        print(stats_prompt)
        print("Valitse suunta [N/W/S/E]")
    else:
        # Kutsutaan liike_lista funktio, joka palauttaa mahdolliset keikat
        liike_lista = flight_lib.find_ports(sijainti["ident"],kantama,valinnanvara,suunta)
        if liike_lista != False:
            liike_lista_str = ""
            target_lista = []
            for kentta in liike_lista:
                # kentta_stats tallennetaan musitiin uudelleenkäyttöä varten
                target_lista.append((kentta["lat"], kentta["long"]))
                liike_lista_str += f"{kentta["ident"]} | {kentta["name"]} / {kentta["type"]} / {kentta["iso_country"]} {"\n"}"

            print(flight_lib.eu_map_marked(sijainti["deg"][1],sijainti["deg"][0],target_lista),end="")
            print(stats_prompt)
            print("Keikat" + "\n" + liike_lista_str)
            print("Valitse keikka antamalla kohteen ICAO-koodi")
        else:
            suunta_valittu = False
            print("Suunnassa ei riittävästi lentokenttiä. Valitse toinen suunta")
            jatkuu = True
    
    while jatkuu == False:
        komento = input(">>> ")
    
        # Tarkistetaan onko komento joku ilmansuunnista
        if suunta_valittu == False and komento.upper() in "NWSE" and len(komento) == 1:
            suunta = komento.upper()
            suunta_valittu = True
            break

        # tämä jakaa inputin listaksi, jotta argumentteja voidaan
        # käsitellä erikseen
        komento_args = komento.split(" ")

        # Tässä kohtaa tarkistetaan onko input joku komennoista.
        # Komennot voi olla esim. päivityksiin yms.
        if komento.upper() == "HELP":
            # tähän listätään kaikki komennot, kun ne on keksitty
            print("Päivitä: Pääset päivittämään konettasi.")
            print("[Q]: Poistu")
            print("SHOW icao: näyttää haluamasi lentokentän sijainnin kartalla. Esim. EDDB")
            print("PROMPT: Näyttää kartan, statsit ja keikat uudestaan")

        # Tässä show komento, joka näyttää lentokentän sijainnin kartalla
        elif komento.upper() == "PÄIVITÄ":
            print(flight_lib.upgrade_airplane(raha, lentokone_di))

        elif komento_args[0].upper() == "SHOW":
            if len(komento_args) < 1:
                show_ident = komento_args[1]
                sql = f"SELECT longitude_deg, latitude_deg, name FROM airport WHERE ident='{show_ident}'"
                kursori.execute(sql)
                show_ident = kursori.fetchone()
                print(flight_lib.eu_map_marked(show_ident[0], show_ident[1]))
                print(show_ident[2])
            else: 
                print("Komento vaatii kaksi argumenttia")

        # Prompt-komento näyttää kartan ja statsit uudestaan
        elif komento.upper() == "PROMPT":
            print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
            print(stats_prompt)
            if suunta_valittu == True:
                print("Keikat:" + "\n" + liike_lista_str)

        # Poistumiskomento
        elif komento.upper() == "Q":
            exit()

        elif suunta_valittu == False:
            # Jos komentoa ei tunnistettu eikä suuntaa vielä valittu
            print("Komento ei ole tunnistettava suunta [N/W/S/E] tai muu tuttu komento")
            print("Kirjoita help saadaksesi listan komennoista")

        else:
            # For loop etsii käyttäjän syöttämää ICAO - koodia vastaavaa 
            # lentokenttää, ja muuttaa sijainnin sen mukaiseksi
            for i in range(len(liike_lista)):
                if komento.upper() == liike_lista[i]["ident"]:
                    # Jos pätevä icao-koodi löytyy, sijainti päivitetään
                    sijainti = {
                        "ident": liike_lista[i]["ident"],
                        "deg": (liike_lista[i]["lat"], liike_lista[i]["long"]),
                        "nimi": liike_lista[i]["name"]
                    }
                    suunta_valittu = False
                    jatkuu = True
                    break
                # Jos lentokenttää ei löytynyt eikä komentoa tunnistettu
                elif i+1 == len(liike_lista):
                    print("Väärä komento, kirjoita help saadaksesi ", end="")
                    print("listan komennoista")
