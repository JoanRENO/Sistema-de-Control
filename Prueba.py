from datetime import datetime
from dataBase.helpers import fecha
import pyodbc

connection = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
				"Server=SERVER;"
				"DataBase=PRODUCCION_PLANTA;"
				"Trusted_Connection=yes;"
				"uid=sa;"
				"pwd=200sa;"
            )

today = datetime.now()
todaySTR = today.strftime("%Y-%m-%d %H:%M:%S")
todayDATE = datetime.strptime(todaySTR, '%Y-%m-%d %H:%M:%S')
print(todaySTR, type(todaySTR))
print(todayDATE, type(todayDATE))
print(fecha())

ids = 290206
cursor = connection.cursor()
cursor.execute("SELECT fechaLecturaHORNO FROM produccion.baseModulos555 WHERE "
                                       "idModulo = ? ", ids)
data = cursor.fetchone()
print(data)

your_timestamp = 44588.42885416667
print(type(your_timestamp))
print(datetime.fromtimestamp(your_timestamp).strftime('%Y-%m-%d %H:%M:%S'))
