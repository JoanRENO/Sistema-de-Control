from .connection import DataBase


class Plano(DataBase):
    def produccion_diaria(self):
        self.cursor.execute('SELECT * FROM ProduccionDiariaModulosTablero')
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray
