from .connection import DataBase


class Informe(DataBase):
    def piezas_noleidas(self, maquina, op):
        print(op)
        if op == '':
            self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                                "FROM " + DataBase.Tablas.tableroBase + maquina)
            data = self.cursor.fetchall()
            self.close()
            return data
        self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                            "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP LIKE '" + op + "%'")
        data = self.cursor.fetchall()
        self.close()
        return data

    def lista_ops(self, maquina):
        if maquina in ["PLTER", "HORNO", "PLACARD", "PEGADO", "AGUJEREADO"]:
            return []
        self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE OP NOT LIKE '%STD%'")
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


