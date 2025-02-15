# LENTOPELI
import mysql.connector

    yhteys = mysql.connector.connect (
        host='127.0.0.1',
        port= 3306,
        database='flight_game',
        user='pythonuser',
        password='salainen-sana',
        autocommit=True,
        collation='utf8mb3_general_ci'
        )

def main():
    #main


main()