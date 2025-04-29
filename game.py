# LENTO-/RAHTIPELI

import random
from geopy import distance
import mysql.connector

import flight_lib
import flight_art
from flight_art import Color

yhteys = mysql.connector.connect (
    host='127.0.0.1',
    port= 3306,
    database='flight_game',
    user='pythonuser',  # HUOM käyttäjä: pythonuser
    password='salainen-sana',  #HUOM salasana
    autocommit=True,
    collation='utf8mb3_general_ci'
    )
kursori = yhteys.cursor()
# python -X utf8 .\game.py

### Keskeiset muttujat:

# Tämänhetkinen sijainti
sijainti = {
    "ident": "EFHK", # Tämänhetkinen ICAO-koodi, lähtöpaikka
    "deg": (60.3172, 24.963301), # Tämänhetkiseen sijainnin lat, long
    "nimi": "Helsinki-Vantaa Airport"
}

# Rahan määrä käyttäjällä
raha = 2000
visited_ident = []
visited_country = []
# Lentokoneen lähtötiedot
lentokone_di = {
    "tyyppi": "Lilla Damen 22", 
    "kantama": 300, 
    "kerroin": 1, 
    "hinta": 0,
    "valinnanvara" : 4
    }

kantama = lentokone_di["kantama"]  # Määrittää miten kauas kone kulkee (km)
valinnanvara = lentokone_di["valinnanvara"]  # Määrittää miten monta kenttää tarjotaan per vuoro

vuorot = 30
player_nimi = "Rahtifirma"

# Pelin aloitus
flight_lib.clear()
print(flight_art.StartScreen.picture + "\n")
print(flight_art.StartScreen.title)


input(" paina [ENTER]")

print("""
 Tervetuloa rahtilento yrittäjäksi!
 Aloitat Helsinki-Vantaalta omalla rahtikoneellasi. Valitse reittisi,
 kuljeta lastia ja kasvata varallisuuttasi. Päivitä konettasi kantaman, 
 lastikapasiteetin ja tuottojen parantamiseksi. Muista, että aikasi on 
 rajallinen - tee fiksuja valintoja ja maksimoi voitot ennen pelin 
 päättymistä. 

 Oletko valmis nousemaan ilmaan?
 kirjoita help saadaksesi listan komennoista kun peli on alkanut
 """)
nimitys = input("Nimeä yrityksesi \n> ")
if len(nimitys.strip()) > 0:
    player_nimi = nimitys

suunta_valittu = False
event = False
animaatio = False

### Pelin "main" loop tässä
while vuorot > 0:
    # Näytön tyhjentäminen
    flight_lib.clear()
    
    # Animaatio
    if animaatio == True:
        flight_lib.animaatio()
    animaatio = False

    # Random eventit
    if event == True and suunta_valittu == False:
        event_outcome = flight_lib.random_event(raha)
        if event_outcome != None:
            print(event_outcome[0])
            input("Paina [ENTER]")
            print("")
            raha = event_outcome[1]
            flight_lib.clear()

    # "stats_prompt" näyttää pelaajalle hyödyllistä infoa.
    stats_prompt = f"""x----------------------------------------------x---------x
|   Raha:       {(str(int(raha))+" €").ljust(31)   }|    ^    |
|   Sijainti:   {sijainti["nimi"].ljust(31)[:31]   }|    N    |
|   Lentokone:  {lentokone_di["tyyppi"].ljust(31)  }|  W + E  |
|   Kantama:    {(str(kantama)+" km").ljust(31)    }|    S    |
x----------------------------------------------x---------x"""
    header_pompt = f"""x--------------------------------------------------------x
|  {player_nimi.ljust(30)}   Päiviä jäljellä: {str(vuorot).ljust(2)}  |
x--------------------------------------------------------x"""
    #Koneen päivitys kysely

    # Tässä kartta. huom: eu_map_marked(long, lat) ottaa long ja lat arvot
    # argumentteina ja palauttaa kartan merkijonona jossa punainen
    # X merkitsee long ja lat arvojen ylimalkaisen sijainnin
    jatkuu = False
    if suunta_valittu == False:
        print(header_pompt)
        print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
        print(stats_prompt)
        print("Valitse suunta [N/W/S/E]")
    else:
        # Kutsutaan liike_lista funktio, joka palauttaa mahdolliset keikat
        liike_lista = flight_lib.find_ports(sijainti["ident"],int(kantama),valinnanvara, suunta, lentokone_di)
        if liike_lista != False:
            liike_lista_str = ""
            target_lista = []
            # Liike_lista_str ensimmäiset rivit
            liike_lista_str = f" - Palkkio - ICAO --- Lentokentän nimi -----------------\n"
            for kentta in liike_lista:
                # kentta_stats tallennetaan musitiin uudelleenkäyttöä varten
                target_lista.append((kentta["lat"], kentta["long"]))

                if kentta["type"]=="medium_airport":
                    base_reward = 2000
                if kentta["type"]=="large_airport":
                    base_reward = 3500



                # Reward
                etaisyys = distance.distance(sijainti["deg"],(kentta["lat"],kentta["long"])).km

                kentta["reward"] = flight_lib.reward(kentta["iso_country"], kentta["ident"], etaisyys, visited_ident, base_reward, lentokone_di)

                # Liike_lista_str tallennetaan muistiin
                liike_lista_str += (f"{Color.fg.lightcyan}{kentta["id"]}{Color.reset} | "
                f"{Color.fg.green}{(str(int(kentta["reward"])) + "€").ljust(7)}{Color.reset}| {kentta["ident"].ljust(7)}|"
                f" {kentta["name"].ljust(30)[:30]} | {kentta["iso_country"]}\n") # etäisyys {(str(int(etaisyys))+"km").ljust(7)}|

            print(header_pompt)
            print(flight_lib.eu_map_marked(sijainti["deg"][1],sijainti["deg"][0],target_lista),end="")
            print(stats_prompt)
            print(liike_lista_str)
            print("Valitse keikka antamalla kohteen numero")
        else:
            print("Suunnassa ei riittävästi lentokenttiä.")
            input("Paina [ENTER]")
            suunta_valittu = False
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
            print("UPGRADE: Osta uusi lentokone.")

        #Komento jolla koneen päivitys onnistuu
        elif komento.upper() == "UPGRADE":
                flight_lib.clear()
                print("\nKoneet ja niiden ominaisuudet.")
                koneet = f"""x------------------------------------------------------------------------------------------x
|   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 450 / Kerroin: 1.4 / Hinta: 25 000 €          |
|   2. Kone = Tyyppi: Nanny 24 / Kantama: 650 / Kerroin: 1.6 / Hinta: 60 000 €             |
|   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 1500 / Kerroin: 2.0 / Hinta: 100 000 €  |
x------------------------------------------------------------------------------------------x"""
                print(koneet)
                print(f'Sinulla on rahaa {int(raha)} €')
                print("Valitse haluamasi päivitys numerolla [1 / 2 / 3].")
                valinta = input("> ")

                paivitys = flight_lib.upgrade_airplane_md(raha, valinta, lentokone_di)
                if paivitys != None:
                    lentokone_di, raha = paivitys[0], paivitys[1]
                    kantama = lentokone_di["kantama"]
                    valinnanvara = lentokone_di["valinnanvara"]

                event = False
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
            
            
            if suunta_valittu == True:
                print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0], target_lista), end="")
                print(stats_prompt)
                print(liike_lista_str)
                print("Valitse keikka antamalla kohteen numero")
            else:
                print(flight_lib.eu_map_marked(sijainti["deg"][1], sijainti["deg"][0]), end="")
                print(stats_prompt)
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
                    # Sijaiti lisätään visited-listaan
                    if sijainti["ident"] not in visited_ident:
                        visited_ident.append(sijainti["ident"])

                    if kentta["iso_country"] not in visited_country:
                        visited_country.append(kentta["iso_country"])

                    # Rahaan lisätään relevantti reward
                    raha += liike_lista[i]["reward"]

                    target_lista = None

                    # Bool arvot päivitetään
                    suunta_valittu = False
                    event = True
                    animaatio = True
                    vuorot -= 1
                    jatkuu = True

                    break
                elif i+1 == len(liike_lista):
                    # Jos lentokenttää ei löytynyt eikä komentoa tunnistettu
                    print("Komentoa ei tunnistettu, kirjoita help saadaksesi"
                    "listan komennoista.")

### Pelin lopetus
flight_lib.clear()
flight_lib.animaatio()
print(f"""
{Color.fg.yellow}Aika loppui!{Color.reset}

Koneesi arvo ajan loppuessa: {int(lentokone_di["hinta"])} €
Rahasi ajan loppuessa: {int(raha)}€

\nMyit koneesi ja sait siitä 80% lisää voittoihisi: {int(raha)+(int(lentokone_di["hinta"]))*0.8} €
Sijaintisi ajan loppuessa: {sijainti["nimi"]}
""")

input("")