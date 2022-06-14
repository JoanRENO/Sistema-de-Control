from .connection import DataBase


class Informe(DataBase):
    def piezas_noleidas(self, maquina, op, tipobusqueda):
        print(op)
        if tipobusqueda == "Contiene":
            self.cursor.execute("SELECT OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO, COUNT(idPieza) as Cantidad "
                                "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP LIKE '" + op + "%'"
                                "GROUP BY OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO")
        else:
            self.cursor.execute("SELECT OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO, COUNT(idPieza) as Cantidad "
                                "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP = ? "
                                "GROUP BY OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO", op)
        data = self.cursor.fetchall()
        self.close()
        return data

    def ids_noleidas(self, maquina, op, tipobusqueda):
        print(op)
        if tipobusqueda == "Contiene":
            self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                                "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP LIKE '" + op + "%'")
        else:
            self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                                "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP = ?", op)
        data = self.cursor.fetchall()
        self.close()
        return data

    def lista_ops(self, maquina, tipobusqueda):
        if maquina in ["PLTER", "HORNO", "PLACARD", "PEGADO", "AGUJEREADO"]:
            return []
        if tipobusqueda == "Contiene":
            self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP NOT LIKE '%STD%'")
        else:
            self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.tableroBase + maquina)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        lista = []
        for op in OutputArray:
            lista.append(op['OP'])
        return lista

