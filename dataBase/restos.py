from .connection import DataBase
from .helpers import fecha
import re



class Resto(DataBase):
    def altaResto(self, color, medidas):
        medidas2 = re.split("x", medidas.lower())
        print(medidas2)
        alto = medidas2[0]
        ancho = medidas2[1]
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.restos + " ([alto], [ancho], [estado], [color]) VALUES "
                            "(?,?,?,?)", alto, ancho, 'NO ASIGNADO', color)
        self.cursor.commit()
        self.close()

    def bajaResto(self, color, medidas):
        medidas = re.split('x', medidas.lower())
        print(medidas)
        alto = medidas[0]
        ancho = medidas[1]
        self.cursor.execute("SELECT TOP 1 idResto FROM " + DataBase.Tablas.restos +
                            " WHERE color = ? AND alto = ? AND ancho = ? AND estado = 'NO ASIGNADO'", color, alto, ancho)
        idResto = self.cursor.fetchall()[0]
        self.cursor.execute("UPDATE " + DataBase.Tablas.restos +
                                " SET [estado] = 'ASIGNADO' "
                                "WHERE idResto = ?", idResto)
        self.cursor.commit()
        self.close()

    def listaColoresBAJA(self):
        self.cursor.execute("SELECT DISTINCT color FROM " + DataBase.Tablas.restos + " WHERE estado = 'NO ASIGNADO'")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def listaColoresALTA(self):
        self.cursor.execute("SELECT DISTINCT CONCAT(CONVERT(varchar, cod_selco), ' ' , color) AS color, cod_selco FROM "
                            + DataBase.Tablas.colores_selco)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def listaPiezas(self, color):
        self.cursor.execute("SELECT idResto, alto, ancho FROM " + DataBase.Tablas.restos +
                            " WHERE estado = 'NO ASIGNADO' AND color = ?", color)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def listaIdBAJA(self):
        self.cursor.execute("SELECT idResto, CONCAT(color, '', alto, 'X',ancho) as Descripcion FROM "
                            + DataBase.Tablas.restos + " WHERE estado = 'NO ASIGNADO'")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def bajaRestoId(self, idResto):
        self.cursor.execute("UPDATE " + DataBase.Tablas.restos +
                                " SET [estado] = 'ASIGNADO' "
                                "WHERE idResto = ?", idResto)
        self.cursor.commit()
        self.close()

    def verificarOP(self):
        self.cursor.execute("SELECT estado FROM " + DataBase.Tablas.restos + " WHERE idResto = 1")
        a = self.cursor.fetchone()
        print(a)
        if a[0] == 'ACTIVADO':
            self.cursor.execute("SELECT color FROM " + DataBase.Tablas.restos + " WHERE idResto = 1")
            a = self.cursor.fetchone()
            return a[0]
        else:
            return False

    def activarOP(self, estado, colores):
        aux = ''
        for color in colores:
            aux += color + ','
        aux = aux[:-1]
        print(aux)
        self.cursor.execute("UPDATE " + DataBase.Tablas.restos + " SET estado = ?, color = ? WHERE idResto = 1", estado, aux)
        self.cursor.commit()
        self.close()

    def obtenerColores(self, lista_colores):
        self.cursor.execute("SELECT CONCAT(CONVERT(varchar, cod_selco), ' ' , color) AS color FROM " + DataBase.Tablas.colores_selco + " WHERE"
                            " cod_selco IN (" + lista_colores + ")")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        lista = []
        for a in OutputArray:
            lista.append(a['color'])
        return lista

    def listaColoresBAJA_OP(self, lista_colores):
        aux = "'"
        for co in lista_colores:
            aux += co + "','"
        aux = aux[:-1]
        aux = aux[:-1]
        print(aux)
        self.cursor.execute("SELECT DISTINCT color FROM " + DataBase.Tablas.restos + " WHERE estado = 'NO ASIGNADO'"
                            " AND color NOT IN (" + aux + ")")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def desactivarOP(self, estado):
        self.cursor.execute("UPDATE " + DataBase.Tablas.restos + " SET estado = ?, color = null WHERE idResto = 1", estado)
        self.cursor.commit()
        self.close()
