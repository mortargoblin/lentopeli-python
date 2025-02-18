# LENTO-/RAHTIPELI

# Huom! funktiot tuolla
import flight_lib

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

def main(): # MAIN FUNKTIO

    ### Keskeiset muttujat:

    # Tämänhetkisen sijainnin arvot on sanakirjassa.
    # Jos haluaa esimerkiksi käyttää sijainnin nimeä 
    # (Helsinki-Vantaa...) tulee käyttää sijainti["nimi"]
    sijainti = {
        "ident": "EFHK", # Tämänhetkinen ICAO-koodi, lähtöpaikka
        "deg": (60.3172, 24.963301), # Tämänhetkiseen sijainnin long, lat
        "nimi": "Helsinki-Vantaa Airport"
    }

    kantama = 300  # Määrittää miten kauas kone kulkee (km)
    valinnanvara = 5  # Määrittää miten monta kenttää tarjotaan per vuoro

    raha = 10000000000000 #rahaa


    # Pelin aloitus
    print("Tässä pelin loredump, selitys, avaus, yms")
    print("..........")
    print("kirjoita help saadaksesi listan komennoista kun peli on alkanut")
    input("paina [ENTER] jataaksesi")

    ### Pelin "main" loop tässä
    while True: 
        # "stats_prompt" näyttää pelaajalle hyödyllistä infoa.
        # Sitä voi muokata miten lystää ja sen voi printata: print(stats_prompt)
        # Muuttuja on pääloopin alussa sillä sen pitää päivittyä joka kierros
        stats_prompt = f"""x------------------------------------------------x
|   Raha:       {(str(raha)+'€').ljust(33)}|
|   Sijainti:   {sijainti["nimi"].ljust(33)}|
x------------------------------------------------x"""

        try:
            # Tässä kartta. huom: eu_map_marked(long, lat) ottaa long ja lat arvot
            # argumentteina ja palauttaa kartan merkijonona jossa punainen
            # X merkitsee long ja lat arvojen ylimalkaisen sijainnin
            print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
        except:
            pass
        
        print(stats_prompt)
        print("Keikat:")
        liike_lista = flight_lib.find_ports(sijainti["ident"],kantama,valinnanvara)
        for kentta in liike_lista:
            print(f"{kentta[0]} | {kentta[1]} / {kentta[2]} / {kentta[3]}")
        
        # Tässä while loop joka kysyy inputteja ja tarkistaa niitä
        jatkuu = False
        while jatkuu == False:
            print("\nValitse keikka antamalla kohteen ICAO-koodi")
            liike_valinta = input("> ")

            # tämä jakaa inputin listaksi, jotta argumentteja voidaan
            # käsitellä erikseen
            liike_valinta_args = liike_valinta.split(" ")

            # Tässä kohtaa tarkistetaan onko input joku komennoista.
            # Komennot voi olla esim. päivityksiin yms.
            if liike_valinta.upper() == "HELP":
                # tähän listätään kaikki komennot, kun ne on keksitty
                print("[Q]: Poistu")
                print("SHOW icao: näyttää haluamasi lentokentän sijainnin kartalla. Esim. EDDB")
                print("PROMPT: Näyttää kartan, statsit ja keikat uudestaan")

            # Tässä show komento, joka näyttää lentokentän sijainnin kartalla
            elif liike_valinta_args[0].upper() == "SHOW":
                try:
                    show_ident = liike_valinta_args[1]
                    sql = f"SELECT longitude_deg, latitude_deg, name FROM airport where ident='{show_ident}'"
                    kursori.execute(sql)
                    show_ident = kursori.fetchone()
                    print(flight_lib.eu_map_marked(show_ident[0], show_ident[1]))
                    print(show_ident[2])
                except:
                    print("epäonnistui :D")

            # Prompt-komento näyttää kartan ja statsit uudestaan
            elif liike_valinta.upper() == "PROMPT":
                print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
                print(stats_prompt)
                for kentta in liike_lista:
                    print(f"{kentta[0]} | {kentta[1]} / {kentta[2]} / {kentta[3]}")

            # Poistumiskomento
            elif liike_valinta.upper() == "Q":
                exit()

            else:
                # For loop etsii käyttäjän syöttämää ICAO - koodia vastaavaa 
                # lentokenttää, ja muuttaa sijainnin sen mukaiseksi
                for i in range(len(liike_lista)):
                    if liike_valinta.upper() == liike_lista[i][0]:
                        # Jos pätevä icao-koodi löytyy, sijainti päivitetään
                        sijainti = {
                            "ident": liike_lista[i][0],
                            "deg": (liike_lista[i][4], liike_lista[i][5]),
                            "nimi": liike_lista[i][1]
                        }
                        jatkuu = True
                        break
                    # Jos lentokenttää ei löytynyt
                    elif i+1 == len(liike_lista):
                        print("Väärä komento, kirjoita help saadaksesi ", end="")
                        print("listan komennoista")

    
if __name__ == "__main__":
    main()