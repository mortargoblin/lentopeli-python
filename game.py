# LENTO-/RAHTIPELI
import mysql.connector
from geopy import distance
import random

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
    kantama = 200  # Määrittää miten kauas kone kulkee (km)
    valinnanvara = 3  # Määrittää miten monta kenttää tarjotaan per vuoro

    print("Tässä pelin loredump, selitys, avaus, yms")
    print("kirjoita help saadaksesi listan komennoista")

    ### Pelissä liikkumisen while loop tässä
    while True: 
        print("Keikat:")
        liike_lista = find_ports(sijainti,kantama,valinnanvara)
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
                        print("\nSijainti:", kentta[1])
                        jatkuu = True
                        break
                    elif i+1 == len(liike_lista):
                        print("Väärä komento, kirjoita help saadaksesi ", end="")
                        print("listan komennoista")

        



def find_ports(sij, kant, valvara):
    # Funktio tarvitsee kolme argumenttia: sijainti, kantama, valinnanvara.
    # Funktio palauttaa listan monikkoja:
    # !! [0]: ident, [1]: nimi, [2]: tyyppi, [3]: iso_country !!

    # Funktion selitys:
    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    sql = f"SELECT ident, name, type, iso_country, latitude_deg, longitude_deg FROM airport"
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta :DDD
    # Nopeutuu paljon jos poistetaan small_airport tietokannasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[4], airport[5])
        if (distance.distance(sij_deg, paamaara_deg).km < kant and 
        airport[2] != "small_airport" and airport[0] != sij):
            # Jos koneen kantama riittää, lisätään kenttä pool-listaan
            pool.append(airport)

    # Seuraavaksi valitaan lopulliset kandidaatit sattumanvaraisesti
    # Palautettavien määrän määrittää valinnanvara-muuttuja
    tulos = []
    for _ in range(valvara):
        pool_current = random.choice(pool)
        pool.remove(pool_current)
        tulos.append(pool_current)
    return tulos
    

main()