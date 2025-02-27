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

def find_ports(sij, kant, valvara, suunta):
    # Funktio tarvitsee yllämerkityt.
    # Funktio palauttaa listan monikkoja:
    # !! [0]: ident, [1]: nimi, [2]: tyyppi, [3]: iso_country, [4][5]: Lat ja Lon

    # Funktion selitys:
    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    sql = f"SELECT ident, name, type, iso_country, latitude_deg, longitude_deg FROM airport WHERE NOT type='small_airport'"
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta :DDD
    # Nopeutuu paljon jos poistetaan small_airport tietokannasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[4], airport[5])
        if (distance.distance(sij_deg, paamaara_deg).km < kant and 
        airport[0] != sij):
            if suunta=="N": #north
                if paamaara_deg[0] > sij_deg[0]:
                    pool.append(airport)
            elif suunta=="W": #west
                if paamaara_deg[1] < sij_deg[1]:
                    pool.append(airport)
            elif suunta=="S": #south
                if paamaara_deg[0] < sij_deg[0]:
                    pool.append(airport)
            elif suunta=="E": #east
                if paamaara_deg[1] > sij_deg[1]:
                    pool.append(airport)
            else:
                pass

    # Seuraavaksi valitaan lopulliset kandidaatit sattumanvaraisesti
    # Palautettavien määrän määrittää valinnanvara-muuttuja
    tulos = []
    for _ in range(valvara):
        try:
            pool_current = random.choice(pool)
            pool.remove(pool_current)
            tulos.append(pool_current)
        except IndexError:
            return False
    return tulos


def eu_map_marked(long, lat, targets = None): 
    ### Tämä funktio ottaa longitude ja latitude arvot siinä järjestyksessä
    ### ja palauttaa kartan merkkijonon muodossa, jossa punainen X
    ### longitude ja latitude arvojen ylimalkaisessa sijainnissa


    ### Kartta:
    map_str = """
x-------x.........................OOOOOOOOOOOOOOOO
|   N   |..............OOOOOOO....OOOOOOOOOOOOOOOO
| W + E |............OOOOOOOOOOOOOOOOOOOOOOOOOOOOO
|   S   |...........OOOOOOOOOO..OOOOOOOOOOOOOOOOOO
x-------x..........OOOOO.OOOOOOOOOOOOOOOOOOOOOOOOO
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
..OOOOOOOOOOOOOOOOO.......................OOOOOOOO"""
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
    normalized_longitude = ((airport_coords["longitude"] - min_longitude) / 
                        (max_longitude - min_longitude) * map_width)
    normalized_latitude = ((airport_coords["latitude"] - min_latitude) / 
                        (max_latitude - min_latitude) * map_height)
    # Tästä saadaan ns "pikseliarvot" sijainnille eli x,y kordinaatit ascii kartasta 
    pixel_position_x = int(normalized_longitude)
    pixel_position_y = int(normalized_latitude)

    ### Kirjoitetaan punainen X oikeaan kohtaan kartassa
    updated_map_str = []
    index = map_height

    # For loop jossa käsitellään jokainen kartan rivi erikseen
    for line in map_str.split('\n'):
        if pixel_position_x <= len(line):
            updated_line = list(line)
            # Jos pikselin x ja y arvot täsmäävät, on löydetty äksän sijainti 
            if index == pixel_position_y:
                # Laitetaan X paikalleen
                updated_line[pixel_position_x] = "X"
            updated_map_str.append("".join(updated_line))
        else:
            updated_map_str.append(line)
        index -= 1

    if targets != None:
        for target in targets:
            pixel_position_x = int((target[1] - min_longitude) / 
                    (max_longitude - min_longitude) * map_width)
            pixel_position_y = int((target[0] - min_latitude) / 
                    (max_latitude - min_latitude) * map_height)
            
            index = map_height
            for i in range(len(updated_map_str)):
                if pixel_position_x <= len(updated_map_str[i]):
                    updated_line = list(updated_map_str[i])
                    if index==pixel_position_y:
                        updated_line[pixel_position_x] = "?"
                    updated_map_str[i] = "".join(updated_line)
                else:
                    updated_map_str[i] = updated_line
                index -= 1
    # Palautetaan X:llä merkitty kartta
    tulos = str()
    if targets == None:
        for line in updated_map_str:
            tulos = tulos + line + "\n"
            pass
        return tulos
    if targets != None:
        for i in range(len(updated_map_str)):
            # Laastari bugille tässä
            if i != 0:
                tulos = tulos + updated_map_str[i] + "\n"
        return tulos

def upgrade_airplane():

    lentokone1 = {"type" : "Lilla Damen 22",
                  "kantama" : 700,
                  "kohteet" : 5,
                  "kerroin" : 1
                  }

    print("Haluatko päivittää lentokonetta tai sen osia K/E?")
    paivitys = input(">>>")
    if paivitys == "K":
        print("Koneet ja niiden ominaisuudet.")
        koneet = f"""x-----------------------------------------------------------------------------------x
|   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 700 / Kerroin: 1.25 / hinta 20000000 € |
|   2. Kone = Tyyppi: Nanny 24 / Kantama: 1400 / Kerroin: 1.6 / hinta 200000000 €   |
|   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 2000 / kerroin: 2.0 500000000 €  |
x-----------------------------------------------------------------------------------x"""

        return koneet
    #1 Lilla Damen 22
    #2 Stor Dam 23
    #3 Nanny 24
    #4 Mamma Birgitta 25
    #if Nanny 24 And somtihing else bath to Lokheed BalckBird

#koneet = f"""x------------------------------------------------------------------------------x
  #  |   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 700 / Kerroin: 1.25{64}|
   # |   2. Kone = Tyyppi: Nanny 24 / Kantama: 1400 / Kerroin: 1.6{64}|
  #  |   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 2000 / kerroin: 2.0{64}|
   # x------------------------------------------------------------------------------x"""