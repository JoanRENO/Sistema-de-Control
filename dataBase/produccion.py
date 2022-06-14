from .connection import DataBase
from .helpers import fecha
import re


class Produccion(DataBase):
    def consultarEstadoTurno(self, maquina):
        self.cursor.execute("SELECT maquina FROM " + DataBase.Tablas.turnos + " WHERE maquina LIKE '"
                            + maquina + "-TURNO-%'")
        row = self.cursor.fetchone()
        self.close()
        estados = re.split("-", row[0])
        print(estados[2])
        return estados[2]

    def cambiarEstadoTurno(self, maquina, legajos):
        if Produccion().consultarEstadoTurno(maquina) == "0":
            estado = "1"
            aux = ""
            for legajo in legajos:
                us = Produccion().getUsuario(legajo)
                aux += us + ", "
            print(aux)
            self.cursor.execute("INSERT INTO " + DataBase.Tablas.turnos + " (maquina, fechaInicio, usuario) VALUES (?,?,?)",
                                maquina, fecha(), aux)
            self.cursor.commit()
            idTurno = Produccion().getIdTurno(maquina)
            print(idTurno)
            for legajo in legajos:
                usuario = Produccion().getUsuario(legajo)
                self.cursor.execute("INSERT INTO " + DataBase.Tablas.turnos_usuarios + " (idTurno, idUsuario, nombreUsuario) "
                                    "VALUES (?, ?, ?)", idTurno, legajo, usuario)
            self.cursor.commit()
            print("AAAAAAAAA: " + str(idTurno))
            self.cursor.execute("SELECT fechaInicio FROM " + DataBase.Tablas.turnos + " WHERE idTurno = ?", idTurno)
            fechaTurno = self.cursor.fetchone()[0]
            print("BBBBBBBBB: " + str(fechaTurno))
            self.cursor.execute("INSERT INTO " + DataBase.Tablas.tareas + "(idTurno, fechaInicio, maquina) VALUES "
                                " (?,?,?)", idTurno, fechaTurno, maquina)
            self.cursor.commit()
        else:
            estado = "0"
            date = fecha()
            idTurno = Produccion().getIdTurno(maquina)
            self.cursor.execute("UPDATE " + DataBase.Tablas.turnos + " SET fechaFin = ? WHERE idTurno = ?", date,
                                Produccion().getIdTurno(maquina))
            self.cursor.execute("DELETE FROM " + DataBase.Tablas.tareas + " WHERE idTarea = "
                                "(SELECT MAX(idTarea) FROM " + DataBase.Tablas.tareas + " WHERE idTurno = ?) ", idTurno)
        self.cursor.execute("UPDATE " + DataBase.Tablas.turnos + " SET maquina = '" + maquina + "-TURNO-" + estado + "' WHERE "
                            "maquina LIKE '" + maquina + "-TURNO-%'")
        self.cursor.commit()
        self.close()


    def iniciarTarea(self, maquina, turno):
        #self.cursor.execute("INSERT INTO " + DataBase.Tablas.tareas + " (idTurno, fechaInicio, op, maquina) VALUES "
                            #"(?, ?, ?, ?)", turno, fecha(), op, maquina)
        #self.cursor.commit()
        self.cursor.execute("SELECT MAX(fechaFin) FROM " + DataBase.Tablas.tareas + " WHERE idTurno = ?", turno)
        date = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.tareas + " (maquina, fechaInicio, idTurno) VALUES (?,?, ?)",
                            maquina, date, turno)
        self.cursor.commit()
        self.close()

    def updateTarea(self, maquina, turno, op):
        idTarea = Produccion().getIdTarea(maquina, turno)
        self.cursor.execute("UPDATE " + DataBase.Tablas.tareas + " SET op = ? WHERE idTurno = ? AND idTarea = ?"
                            , op, turno, idTarea)
        self.cursor.commit()
        self.close()

    def finalizarTarea(self, maquina, descripcion, cantidad, reproceso):
        turno = Produccion().getIdTurno(maquina)
        tarea = Produccion().getIdTarea(maquina, turno)
        if reproceso is None:
            reproceso = "NO"
        #self.cursor.execute("SELECT CASE WHEN (COUNT(idTarea)) > 1 THEN 1 ELSE 0  FROM " + DataBase.Tablas.tareas + " "
        #                    "WHERE idTurno = ?", turno)
        #aux = self.cursor.fetchone()[0]
        #if aux == 0:
        self.cursor.execute(
            "UPDATE " + DataBase.Tablas.tareas + " SET fechaFin = ? , descripcion = ? , cantidad = ?, reproceso = ? "
            "WHERE idTurno = ? AND idTarea = ?", fecha(), descripcion, cantidad, reproceso,
            turno, tarea)
        self.cursor.commit()
        self.close()

    def iniciarParada(self, maq):
        idTurno = Produccion().getIdTurno(maq)
        idTarea = Produccion().getIdTarea(maq, idTurno)
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.paradas + " (idTarea, idTurno, fechaInicio, maquina)"
                            " VALUES (?,?,?,?)", idTarea, idTurno, fecha(), maq)
        self.cursor.commit()
        self.close()

    def finalizarParada(self, maq, observacion):
        idTurno = Produccion().getIdTurno(maq)
        idTarea = Produccion().getIdTarea(maq, idTurno)
        idParada = Produccion().getIdParada(maq, idTurno, idTarea)
        self.cursor.execute("UPDATE " + DataBase.Tablas.paradas + " SET fechafin = ?, observaciones = ? "
                            "WHERE idTurno = ? AND idTarea = ? AND idParada = ?"
                            , fecha(), observacion, idTurno, idTarea, idParada)
        self.cursor.commit()
        self.close()


##################################### GET #######################################
    def getIdTurno(self, maquina):
        self.cursor.execute("SELECT MAX(idTurno) FROM " + DataBase.Tablas.turnos + " WHERE maquina = ?", maquina)
        idTurno = self.cursor.fetchone()[0]
        return idTurno

    def getIdTarea(self, maquina, turno):
        print(maquina + " + " + str(turno))
        self.cursor.execute("SELECT MAX(idTarea) FROM " + DataBase.Tablas.tareas + " WHERE maquina = ? AND idTurno = ? "
                            , maquina, turno)
        idTarea = self.cursor.fetchone()[0]
        return idTarea

    def getIdParada(self, maquina, turno, tarea):
        self.cursor.execute("SELECT MAX(idParada) FROM " + DataBase.Tablas.paradas + " WHERE maquina = ? AND idTurno = ? "
                            "AND idTarea = ?"
                            , maquina, turno, tarea)
        idTurno = self.cursor.fetchone()[0]
        return idTurno

    def getOP(self, maquina):
        idTurno = Produccion().getIdTurno(maquina)
        idTarea = Produccion().getIdTarea(maquina, idTurno)
        print(idTurno, " + ", idTarea)
        self.cursor.execute("SELECT op FROM " + DataBase.Tablas.tareas + " WHERE idTarea = ? AND idTurno = ? "
                            , idTarea, idTurno)
        op = self.cursor.fetchone()[0]
        return op

    def getOPanterior(self, maquina):
        idTurno = Produccion().getIdTurno(maquina)
        idTarea = Produccion().getIdTarea(maquina, idTurno)
        print(idTurno, " + ", idTarea)
        self.cursor.execute("SELECT MAX(idTarea) FROM " + DataBase.Tablas.tareas + " WHERE idTarea < ? "
                            " AND idTurno = ?", idTarea, idTurno)
        idTarea = self.cursor.fetchone()[0]
        print("AAAA: " + str(idTarea))
        self.cursor.execute("SELECT op FROM " + DataBase.Tablas.tareas + " WHERE idTarea = ? AND idTurno = ? "
                            , idTarea, idTurno)
        op = self.cursor.fetchone()[0]
        return op

    def getListaOp(self, maquina):
        self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.basePiezas +
                            " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' ")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getPiezas(self, maquina, op):
        if maquina == 'SLC' or maquina == 'GBN1' or maquina == 'NST':
            self.cursor.execute("SELECT DISTINCT PIEZA_NOMBRECOLOR as PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas + " WHERE OP = ? AND"
                                " RUTA_ASIGNADA LIKE '%" + maquina + "%'", op)
        else:
            self.cursor.execute("SELECT DISTINCT PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas + " WHERE OP = ? AND"
                                " RUTA_ASIGNADA LIKE '%" + maquina + "%'", op)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getUsuario(self, legajo):
        self.cursor.execute("SELECT usuario FROM " + DataBase.Tablas.tablaUsuarios + " WHERE PIN = ?", legajo)
        leg = self.cursor.fetchone()[0]
        self.cursor.close()
        return leg

    def getCantidad(self, op, pieza, maq, espesor):
        if maq == "SLC" or maq == "GBN1" or maq == "NST":
             self.cursor.execute("SELECT COUNT(idPieza) FROM " + DataBase.Tablas.basePiezas + " WHERE OP = ? AND "
                                 "PIEZA_NOMBRECOLOR = ? AND RUTA_ASIGNADA LIKE '%" + maq + "%'"
                                 " AND PIEZA_PROFUNDO = ?", op, pieza, espesor)
        else:
            self.cursor.execute("SELECT COUNT(idPieza) FROM " + DataBase.Tablas.basePiezas + " WHERE OP = ? AND "
                                "PIEZA_DESCRIPCION = ? AND RUTA_ASIGNADA LIKE '%" + maq + "%'", op, pieza)
        cantidad = self.cursor.fetchone()[0]
        return cantidad

    def getEspesores(self, op, pieza, maq):
        self.cursor.execute("SELECT DISTINCT PIEZA_PROFUNDO FROM " + DataBase.Tablas.basePiezas + " WHERE OP = ? AND "
                            "PIEZA_NOMBRECOLOR = ? AND RUTA_ASIGNADA LIKE '%" + maq + "%'", op, pieza)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def consultarProceso(self, maquina):
        idTurno = Produccion().getIdTurno(maquina)
        idTarea = Produccion().getIdTarea(maquina, idTurno)
        self.cursor.execute("SELECT fechaFin FROM " + DataBase.Tablas.paradas + " WHERE idParada = "
                            "(SELECT MAX(idParada) FROM " + DataBase.Tablas.paradas + " WHERE idTurno = ? AND idTarea = ?)"
                            , idTurno, idTarea)
        aux1 = self.cursor.fetchone()
        print(aux1)
        if (aux1 is None) or (aux1[0] is not None):
            self.cursor.execute("SELECT fechaFin FROM " + DataBase.Tablas.tareas + " WHERE idTurno = ? AND idTarea = ?",
                                idTurno, idTarea)
            aux2 = self.cursor.fetchone()
            print(aux2)
            if (aux2 is None) or (aux2[0] is not None):
                pass
            else:
                return "1"
        else:
            return "2"

    def listaInforme(self, idTurno):
        self.cursor.execute("""
            (SELECT CONVERT(smalldatetime, [fechaInicio]) as Fecha
                  ,'INICIO DE TURNO' as OP
                  ,usuario as Descripcion
                  ,null as Cantidad
              FROM """ + DataBase.Tablas.turnos + """
               WHERE idTurno = ?
            UNION ALL
            SELECT 
                  CONVERT(smalldatetime, [fechaFin]) as Fecha
                  ,[op] as OP
                  ,[descripcion] as Descripcion
                  ,[cantidad] as Cantidad
              FROM """ + DataBase.Tablas.tareas + """
               WHERE idTurno = ? AND fechaFin IS NOT NULL
            UNION ALL
            SELECT 
                  CONVERT(smalldatetime, [fechaInicio]) as Fecha
                  ,CONCAT('PARADA: ', DATEDIFF(minute, fechaInicio, [fechaFin]), ' Minutos') as OP
                  ,[observaciones] as Descripcion
                  ,null as Cantidad
              FROM """ + DataBase.Tablas.paradas + """
              WHERE idTurno = ? AND fechaFin IS NOT NULL)
              ORDER BY Fecha
        """, idTurno, idTurno, idTurno)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def contarTareas(self, maq):
        idTurno = Produccion().getIdTurno(maq)
        self.cursor.execute("SELECT COUNT(idTarea) FROM " + DataBase.Tablas.tareas + " WHERE idTurno = ?", idTurno)
        cant = self.cursor.fetchone()[0]
        self.close()
        return cant
