# LENTOPELI
import mysql.connector
from geopy import distance
import random

yhteys = mysql.connector.connect (
    host='127.0.0.1',
    port= 3306,
    database='rahtipeli',
    user='pythonuser',
    password='salainen-sana',
    autocommit=True,
    collation='utf8mb3_general_ci'
    )
kursori = yhteys.cursor()

def main(): # MAIN FUNKTIO
    sijainti = "EFHK"
    find_ports(sijainti)

def find_ports(sij):
    # Tän funktion kuuluis palauttaa lista mahdollisista
    # matkustuskohteista. Position argumentti on tämänhetkinen
    # sijainti.

    # Ekaks lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()


    sql = f"SELECT ident, name, latitude_deg, longitude_deg, type FROM airport"
    kursori.execute(sql)
    airports = kursori.fetchall()
    # Tässä for loop käy jokaikisen lentokentän euroopassa
    # läpi ja laskee jokaisen kohdalla etäisyyden :DDD
    pool = []
    for airport in airports:
        paamaara_deg = (airport[2], airport[3])
        if (distance.distance(sij_deg, paamaara_deg).km < 200 and 
        airport[4] != "small_airport" and airport[0] != sij):
            pool.append(airport)
    for i in range(3): # Vielä pitää karsia mahdollinen toistuvuus
        print(pool[random.randrange(0, len(pool))])
        # voi olla että sama lentokenttä ilmenee kahdesti (tai kolmesti)


main()