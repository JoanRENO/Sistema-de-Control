from .connection import DataBase
from .helpers import fecha
import requests
from flask import url_for

class Control(DataBase):
    def getTabla(self, maquina):
        hoy = fecha().date()
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "SELECT TOP 8 idOrdenManufactura, PT_PRODUCTO FROM " + DataBase.Tablas.baseModulos + \
                       " where CONVERT (DATE, fechaLecturaHORNO) = ? ORDER BY fechaLecturaHorno DESC"
        else:
            complete = "SELECT TOP 8 idPieza, PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas + \
                       " where CONVERT (DATE, fechaLectura" + maquina + ") = ? ORDER BY fechaLectura" + maquina + " DESC"
        self.cursor.execute(complete, hoy)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def verificar_cod(self, codigo, maquina):
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "SELECT (CASE WHEN lecturahorno >= 1 THEN 1 ELSE 0 END) as VER FROM " + DataBase.Tablas.baseModulos + \
                       " WHERE idOrdenManufactura=?"
        elif maquina == "AGUJEREADO" or maquina == "PEGADO" or maquina == "PLACARD":
            complete = "SELECT (CASE WHEN lectura" + maquina + " >= 1 THEN 1 ELSE 0 END) FROM " + DataBase.Tablas.basePiezas + \
                        " WHERE idPieza=?"
        else:
            complete = "SELECT (CASE WHEN lectura" + maquina + " >= 1 THEN 1 ELSE 0 END) FROM  " + DataBase.Tablas.basePiezas + \
                        " WHERE idPieza=? AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
        self.cursor.execute(complete, codigo)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
        return data

    def updatePM(self, codigo, maquina):
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "UPDATE " + DataBase.Tablas.baseModulos + " SET fechaLecturaHorno = ?, lecturaHorno = 1 " \
                       "WHERE idOrdenManufactura = ?"
        else:
            complete = "UPDATE " + DataBase.Tablas.basePiezas + " SET fechaLectura" + maquina + " = ?, lectura" + maquina + " = 1 " \
                        "WHERE idPieza = ?"
        self.cursor.execute(complete, fecha(), codigo)
        self.cursor.commit()
        self.close()

    def putQtyProduced(self, om, idOM):
        self.cursor.execute("SELECT COUNT(idModulo) FROM " + DataBase.Tablas.baseModulos +
                            " WHERE ORDEN_MANUFACTURA = ? AND lecturaHorno >= 1", om)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]

        headers = {'Content-type': 'application/json', 'Accept': 'application/json',
                   'Authorization': 'Basic e7d942c4-5bc4-4529-b24a-8d0b6bc01da5'}

        username = "batch"
        password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"

        contents = '{"x_pqty": ' + str(data) + ' ,"x_estado": "a_procesar"}'
        bytes(contents, encoding="utf-8")
        print(contents)

        url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production/' + str(idOM)
        response = requests.put(url, auth=(username, password), data=contents, headers=headers)

        # Imprime los resultados
        status = response.status_code

        responseGet = requests.get(url, auth=(username, password))

        getStatus = str(status) + str(responseGet.json())

        Control().logOdoo(idOM, om, status, getStatus)
        return str(status)

    #def verificarComplete(self, om):
    #    print("PASO 2")
    #    self.cursor.execute(
    #        "SELECT CASE WHEN COUNT(idModulo) = SUM(CASE WHEN lecturaHorno >= 1 THEN 1 ELSE 0 END) THEN 1 ELSE 0 END as VER FROM " + DataBase.Tablas.baseModulos +
    #        " WHERE ORDEN_MANUFACTURA = ?", om)
    #    data = self.cursor.fetchone()
    #    self.close()
    #    if data is not None:
    #        data = data[0]
    #    print(data)
    #    return data

    def getIdOdoo(self, om):
        print("PASO 3")
        username = "batch"
        password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"

        args = {"args": [[["name", "=", om]]]}
        url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production'
        print(url)

        response = requests.patch(url, auth=(username, password), json=args)

        # Imprime los resultados
        status = response.status_code

        getResult = response.json()
        idOdoo = getResult[0]['id']

        return status, idOdoo

    #def putOdoo(self, idOM):
    #    print("PASO 4")
    #    headers = {'Content-type': 'application/json', 'Accept': 'application/json',
    #               'Authorization': 'Basic e7d942c4-5bc4-4529-b24a-8d0b6bc01da5'}

    #    username = "batch"
    #    password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"


    #    contents = '{"x_estado": "a_procesar"}'
    #    bytes(contents, encoding="utf-8")
    #    print(contents)

    #    url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production/' + str(idOM)
    #    response = requests.put(url, auth=(username, password), data=contents, headers=headers)

        # Imprime los resultados
    #    status = response.status_code
    #    print(status)

    #    response = requests.get(url, auth=(username, password))

        # Imprime los resultados
    #    getStatus = str(response.status_code) + str(response.json())
    #    print(getStatus)
    #    return str(status), getStatus

    def logOdoo(self, idOM, OM, status, getStatus):
        self.cursor.execute("""
                                INSERT INTO [dbo].[logPUT]
                                        (idOM, fecha, OM, status, getResult)
                                    VALUES
                                        (?,?,?,?,?)
                            """, idOM, fecha(), OM, status, getStatus)
        self.cursor.commit()
        self.close()

    def getOM(self, idOM):
        print("PASO 1")
        self.cursor.execute(
            "SELECT ORDEN_MANUFACTURA FROM " + DataBase.Tablas.baseModulos + " WHERE idOrdenManufactura = ?", idOM)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
        print(data)
        return data
