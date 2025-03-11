## RAHTIPELI KIRJASTO

import sys
import random
import mysql.connector
import flight_art
from flight_art import Color
from geopy import distance
from time import sleep

# Color class tekstin värittelyä varten


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
    sql = (f"SELECT ident, name, type, iso_country, latitude_deg,"
           " longitude_deg FROM airport WHERE NOT type='small_airport'")
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[4], airport[5])
        if (distance.distance(sij_deg, paamaara_deg).km < kant and 
        airport[0] != sij and paamaara_deg[1] < 55):
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
    for i in range(valvara):
        try:
            pool_current = random.choice(pool)
            pool.remove(pool_current)                #if lentokone_di["tyyppi"] == "Mamma Birgitta":

            tulos.append({
                "id": i + 1,
                "ident": pool_current[0],
                "name": pool_current[1],
                "type": pool_current[2],
                "iso_country": pool_current[3],
                "lat": pool_current[4],
                "long": pool_current[5],})
        except IndexError as ie:
            # Jos kenttiä ei ole riittävästi palautetaan False
            if i + 1 == valvara:
                return False
            else:
                # Kumminkin jos kenttiä on tarpeeksi, mutta ei valinnanvaran
                # verran, palautetaan vajaa lista. Näin valinnanvarasta ei
                # tule debuffia.
                pass
            
    return tulos


def eu_map_marked(long, lat, targets = None): 
    ### Tämä funktio ottaa longitude ja latitude arvot siinä järjestyksessä
    ### ja palauttaa kartan merkkijonon muodossa, jossa punainen X
    ### longitude ja latitude arvojen ylimalkaisessa sijainnissa


    ### Kartta:
    map_str= flight_art.Map.str

    # Kartan leveys ja korkeus merkkeinä 
    map_width = 58
    map_height = 29

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
    min_longitude = -12
    max_longitude = 55
    # Latitude
    min_latitude = 35
    max_latitude = 75.4

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
    
    # Targets
    target_id = 0
    if targets != None:
        for target in targets:
            target_id += 1

            # Normalisointi
            pixel_position_x = int((target[1] - min_longitude) / 
                    (max_longitude - min_longitude) * map_width)
            pixel_position_y = int((target[0] - min_latitude) / 
                    (max_latitude - min_latitude) * map_height)
            
            # Merkkaaminen
            index = map_height
            for i in range(len(updated_map_str)):
                if pixel_position_x <= len(updated_map_str[i]):
                    updated_line = list(updated_map_str[i])
                    if index==pixel_position_y:
                        updated_line[pixel_position_x] = str(target_id)
                    updated_map_str[i] = "".join(updated_line)
                else:
                    updated_map_str[i] = updated_line
                index -= 1

    # Väritetään X:t ja nro:t
    for line in range(len(updated_map_str)):
        updated_line = list(updated_map_str[line])
        for column in range(len(updated_line)):
            if updated_line[column] == "X":
                # Väritetään X
                updated_line[column] = (f"{Color.fg.blue}"
                f"X{Color.reset}")
                updated_map_str[line] = "".join(updated_line)
            elif updated_line[column] in "123456789":
                # Värotetään numerot
                updated_line[column] = (f"{Color.fg.black}"
                f"{Color.bg.blue}{updated_line[column]}{Color.reset}")
                updated_map_str[line] = "".join(updated_line)
    
    # Palautetaan X:llä merkitty kartta
    tulos = str()
    for i in range(len(updated_map_str)):            
        tulos += updated_map_str[i] + "\n"
    return tulos


#Päivitykset, kesken!!!!!
def upgrade_airplane(raha, valinta, lentokone_di):
    if valinta == "1" and raha >= 200000:
            if lentokone_di["tyyppi"] != "Stor Dam 23":
                paivitys = {
                    "tyyppi": "Stor Dam 23", 
                    "kantama": 600, 
                    "kerroin": 1.4, 
                    "hinta": 200000,
                    "valinnanvara" : 6}
                vahennys = raha - paivitys["hinta"]
                return paivitys, vahennys
    elif valinta == "2" and raha >= 1000000:
            if lentokone_di["tyyppi"] != "Nanny 24":
                paivitys = {
                    "tyyppi": "Nanny 24", 
                    "kantama": 1400, 
                    "kerroin": 1.6, 
                    "hinta": 1000000,
                    "valinnanvara" : 7}
                vahennys = raha - paivitys["hinta"]
                return paivitys, vahennys
    elif valinta == "3" and raha >= 1500000:
            if lentokone_di["tyyppi"] != "Mamma Birgitta 25":
                paivitys = {
                    "tyyppi": "Mamma Birgitta 25", 
                    "kantama": 2000, 
                    "kerroin": 2, 
                    "hinta": 1500000,
                    "valinnanvara" : 8}
                vahennys = raha - paivitys["hinta"]
                return paivitys, vahennys
    elif valinta in "123" and len(valinta) == 1:
        print("raha ei riitä")
        input("")

    return None


#random eventti
# [0] :  merkkijono kuvaa tapahtuman
# [1] :  päivitetty rahan arvo
def random_event(raha):
    if random.random() < 0.9:
        random_juttu = random.randint(0, 1)
        if random_juttu == 0:
            # MENETYS
            vahennys = random.uniform(3000, 16000)
            raha -= vahennys

            tulos_str = f"""{Color.fg.red}{flight_art.Money.euro}{Color.reset}

    {Color.bg.red}Voi ei!{Color.reset}
    Laskeutuessasi huomasit koneen vaativan välitöntä huoltoa.  
    kulut: {int(vahennys)}€\n"""

            return tulos_str, raha

        elif random_juttu == 1:
            # ANSIO
            bonus = random.uniform(1000,9000)
            raha += bonus

            tulos_str = f"""{Color.fg.green}{flight_art.Money.euro}{Color.reset}

    {Color.bg.green}Onneksi olkoon!{Color.reset}
    Keikka osoittautui tuottoisemmaksi kuin oletit,
    tienasit ylimääräistä: {int(bonus)} €\n"""
            return tulos_str, raha

        elif random_juttu == "shady":
            kysy = input(" Haluatko ottaa epäilyttävän kuorman? (K/E): ").strip().lower()
            if kysy == "K":
                on_success = random.choice([True, False])
                if on_success:
                    palkkio = 20000
                    raha += palkkio

                    tulos_str = f"""   
                    
{Color.bg.yellow}Riskialtis lasti!{Color.reset}
 Otit riskialitsta lastia ja se kannatti tienasit: {palkkio} €\n"""
                    return tulos_str, raha
    else:
        return None

# Tyhjentää ammount määrän rivejä terminaalista
def clear(ammount = 200):
    for _ in range(ammount):
        sys.stdout.write("\x1b[1A\x1b[2K")

def animaatio():
    print("\n                      ----- Matkalla -----")
    animaatio_str = flight_art.Animation.list

    for i in range(13):
        print(animaatio_str[i % len(animaatio_str)])
        clear(26)
        sleep(0.08)
    clear(28)

def reward(country, ident, etaisyys, visited_ident, base_reward, lentokone_di):
    etaisyys_raha = etaisyys * 2
    bonus = 0
    country_reward = 1

    match country:
        case "RU" | "BY":
            country_reward = 0.75
        case "FI" | "PL" | "EE" | "HR" | "GR":
            country_reward = 0.95
        case "SE" | "NO" | "DK" | "FR" | "CH" | "SP":
            country_reward = 1.1
        case "GB" | "IT" | "AT":
            country_reward = 1.05
        case "DE" | "LU":
            country_reward = 1.2

    if ident in visited_ident:
        base_reward = base_reward / 2

    return ((base_reward * float(lentokone_di["kerroin"])) + etaisyys_raha) * random.uniform(0.9,1.1) * country_reward