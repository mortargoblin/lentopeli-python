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
            tulos.append({
                "ident": pool_current[0],
                "name": pool_current[1],
                "type": pool_current[2],
                "iso_country": pool_current[3],
                "lat": pool_current[4],
                "long": pool_current[5],
                })

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
                try:
                    tulos = tulos + updated_map_str[i] + "\n"
                except TypeError as te:
                    print("")
        return tulos

#Rahan määrä käyttäjällä

raha = {"euroa": 10000000000}
lentokone_di = {"tyyppi": "Lilla Damen 22", "kantama": 300, "kerroin": 1, "hinta": 2000000}

#Päivitykset, kesken!!!!!
def upgrade_airplane(raha, lentokone_di):
        print("Haluatko päivittää lentokonetta tai sen osia K/E?")
        paivitys = input(">")
        if paivitys.upper() == "K":
            print("Koneet ja niiden ominaisuudet.")
            koneet = f"""x-----------------------------------------------------------------------------------x
|   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 700 / Kerroin: 1.25 / hinta 20000000 € |
|   2. Kone = Tyyppi: Nanny 24 / Kantama: 1400 / Kerroin: 1.6 / hinta 200000000 €   |
|   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 2000 / kerroin: 2.0 500000000 €  |
x-----------------------------------------------------------------------------------x"""
            print(koneet)
            print(f'Sinulla on rahaa {str(raha["euroa"])} €')
            print("Valitse haluamasi päivitys numerolla.")
            valinta = input(">>>")

            #Päivittää Stor Dam 23
            if valinta == "1":
                if lentokone_di["tyyppi"] == "Stor Dam 23":
                    print("Sinulla on jo tämä kone!")
                else:
                    if raha["euroa"] >= 20000000:
                        lentokone_di.update({"tyyppi": "Stor Dam 23", "kantama": 700, "kerroin": 1.25, "hinta": 20000000})
                        raha.update({"euroa" : (float(raha["euroa"]) - 20000000)})
                        return print("Päivitys onnistui")
                    else:
                        print("Rahasi eivät riitä")

            #Päivittää
            elif valinta == "2":
                if lentokone_di["tyyppi"] == "Nanny 24":
                    print("Sinulla on jo tämä kone!")
                else:
                    if raha["euroa"] >= 500000000:
                        lentokone_di.update({"tyyppi": "Nanny 24", "kantama": 1400, "kerroin": 1.6, "hinta": 500000000})
                        raha.update({"euroa": (float(raha["euroa"]) - 500000000)})
                        return print("Päivitys onnistui")
                    else:
                        print("Rahasi eivät riitä")

            elif valinta == "3":
                if lentokone_di["tyyppi"] == "Mamma Birgitta":
                    print("Sinulla on jo tämä kone!")
                else:
                    if raha["euroa"] >= 900000000:
                        lentokone_di.update({"tyyppi": "Mamma Birgitta", "kantama": 1900, "Kerroin": 1.9, "hinta": 900000000})
                        raha.update({"euroa": (float(raha["euroa"]) - 900000000)})
                        return print("Päivitys onnistui")
                    else:
                        print("Rahasi eivät riitä")
        else:
            return




