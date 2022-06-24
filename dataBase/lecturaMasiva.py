from .connection import DataBase
from .helpers import fecha


class LecturaMasiva(DataBase):
    def lista_ops(self, maquina):
        self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.basePiezas +
                            " WHERE (lectura" + maquina + " = 0 OR lectura" + maquina + " is null) "
                            "AND RUTA_ASIGNADA LIKE '%" + maquina + "%' ORDER BY OP")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_colores(self, op, maquina):
        self.cursor.execute("SELECT DISTINCT PIEZA_NOMBRECOLOR FROM " + DataBase.Tablas.basePiezas +
                            " WHERE OP = ? AND RUTA_ASIGNADA LIKE '%" + maquina + "%' AND "
                            "(lectura" + maquina + " = 0 OR lectura" + maquina + " is null) ORDER BY PIEZA_NOMBRECOLOR", op)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_espesores(self, color, op, maquina):
        self.cursor.execute("SELECT DISTINCT PIEZA_PROFUNDO FROM " + DataBase.Tablas.basePiezas +
                            " WHERE OP = '" + op + "' "
                            "AND PIEZA_NOMBRECOLOR = ? AND RUTA_ASIGNADA LIKE '%" + maquina + "%' "
                            " AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null) ORDER BY "
                            "PIEZA_PROFUNDO", color)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_piezas(self, op, color, espesor, maquina):
        self.cursor.execute("SELECT DISTINCT PIEZA_DESCRIPCION "
                            "FROM " + DataBase.Tablas.basePiezas +
                            " WHERE OP = '" + op + "' AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=? AND RUTA_ASIGNADA "
                            "LIKE '%" + maquina + "%' AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null) "
                            , color, espesor)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def calcular_cant(self, op, color, espesor, pieza, maquina):
        if pieza == 1:
            self.cursor.execute("SELECT COUNT(idPieza) as CANTIDAD FROM " + DataBase.Tablas.basePiezas + " WHERE OP = '" + op + "' "
                                "AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=? "
                                "AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
                                " AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null)", color, espesor)
        else:
            self.cursor.execute("SELECT COUNT(idPieza) as CANTIDAD FROM " + DataBase.Tablas.basePiezas + " WHERE OP = '" + op + "' "
                                 "AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=? AND PIEZA_DESCRIPCION=? "
                                "AND RUTA_ASIGNADA LIKE '%" + maquina + "%' "
                                "AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null)"
                                , color, espesor, pieza)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def verificar_lectura(self, op, color, espesor, pieza, maquina, cant):
        if pieza == '':
            complete = "SELECT idPieza FROM " + DataBase.Tablas.basePiezas + " WHERE OP = '" + op + "' " \
                       "AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=?" \
                       " AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null) " \
                        "AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
            self.cursor.execute(complete, color, espesor)
        else:
            complete = "SELECT TOP " + cant + " idPieza FROM " + DataBase.Tablas.basePiezas + " WHERE OP = '" + op + "' " \
                       "AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=? AND PIEZA_DESCRIPCION=?" \
                       " AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null)" \
                       " AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
            self.cursor.execute(complete, color, espesor, pieza)
        records = self.cursor.fetchall()
        if not records:
            self.close()
            return 1
        ids = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            ids.append(dict(zip(columnNames, record)))
        self.close()
        return ids

    def updateMasivo(self, ids, maquina):
        for id in ids:
            complete = 'UPDATE ' + DataBase.Tablas.basePiezas + ' SET fechaLectura' + maquina + ' = ?, lectura' \
                       + maquina + ' = 1 WHERE idPieza = ?'
            self.cursor.execute(complete, fecha(), id['idPieza'])
            self.cursor.commit()
        self.close()

    def verificar_pin(self, pin):
        self.cursor.execute("SELECT Usuario FROM " + DataBase.Tablas.tablaUsuarios + " WHERE PIN = ?", pin)
        usuario = self.cursor.fetchone()
        self.close()
        if usuario is None:
            return None
        else:
            return usuario[0]

    def log_lecturaMasiva(self, usuario, op, color, espesor, maquina, pieza, cant):
        if pieza is None:
            self.cursor.execute("SELECT COUNT(idPieza) as CANTIDAD FROM " + DataBase.Tablas.basePiezas + " WHERE OP = '" + op + "' "
                                "AND PIEZA_NOMBRECOLOR=? AND PIEZA_PROFUNDO=? AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
                                " AND (lectura" + maquina + " = 0 OR lectura" + maquina + " is null)",
                                color, espesor)
            records = self.cursor.fetchall()
            OutputArray = []
            columnNames = [column[0] for column in self.cursor.description]
            for record in records:
                OutputArray.append(dict(zip(columnNames, record)))
            cant = OutputArray[0]['CANTIDAD']
        print(cant)
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.logLecturaMasiva +
                            " (Usuario, fechaMod, OP, Color, Espesor, maquina, Pieza, Cantidad) "
                            "VALUES (?,?,?,?,?,?,?,?)", usuario, fecha(), op, color, espesor, maquina, pieza, cant)
        self.cursor.commit()
        self.close()

    def getTablaLecturaMasiva(self, maquina):
        self.cursor.execute("SELECT TOP 8 * FROM " + DataBase.Tablas.logLecturaMasiva + " WHERE maquina = ? "
                            "ORDER BY fechaMod DESC", maquina)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray
