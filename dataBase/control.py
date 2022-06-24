from .connection import DataBase
from .helpers import fecha


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
