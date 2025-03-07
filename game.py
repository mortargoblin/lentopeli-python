# LENTO-/RAHTIPELI

# Huom! funktiot tuolla
import flight_lib
from flight_lib import Color
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



#Rahan määrä käyttäjällä
raha = 3000000
visited_ident = []
visited_country = []
#Lentokoneen lähtötiedot
lentokone_di = {"tyyppi": "Lilla Damen 22", "kantama": 300, "kerroin": 1, "hinta": 2000000, "valinnanvara" : 5}

kantama = lentokone_di["kantama"]  # Määrittää miten kauas kone kulkee (km)
valinnanvara = 5  # Määrittää miten monta kenttää tarjotaan per vuoro

# Pelin aloitus
print(flight_lib.StartScreen.picture + "\n")
print(flight_lib.StartScreen.title)


print("Tässä pelin loredump, selitys, avaus, yms")
print("..........")
print("kirjoita help saadaksesi listan komennoista kun peli on alkanut")
input("paina [ENTER] jataaksesi")

suunta_valittu = False


### Pelin "main" loop tässä
while True: 
    # "stats_prompt" näyttää pelaajalle hyödyllistä infoa.
    stats_prompt = f"""x-----------------------------------------------------x---------x
|   Raha:       {(str(int(raha))+" €").ljust(38)     }|    ^    |
|   Sijainti:   {sijainti["nimi"].ljust(38)          }|    N    |
|   Lentokone:  {lentokone_di["tyyppi"].ljust(38)    }|  W + E  |
|   Kantama:    {(str(kantama)+" km").ljust(38)      }|    S    |
x-----------------------------------------------------x---------x"""
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
            # Liike_lista_str ensimmäiset rivit
            liike_lista_str = f"   Palkkio   ICAO      Lentokentän nimi      -= KEIKAT =-\n"
            for kentta in liike_lista:
                # kentta_stats tallennetaan musitiin uudelleenkäyttöä varten
                target_lista.append((kentta["lat"], kentta["long"]))
                if kentta["type"]=="medium_airport":
                    base_reward = 2000
                if kentta["type"]=="large_airport":
                    base_reward = 3500

                etaisyys = distance.distance(sijainti["deg"],(kentta["lat"],kentta["long"])).km
                etaisyys_raha = etaisyys * 2
                bonus = 0
                country_reward = 1
                match kentta["iso_country"]:
                    case "RU"|"BY":
                        country_reward = 0.75
                    case "FI"|"PL"|"EE"|"HR"|"GR":
                        country_reward = 0.95
                    case "SE"|"NO"|"DK"|"FR"|"CH"|"SP":
                        country_reward = 1.1
                    case "GB"|"IT"|"AT":
                        country_reward = 1.05
                    case "DE"|"LU":
                        country_reward = 1.2

                if kentta["ident"] in visited_ident:
                    base_reward = base_reward / 2
                else:
                    pass

                reward = ((base_reward * float(lentokone_di["kerroin"]))  + etaisyys_raha) * random.uniform(0.9,1.1) * country_reward
                kentta["reward"] = reward

                # Liike_lista_str tallennetaan muistiin
                liike_lista_str += (f"{Color.fg.lightcyan}{kentta["id"]}{Color.reset} | "
                f"{Color.fg.green}{(str(int(reward)) + "€").ljust(7)}{Color.reset}| {kentta["ident"].ljust(7)}|"
                f"  {kentta["name"]} - {int(etaisyys)}km - {kentta["iso_country"]}{"\n"}")

            print(flight_lib.eu_map_marked(sijainti["deg"][1],sijainti["deg"][0],target_lista),end="")
            print(stats_prompt)
            print(liike_lista_str)
            print("Valitse keikka antamalla kohteen numero")
        else:
            suunta_valittu = False
            print("Suunnassa ei riittävästi lentokenttiä.")
            input("Paina Enter jatkaaksesi")
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
            print("[Q]: Poistu")
            print("SHOW icao: näyttää haluamasi lentokentän sijainnin kartalla. Esim. EDDB")
            print("PROMPT: Näyttää kartan, statsit ja keikat uudestaan")
            print("UPGRADE: Pääset päivittämään konettasi.")

        #Komento jolla koneen päivitys onnistuu
        elif komento.upper() == "UPGRADE":
            print("Koneet ja niiden ominaisuudet.")
            koneet = f"""x----------------------------------------------------------------------------------------x
|   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 700 / Kerroin: 1.4 / Hinta: 600000 €        |
|   2. Kone = Tyyppi: Nanny 24 / Kantama: 1200 / Kerroin: 1.7 / Hinta: 1000000 €         |
|   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 1600 / kerroin: 2.0 Hinta: 1500000 €  |
x----------------------------------------------------------------------------------------x"""
            print(koneet)
            print(f'Sinulla on rahaa {int(raha)} €')
            print("Valitse haluamasi päivitys numerolla [1 / 2 / 3].")
            valinta = input(">>>")

            paivitys = flight_lib.upgrade_airplane(raha, valinta, lentokone_di)
            if paivitys == None:
                print("Riittämätön raha")
            else:
                lentokone_di, raha = paivitys[0], paivitys[1]
                kantama = lentokone_di["kantama"]
                valinnanvara = lentokone_di["valinnanvara"]
            jatkuu = True

        # Tässä show komento, joka näyttää lentokentän sijainnin kartalla
        elif komento_args[0].upper() == "SHOW":
            if len(komento_args) == 2:
                show_ident = komento_args[1]
                sql = f"SELECT longitude_deg, latitude_deg, name FROM airport WHERE ident='{show_ident}'"
                kursori.execute(sql)
                show_ident = kursori.fetchone()
                try:
                    print(flight_lib.eu_map_marked(show_ident[0], show_ident[1]))
                    print("Näytillä:",show_ident[2])
                except TypeError:
                    print("ICAO-koodilla ei löytynyt mitään")
            else: 
                print("Komento vaatii kaksi argumenttia. Esimerkiksi: show eddb")

        # Prompt-komento näyttää kartan ja statsit uudestaan
        elif komento.upper() == "PROMPT":
            print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0], target_lista), end="")
            print(stats_prompt)
            if suunta_valittu == True:
                print(liike_lista_str)
                print("Valitse keikka antamalla kohteen numero")
            else:
                print("Valitse suunta [N/W/S/E]")

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
                if komento.upper() == str(liike_lista[i]["id"]):
                    # Jos pätevä icao-koodi löytyy, sijainti päivitetään
                    sijainti = {
                        "ident": liike_lista[i]["ident"],
                        "deg": (liike_lista[i]["lat"], liike_lista[i]["long"]),
                        "nimi": liike_lista[i]["name"]
                    }
                    if sijainti["ident"] not in visited_ident:
                        visited_ident.append(sijainti["ident"])
                    else:
                        pass
                    if kentta["iso_country"] not in visited_country:
                        visited_country.append(kentta["iso_country"])
                    else:
                        pass
                    raha += liike_lista[i]["reward"]
                    suunta_valittu = False
                    jatkuu = True
                    target_lista = None
                    break
                elif i+1 == len(liike_lista):
                    # Jos lentokenttää ei löytynyt eikä komentoa tunnistettu
                    print("Väärä komento, kirjoita help saadaksesi ", end="")
                    print("listan komennoista")
