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
    password='salainen-sana',  #HUOM salasana
    autocommit=True,
    collation='utf8mb3_general_ci'
    )
kursori = yhteys.cursor()

def main(): # MAIN FUNKTIO
    sijainti = "EFHK"  # Tämän hetkinen sijainti, lähtöpaikka
    kantama = 300  # Määrittää miten kauas kone kulkee (km)
    valinnanvara = 3  # Määrittää miten monta kenttää tarjotaan per vuoro

    print("Tässä pelin loredump, selitys, avaus, yms")
    print("kirjoita help saadaksesi listan komennoista")

    ### Pelissä liikkumisen while loop tässä
    while True: 
        try:
            # Laitoin kartan tähän testausta vatten :)
            # On hieno
            print(flight_lib.eu_map_marked(sijainti_deg[1], sijainti_deg[0]))
        except:
            pass
        print("Keikat:")
        liike_lista = flight_lib.find_ports(sijainti,kantama,valinnanvara)
        for kentta in liike_lista:
            print(f"{kentta[0]} | {kentta[1]} / {kentta[2]} / {kentta[3]}")
        
        # Tässä while loop joka kysyy inputteja ja tarkistaa niitä
        jatkuu = False
        while jatkuu == False:
            print("\nValitse keikka antamalla kohteen ICAO-koodi")
            liike_valinta = input("> ")
            # Tässä kohtaa tarkistetaan onko input joku komennoista.
            # Komennot voi olla esim. päivityksiin yms.
            if liike_valinta.upper() == "HELP":
                # tähän listätään kaikki komennot, kun ne on keksitty
                print("[Q] postuaksesi..") 
            elif liike_valinta.upper() == "Q":
                exit()
            else:
                # Tämä pyörii vain jos tunnistettavaa komentoa ei löydy
                # For loop tarkistaa onko input joku listatuista icao-koodeista
                for i in range(len(liike_lista)):
                    if liike_valinta.upper() == liike_lista[i][0]:
                        # Jos pätevä icao-koodi löytyy, sijainti päivitetään
                        sijainti = liike_lista[i][0]
                        sijainti_deg = (liike_lista[i][4], liike_lista[i][5])
                        print("\nSijainti:", kentta[1])
                        jatkuu = True
                        break
                    elif i+1 == len(liike_lista):
                        print("Väärä komento, kirjoita help saadaksesi ", end="")
                        print("listan komennoista")

    
if __name__ == "__main__":
    main()