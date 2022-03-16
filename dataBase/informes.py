from .connection import DataBase


class Informe(DataBase):
    def piezas_noleidas(self, maquina, op):
        print(op)
        if op == '':
            self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                                "FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE lectura = 0")
            data = self.cursor.fetchall()
            self.close()
            return data
        self.cursor.execute("SELECT idPieza, OP, PIEZA_DESCRIPCION, RUTA_ASIGNADA, PIEZA_CODIGO "
                            "FROM " + DataBase.Tablas.tableroBase + maquina +
                            " WHERE lectura = 0 AND OP = ?", op)
        data = self.cursor.fetchall()
        self.close()
        return data

    def lista_ops(self, maquina):
        if maquina in ["FAB", "NST", "GBM", "CHN", "LEA", "ALU", "INSUMOS", "PLTER", "HORNO", "PLACARD", "PEGADO", "AGUJEREADO"]:
            return []
        self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.tableroBase + maquina + " WHERE lectura = 0 "
                            "AND RUTA_ASIGNADA LIKE '%" + maquina + "%' ORDER BY OP")
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


