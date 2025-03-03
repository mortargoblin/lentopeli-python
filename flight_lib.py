## RAHTIPELI KIRJASTO

import random
import mysql.connector
from geopy import distance


# Color class tekstin värittelyä varten
class Color:
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'


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
    # Funktio palauttaa listan sanakirjoja, joissa jokaisessa:
    # "ident", "name", "type", "iso_country", "lat", "long"

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    sql = f"SELECT ident, name, type, iso_country, latitude_deg, longitude_deg FROM airport WHERE NOT type='small_airport'"
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta
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
            tulos.append({
                "ident": pool_current[0],
                "name": pool_current[1],
                "type": pool_current[2],
                "iso_country": pool_current[3],
                "lat": pool_current[4],
                "long": pool_current[5],
                })
        except IndexError as ie:
            print(ie)
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

    # Väritetään X:t ja ?:t
    for line in range(len(updated_map_str)):
        updated_line = list(updated_map_str[line])
        for column in range(len(updated_line)):
            if updated_line[column] == "X":
                updated_line[column] = f"{Color.fg.red}X{Color.reset}"
                updated_map_str[line] = "".join(updated_line)
            elif updated_line[column] == "?":
                updated_line[column] = f"{Color.fg.yellow}?{Color.reset}"
                updated_map_str[line] = "".join(updated_line)
    
    # Palautetaan X:llä merkitty kartta
    tulos = str()
    for i in range(len(updated_map_str)):
        if targets != None and i == 0:
            # Laastari bugiin :(
            pass
        else:            
            tulos += updated_map_str[i] + "\n"
    return tulos


#Päivitykset, kesken!!!!!
def upgrade_airplane(raha, valinta, lentokone_di):
    if valinta == "1":
        if raha >= 200000:
            if lentokone_di["tyyppi"] != "Stor Dam 23":
                arvot = {"tyyppi": "Stor Dam 23", "kantama": 700, "kerroin": 1.4, "hinta": 200000}
                vahennys = raha - 200000
                return arvot, vahennys
    elif valinta == "2":
        if raha >= 1000000:
            if lentokone_di["tyyppi"] != "Nanny 24":
                paivitys = {"tyyppi": "Nanny 24", "kantama": 1400, "kerroin": 1.6, "hinta": 1000000}
                vahennys = raha - 1000000
                return paivitys, vahennys
    elif valinta == "3":
        if raha >= 1500000:
            if lentokone_di["tyyppi"] != "Mamma Birgitta 25":
                paivitys = {"tyyppi": "Mamma Birgitta 25", "kantama": 1700, "kerroin": 2, "hinta": 1500000}
                vahennys = raha - 1500000
                return paivitys, vahennys
    else:
        return None




