import mysql.connector 

railway_db_config = {
    "host": "monorail.proxy.rlwy.net",
    "port": 48959,
    "user": "root",
    "password": "dAC5a1bbDfAFef-FGbfDfFHbhfg3Ge45",
    "database": "railway"
}

try:
    conn = mysql.connector.connect(**railway_db_config)
    print("Success")
except mysql.connector.Error as e:
    print(e)
else:
    cursor = conn.cursor()