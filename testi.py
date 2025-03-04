import mysql.connector

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

raha = {"euroa": 10000000000}

#Lentokoneen lähtötiedot
lentokone_di = {"tyyppi": "Lilla Damen 22", "kantama": 300, "kerroin": 1, "hinta": 200000}


def testi():
    print("Haluatko päivittää lentokonetta tai sen osia K/E?")
    paivitys = input(">")
    if paivitys.upper() == "K":
        print("Koneet ja niiden ominaisuudet.")
        koneet = f"""x-------------------------------------------------------------------------------------------x
|   1. Kone = Tyyppi: Stor Dam 23 / Kantama: 600 / Kerroin: 1.4 / hinta: 200000 €         |
|   2. Kone = Tyyppi: Nanny 24 / Kantama: 1400 / Kerroin: 1.6 / hinta: 1000000 €           |
|   3. Kone = Tyyppi: Mamma Birgitta 25 / Kantama: 2000 / kerroin: 2.0 / hinta: 500000000 €  |
x--------------------------------------------------------------------------------------------x"""
        print(koneet)
        print(f'Sinulla on rahaa {str(raha["euroa"])} €')
        print("Valitse haluamasi päivitys numerolla.")
        valinta = input(">>>")
        tehty = "Päivitys onnistui"

        # Päivittää Stor Dam 23
        if valinta == "1":
            if lentokone_di["tyyppi"] == "Nanny 24":
                print("Sinulla on jo tämä kone!")
            else:
                vaihtoehto = 2
                airplain_upgrade(vaihtoehto)
                print(tehty)
        elif valinta == "2":
            if lentokone_di["tyyppi"] == "Nanny 24":
                print("Sinulla on jo tämä kone!")
            else:
                vaihtoehto = 3
                airplain_upgrade(vaihtoehto)
                print(tehty)
        elif valinta == "3":
            if lentokone_di["tyyppi"] == "Nanny 24":
                print("Sinulla on jo tämä kone!")
            else:
                vaihtoehto = 4
                airplain_upgrade(vaihtoehto)
                print(tehty)
        else:
            print("ei tulosta")
    return None

def airplain_upgrade(vaihtoehto):
    sql = f"SELECT type, distance, factor, price FROM airplain WHERE id = '{vaihtoehto}'"
    kursori.execute(sql)
    tulos = kursori.fetchall()

    for tiedot in tulos:
        lentokone_di.update({"tyyppi": tiedot[0], "kantama": tiedot[1], "kerroin": tiedot[2], "hinta": tiedot[3]})
        raha.update({"euroa": float(raha["euroa"]) - float(tiedot[3])})
        return tiedot[0], tiedot[1], tiedot[2], tiedot[3]

print(lentokone_di)
testi()
print(lentokone_di)
print(f'Rahaa on jäljellä {raha["euroa"]} €')