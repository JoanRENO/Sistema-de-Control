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
        return estados[2]

    def verificarIdTurno(self, maquina, idTurno):
        self.cursor.execute("SELECT idTurno FROM " + DataBase.Tablas.turnos + " WHERE maquina = ? AND idTurno = ?",
                            maquina, idTurno)
        if self.cursor.fetchone() is None:
            return 0
        else:
            return 1

    def cambiarEstadoTurno(self, maquina, legajos):
        if Produccion().consultarEstadoTurno(maquina) == "0":
            estado = "1"
            aux = ""
            for legajo in legajos:
                us = Produccion().getUsuario(legajo)
                aux += us + ", "
            idTurno = Produccion().getIdTurno()
            if Produccion().verificarIdTurno(maquina, idTurno) == 0:
                self.cursor.execute("INSERT INTO " + DataBase.Tablas.turnos + " (idTurno, maquina, fechaInicio, usuario) VALUES (?,?,?,?)",
                                    idTurno, maquina, fecha(), aux)
                self.cursor.commit()
                for legajo in legajos:
                    usuario = Produccion().getUsuario(legajo)
                    self.cursor.execute("INSERT INTO " + DataBase.Tablas.turnos_usuarios + " (idTurno, idUsuario, nombreUsuario, maquina) "
                                        "VALUES (?, ?, ?, ?)", idTurno, legajo, usuario, maquina)
                self.cursor.commit()
        else:
            estado = "0"
            date = fecha()
            idTurno = Produccion().getIdTurno()
            self.cursor.execute("UPDATE " + DataBase.Tablas.turnos + " SET fechaFin = ? WHERE idTurno = ? AND maquina = ?"
                                , date, idTurno, maquina)
        self.cursor.execute("UPDATE " + DataBase.Tablas.turnos + " SET maquina = '" + maquina + "-TURNO-" + estado + "' WHERE "
                            "maquina LIKE '" + maquina + "-TURNO-%'")
        self.cursor.commit()
        self.close()

    def iniciarParada(self, maquina):
        idTurno = Produccion().getIdTurno()
        idParada = Produccion().getIdParada(maquina, idTurno)
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.paradas + " (idParada, idTurno, fechaInicio, maquina)"
                            " VALUES (?,?,?,?)", idParada, idTurno, fecha(), maquina)
        self.cursor.commit()
        self.close()

    def finalizarParada(self, maquina, observacion):
        idTurno = Produccion().getIdTurno()
        idParada = Produccion().getIdParada(maquina, idTurno)
        self.cursor.execute("UPDATE " + DataBase.Tablas.paradas + " SET fechafin = ?, observacion = ? "
                            "WHERE idTurno = ? AND maquina = ? AND idParada = ?-1"
                            , fecha(), observacion, idTurno, maquina, idParada)
        self.cursor.commit()
        self.close()


##################################### GET #######################################
    def getIdTurno(self):
        self.cursor.execute("""
                SELECT [idTurno]
                FROM [dbo].[baseTurnos]
                WHERE GETDATE() > fechaInicio AND GETDATE() < fechaFin
        """)
        idTurno = self.cursor.fetchone()[0]
        return idTurno

    def getIdParada(self, maquina, turno):
        self.cursor.execute("SELECT MAX(idParada) FROM " + DataBase.Tablas.paradas + " WHERE maquina = ? AND idTurno = ?"
                            , maquina, turno)
        aux = self.cursor.fetchone()
        if aux is None or aux[0] is None:
            idTurno = 1
        else:
            idTurno = aux[0] + 1
        return idTurno

    def getUsuario(self, legajo):
        self.cursor.execute("SELECT usuario FROM " + DataBase.Tablas.tablaUsuarios + " WHERE PIN = ?", legajo)
        leg = self.cursor.fetchone()[0]
        self.cursor.close()
        return leg

    def consultarProceso(self, maquina):
        idTurno = Produccion().getIdTurno()
        self.cursor.execute("SELECT fechaFin FROM " + DataBase.Tablas.paradas +
                            " WHERE idTurno = ? AND maquina = ? AND idParada = "
                            "(SELECT MAX(idParada) FROM " + DataBase.Tablas.paradas + " WHERE idTurno = ? AND maquina = ?)"
                            , idTurno, maquina, idTurno, maquina)
        aux1 = self.cursor.fetchone()
        print("PARADA: " + str(aux1))
        if (aux1 is None) or (aux1[0] is not None):
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
