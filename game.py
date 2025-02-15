# LENTO-/RAHTIPELI
import mysql.connector
from geopy import distance
import random

yhteys = mysql.connector.connect (
    host='127.0.0.1',
    port= 3306,
    database='rahtipeli',
    user='pythonuser', # HUOM käyttäjä: pythonuser
    password='salainen-sana', #HUOM: salasana
    autocommit=True,
    collation='utf8mb3_general_ci'
    )
kursori = yhteys.cursor()

def main(): # MAIN FUNKTIO
    sijainti = "EFHK" # Tämän hetkinen sijainti, ylikirjoitettava
    kantama = 160 # Määrittää miten kauas kone kulkee (km)
    valinnanvara = 3 # Määrittää miten monta kenttää tarjotaan per vuoro

    # Tässä esimerkki find_ports() funktion käytöstä
    liike_lista = find_ports(sijainti,kantama,valinnanvara)
    for kentta in liike_lista:
        print(f"{kentta[0]} | {kentta[1]}  /  {kentta[2]}")




def find_ports(sij, kant, valvara):
    # Funktio tarvitsee kolme argumenttia: sijainti, kantama, valinnanvara.
    # Funktio palauttaa listan monikkoja:
    # !! [0]: ident, [1]: nimi, [2]: tyyppi !!

    # Funktion selitys:
    # Ensimmäiseksi lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamainitut tiedot.
    sql = f"SELECT ident, name, type, latitude_deg, longitude_deg FROM airport"
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden :DDD
    # Nopeutuu paljon jos poistetaan small_airport tietokannasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[3], airport[4])
        if (distance.distance(sij_deg, paamaara_deg).km < kant and 
        airport[2] != "small_airport" and airport[0] != sij):
            # Jos koneen kantama riittää, lisätään kenttä pool-listaan
            pool.append(airport)
    # Seuraavaks valitaan lopulliset kandidaatit sattumanvaraisesti
    # Palautettavien määrän määrää valvara - muuttuja
    tulos = []
    for _ in range(valvara):
        pool_current = random.choice(pool)
        pool.remove(pool_current)
        tulos.append(pool_current)
    return tulos
    

main()