from .connection import DataBase


class Plano(DataBase):
    def produccion_diaria(self):
        self.cursor.execute('SELECT * FROM ProduccionDiariaModulosTablero')
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            if record[0] == 'Multifamiliar (u obra)':
                record[0] = 'Multifamiliar'
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print(OutputArray)
        if len(OutputArray) == 1:
            if OutputArray[0]['Acuerdo/Tipo de pedido'] == 'Unifamiliar':
                OutputArray.append({'Acuerdo/Tipo de pedido': 'Multifamiliar', 'Cantidad': 0, 'Objetivo': '100'})
            else:
                OutputArray.append({'Acuerdo/Tipo de pedido': 'Unifamiliar', 'Cantidad': 0, 'Objetivo': '150'})
        elif len(OutputArray) == 0:
            OutputArray.append({'Acuerdo/Tipo de pedido': 'Multifamiliar', 'Cantidad': 0, 'Objetivo': '100'})
            OutputArray.append({'Acuerdo/Tipo de pedido': 'Unifamiliar', 'Cantidad': 0, 'Objetivo': '150'})
        return OutputArray
