    ## RAHTIPELI KIRJASTO

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

def find_ports(sij, kant, valvara):
    # Funktio tarvitsee kolme argumenttia: sijainti, kantama, valinnanvara.
    # Funktio palauttaa listan monikkoja:
    # !! [0]: ident, [1]: nimi, [2]: tyyppi, [3]: iso_country, [4][5]: Lat ja Lon

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


def eu_map_marked(long, lat): 
    ### Tämä funktio palauttaa merkkijonon jossa euroopan kartta,
    ### sekä long ja lat arvojen kohdalla punainen "X"
    from termcolor import colored

    ### Kartta:
    map_str = """
..................................OOOOOOOOOOOOOOOO
.......................OOOOOOO....OOOOOOOOOOOOOOOO
...OOO...............OOOOOOOOOOOOOOOOOOOOOOOOOOOOO
...OOOO.............OOOOOOOOOO..OOOOOOOOOOOOOOOOOO
...................OOOOO.OOOOOOOOOOOOOOOOOOOOOOOOO
.................OOOOOO.OOOOOOOOOOOOOOOOOOOOOOOOOO
................OOOOOO...OOO.OOOOOOOOOOOOOOOOOOOOO
................OOOOOOO....OOOOOOOOOOOOOOOOOOOOOOO
........OO.........OOO...OOOOOOOOOOOOOOOOOOOOOOOOO
.....OOO.OO......O..O....OOOOOOOOOOOOOOOOOOOOOOOOO
.....OO..OOO.....OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO..
........OOOO..OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...
...........OOOOOOOOOOOOOOOOOOOOOOOOOOOO.OOOOOOOO..
........OOOOOOOOOOOOOOOOOOOOOOOOOOO.OO..OOOOOOOOOO
.........OOOOOOOOOOOOOOOOOOOOOOOOO..........OOOOOO
..OOOOO..OOOOOOOOOOOO.OOOOOOOOOOO....OOOOOOOOOOOOO
..OOOOOOOOOO......OOOO....OOOOOOOO.OOOOOOOOOOOOOOO
.OOOOOOOOO.......O..OOO....OOO...OOOOOOOOOOOOOOOOO
.OOOOOOOO.............OO....OO....OOO.OO..OOOOOOOO
...O......OOOOOO.O..OO....................OOOOOOOO
..OOOOOOOOOOOOOOOOO.......................OOOOOOOO
"""
    # Kartan leveys ja korkeus merkkeinä 
    map_width = 50
    map_height = 21

    try:
        airport_coords = {
            'longitude': long,
            'latitude': lat
        }
    except TypeError as te:
        return te

    ### Asetetaan rajat kartan long ja lat arvoille
    ### Näitä säätämällä kalibroin tekstikartan
    ### oikeiden lat, long arvojen kanssa sopivaksi
    # Longitude
    min_longitude = -15
    max_longitude = 60
    # Latitude
    min_latitude = 35
    max_latitude = 72

    ### Normalisoidaan lat ja long kartan koordinaatistoon
    normalized_longitude = ((airport_coords['longitude'] - min_longitude) / 
                        (max_longitude - min_longitude) * map_width)
    normalized_latitude = ((airport_coords['latitude'] - min_latitude) / 
                        (max_latitude - min_latitude) * map_height)
    # Tästä saadaan ns "pikseliarvot" sijainnille eli x,y kordinaatit ascii kartasta 
    pixel_position_x = int(normalized_longitude)
    pixel_position_y = int(normalized_latitude)

    ### Kirjoitetaan punainen X oikeaan kohtaan kartassa
    updated_map_str = []
    index = map_height
    # for loop jossa käsitellään jokainen kartan rivi erikseen
    for line in map_str.split('\n'):
        if pixel_position_x <= len(line):
            updated_line = list(line)
            if index == pixel_position_y:
                updated_line[pixel_position_x] = colored('X', "red")
            updated_map_str.append(''.join(updated_line))
        else:
            updated_map_str.append(line)
        index -= 1

    # Palautetaan X:llä merkitty kartta
    result = ""
    for line in updated_map_str:
        result = result + "\n" + line
    
    return result

if __name__ == "__main__":
    print(eu_map_marked(24.963301, 60.3172))