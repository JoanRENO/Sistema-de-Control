from .connection import DataBase
import re
from PIL import Image, ImageDraw, ImageFont, ImageWin
import code128
import win32ui

class Comex(DataBase):
    #ARMAR PAQUETE
    def verificarPieza(self, idPieza):
        self.cursor.execute("SELECT idPieza, idModulo, clasificacion FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE idPieza = ?", idPieza)
        record = self.cursor.fetchone()
        if record is not None:
            idModulo = record[1]
            clasificacion = record[2]
            self.cursor.execute("SELECT idPieza FROM [PRODUCCION_PLANTA].[dbo].[PaquetesCOMEX] WHERE idPieza = ?", idPieza)
            record = self.cursor.fetchone()
            if record is None:
                return 1, idModulo, clasificacion
            else: 
                return 2, 0, 0
        else:
            return 3, 0, 0

    def verPaqueteCompleto(self, idPieza, idModulo, nroPaquete, clasificacion):
        self.cursor.execute("SELECT idPieza FROM [PRODUCCION_PLANTA].[dbo].[PaquetesCOMEX] WHERE estado IS NULL")
        record1 = self.cursor.fetchall()
        print(record1)
        if record1 == []:
            Comex().insertPieza(idPieza , nroPaquete)
            self.cursor.execute("SELECT PIEZA_DESCRIPCION FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE idPieza = ?", idPieza)
            pieza = self.cursor.fetchone()[0]
            record2 = []
            self.cursor.execute("SELECT PIEZA_DESCRIPCION FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE idModulo = ? AND clasificacion = ?", idModulo, clasificacion)
            record1 = self.cursor.fetchall()
            for record in record1:
                record2.append(record[0])
            print(record2, len(record2))
            record2.remove(pieza)
            print(record2, len(record2))
            record3 = ''
            for record in record2:
                record3 += record + '-'
            self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[PaquetesCOMEX] SET estado = ? WHERE idPieza = 0", record3)
            self.cursor.commit()
            self.close()
            if len(record2) == 0:
                return 1
        else:
            self.cursor.execute("SELECT PIEZA_DESCRIPCION FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE idPieza = ?", idPieza)
            record1 = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT estado FROM [PRODUCCION_PLANTA].[dbo].[PaquetesCOMEX] WHERE idPieza = 0")
            record2 = self.cursor.fetchone()[0]
            Piezas = re.split('-', record2)
            Piezas.pop()
            print(Piezas, len(Piezas))
            try:
                print(record1)
                Piezas.remove(record1)
                record3 = ''
                for record in Piezas:
                    record3 += record + '-'
                self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[PaquetesCOMEX] SET estado = ? WHERE idPieza = 0", record3)
                self.cursor.commit()
            except ValueError:
                return 8
            print(Piezas, len(Piezas))
            Comex().insertPieza(idPieza , nroPaquete)
            if len(Piezas) == 0:
                return 1
            return 2

    def insertPieza(self, idPieza, nroPaquete):
        self.cursor.execute("INSERT INTO [dbo].[PaquetesCOMEX] (nroPaquete, idPieza) VALUES (?, ?)", nroPaquete, idPieza)
        self.cursor.commit()
        self.close()
        
    def elminarPieza(self, idPieza):
        self.cursor.execute("DELETE FROM [dbo].[PaquetesCOMEX] WHERE idPieza = ?", idPieza)
        self.cursor.commit()
        self.close()
        
    def getPiezas(self):
        self.cursor.execute("SELECT pla.idPieza, bp.PIEZA_DESCRIPCION FROM PRODUCCION_PLANTA.dbo.PaquetesCOMEX pla INNER JOIN [PRODUCCION_PLANTA].[produccion].[basePiezas] bp ON pla.idPieza = bp.idPieza WHERE pla.estado IS NULL")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getNroPaquete(self):
        self.cursor.execute("SELECT MAX(nroPaquete) FROM PRODUCCION_PLANTA.dbo.PaquetesCOMEX")
        records = self.cursor.fetchone()
        return records[0]
    
    def cerrarPaquete(self, nroPaquete, clasificacion, idPieza):
        self.cursor.execute("UPDATE PRODUCCION_PLANTA.dbo.PaquetesCOMEX SET estado = 'CERRADO' WHERE nroPaquete = ?", nroPaquete)
        self.cursor.execute("SELECT SO, OP  FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE idPieza = ?", idPieza)
        record = self.cursor.fetchone()
        so = record[0]
        aux = re.split(' ', so)
        acuerdo = aux[0]
        #ambiente = so[len(acuerdo)+3:]
        #print(ambiente)
        self.cursor.execute("INSERT INTO [dbo].[PalletsCOMEX] (nroPaquete, clasificacion, acuerdo, op) VALUES (?, ?, ?, ?)", nroPaquete, clasificacion, acuerdo, record[1])
        self.cursor.commit()
        self.close()

    #ARMAR PALLET
    def getNroPallet(self):
        self.cursor.execute("SELECT MAX(nroPallet) FROM PRODUCCION_PLANTA.dbo.PalletsCOMEX")
        records = self.cursor.fetchone()
        return records[0]
    
    def getPalletsAbiertos(self):
        self.cursor.execute("SELECT DISTINCT c.nroPallet , c.Acuerdo, p.estado FROM PRODUCCION_PLANTA.dbo.ContenedoresCOMEX c " + 
                            "LEFT JOIN PRODUCCION_PLANTA.dbo.PalletsCOMEX p ON p.nroPallet = c.nroPallet " + 
                            "WHERE p.estado IS NULL AND c.nroPallet > 0 GROUP BY c.nroPallet , c.Acuerdo, c.Ambiente, p.estado")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray
    
    def getAmbientesAcuerdo(self, nroPallet):
        self.cursor.execute("SELECT c.Ambiente, p.estado FROM PRODUCCION_PLANTA.dbo.ContenedoresCOMEX c " + 
                            "LEFT JOIN PRODUCCION_PLANTA.dbo.PalletsCOMEX p ON p.nroPallet = c.nroPallet " + 
                            "WHERE p.estado IS NULL AND c.nroPallet = ? GROUP BY c.nroPallet , c.Acuerdo, c.Ambiente, p.estado", nroPallet)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray
    
    def getAmbientesBOs(self, nroPallet):
        self.cursor.execute("SELECT Acuerdo FROM [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] WHERE nroPallet = ?", nroPallet)
        acuerdo = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT DISTINCT SO FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE SO LIKE '%" + acuerdo + "%'")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        OutputArrayAux = []
        for aux in OutputArray:
            OutputArrayAux.append(aux['SO'][len(acuerdo)+3:])
        return OutputArrayAux
    
    def agregarAmbientePallet(self, nroPallet, ambiente):
        self.cursor.execute("SELECT Acuerdo FROM [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] WHERE nroPallet = ?", nroPallet)
        acuerdo = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] (nroPallet, Acuerdo, Ambiente) VALUES (?,?,?)", nroPallet, acuerdo, ambiente)
        self.cursor.commit()
        paquetes_ambinetes = Comex().getArmadoPallet(nroPallet, ambiente)
        aux = ''
        for paquete in paquetes_ambinetes:
            for piezas in paquete:
                aux += piezas + '-'
            aux += '@'
        cantidad = len(paquetes_ambinetes)
        self.cursor.execute("UPDATE [dbo].[ContenedoresCOMEX] SET auxiliar = ?, cantPaquetes = ? WHERE nroPallet = ? AND ambiente = ?", aux, cantidad, nroPallet, ambiente)
        self.cursor.commit()
        self.close()

    def getArmadoPallet(self, nroPallet, ambiente):
        self.cursor.execute("SELECT Acuerdo FROM [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] WHERE nroPallet = ?", nroPallet)
        acuerdo = self.cursor.fetchone()[0]
        so = acuerdo + ' - ' + ambiente
        self.cursor.execute("SELECT PIEZA_DESCRIPCION, idModulo, Clasificacion FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE so = ?", so)
        records1 = self.cursor.fetchall()
        OutputArray1 = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records1:
            OutputArray1.append(dict(zip(columnNames, record)))
        self.cursor.execute("SELECT DISTINCT idModulo, Clasificacion FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex] WHERE so = ?", so)
        records2 = self.cursor.fetchall()
        OutputArray2 = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records2:
            OutputArray2.append(dict(zip(columnNames, record)))
        print(len(OutputArray2))
        piezas_totales = []
        for row2 in OutputArray2:
            aux = []
            for row1 in OutputArray1:
                if row1['idModulo'] == row2['idModulo'] and row1['Clasificacion'] == row2['Clasificacion']:
                    aux.append(row1['PIEZA_DESCRIPCION'])
                aux.sort()
            piezas_totales.append(aux)
        print(piezas_totales)
        print(len(piezas_totales))
        return piezas_totales
        
    def getPiezasPaquetes(self, nroPaquete):
        self.cursor.execute("SELECT pc.idPieza, bp.PIEZA_DESCRIPCION FROM PaquetesCOMEX pc INNER JOIN PRODUCCION_PLANTA.produccion.basePiezas bp ON bp.idPieza = pc.idPieza WHERE nroPaquete = ?", nroPaquete)
        piezas = self.cursor.fetchall()
        print(piezas)
        piezas_desc = []
        for row in piezas:
            piezas_desc.append(row[1])
        piezas_desc.sort()
        print(piezas_desc)
        return piezas_desc

    def getCantPaquetes(self, nroPallet, ambiente):
        print(nroPallet, ambiente)
        self.cursor.execute("SELECT cantPaquetes FROM PRODUCCION_PLANTA.dbo.ContenedoresCOMEX WHERE ambiente = ? AND nroPallet = ?", ambiente, nroPallet)
        cantTotal = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(nroPaquete) as cantPaquete FROM PRODUCCION_PLANTA.dbo.PalletsCOMEX WHERE Ambiente = ? AND nroPallet = ?", ambiente, nroPallet)
        cant = self.cursor.fetchone()[0]
        return cant, cantTotal
        
        
    def asignarPalletPaquete(self, nroPaquete, nroPallet, ambiente):
        self.cursor.execute("SELECT nroPallet FROM PRODUCCION_PLANTA.dbo.PalletsCOMEX WHERE nroPaquete = ?", nroPaquete)
        record = self.cursor.fetchone()
        print('Encontro paquete: ')
        print(record)
        if record is None:
            #Paquete no existe
            return 3
        else:
            if record[0] is None:
                #Consulto ambiente de paquetes
                self.cursor.execute("SELECT auxiliar FROM [PRODUCCION_PLANTA].[dbo].[ContenedoresCOMEX] WHERE nroPallet = ? AND ambiente = ?", nroPallet, ambiente)
                aux = self.cursor.fetchone()[0]
                #Desempaqueto
                aux2 = aux.split('@')
                aux2.pop()
                aux3 = []
                for a in aux2:
                    b = a.split('-')
                    b.pop()
                    b.sort()
                    aux3.append(b)
                paquetes_restantes = aux3
                paquete = Comex().getPiezasPaquetes(nroPaquete)
                try:
                    paquetes_restantes.remove(paquete)
                    print('Exito')
                    self.cursor.execute("UPDATE PRODUCCION_PLANTA.dbo.PalletsCOMEX SET nroPallet = ?, ambiente = ? WHERE nroPaquete = ?", nroPallet, ambiente, nroPaquete)
                    #Empaqueto
                    aux = ''
                    for paquete in paquetes_restantes:
                        for piezas in paquete:
                            aux += piezas + '-'
                        aux += '@'
                    self.cursor.execute("UPDATE PRODUCCION_PLANTA.dbo.ContenedoresCOMEX SET auxiliar = ? WHERE nroPallet = ? AND ambiente = ?", aux, nroPallet, ambiente)
                    self.cursor.commit()
                    self.close()
                    return 1
                except:
                    print('Fallo, paquete incorrecto no pertenece al ambiente')
                    return 4
            else:
                #Paquete ya asignado
                return 3

    def getDataPallet2(self, nroPallet, ambiente):
        self.cursor.execute("SELECT nroPaquete, Clasificacion, ambiente FROM [PRODUCCION_PLANTA].[dbo].[PalletsCOMEX] WHERE nroPallet = ? AND ambiente = ?", nroPallet, ambiente)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getDataPallet(self, nroPallet):
        self.cursor.execute("SELECT ambiente FROM [PRODUCCION_PLANTA].[dbo].[ContenedoresCOMEX] WHERE nroPallet = ?", nroPallet)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def elminarPaquete(self, nroPaquete, ambiente):
        self.cursor.execute("SELECT nroPallet FROM [PRODUCCION_PLANTA].[dbo].[PalletsCOMEX] WHERE nroPaquete = ?", nroPaquete)
        nroPallet = self.cursor.fetchone()[0]
        print(nroPallet, ambiente)
        paquete = Comex().getPiezasPaquetes(nroPaquete)
        print('Paquete: ')
        print(paquete)
        #Consulto ambiente de paquetes
        self.cursor.execute("SELECT auxiliar FROM [PRODUCCION_PLANTA].[dbo].[ContenedoresCOMEX] WHERE nroPallet = ? AND ambiente = ?", nroPallet, ambiente)
        aux = self.cursor.fetchone()[0]
        #Desempaqueto
        aux2 = aux.split('@')
        aux2.pop()
        aux3 = []
        for a in aux2:
            b = a.split('-')
            b.pop()
            b.sort()
            aux3.append(b)
        paquetes_restantes = aux3
        paquetes_restantes.append(paquete)
        aux = ''
        for paquete in paquetes_restantes:
            for piezas in paquete:
                aux += piezas + '-'
            aux += '@'
        self.cursor.execute("UPDATE PRODUCCION_PLANTA.dbo.ContenedoresCOMEX SET auxiliar = ? WHERE nroPallet = ? AND ambiente = ?", aux, nroPallet, ambiente)
        self.cursor.execute("UPDATE [dbo].[PalletsCOMEX] SET nroPallet = NULL , ambiente = NULL WHERE nroPaquete = ?", nroPaquete)
        self.cursor.commit()
    
    def crearPallet(self, acuerdo, ambiente):
        self.cursor.execute("SELECT MAX(nroPallet) FROM PRODUCCION_PLANTA.dbo.ContenedoresCOMEX")
        records = self.cursor.fetchone()
        nroPallet = records[0] + 1
        self.cursor.execute("INSERT INTO [PRODUCCION_PLANTA].[dbo].[ContenedoresCOMEX] (nroPallet, acuerdo, ambiente) VALUES (?,?,?)", nroPallet, acuerdo, ambiente)
        self.cursor.commit()
        #Obtener todos los paquetes de un ambiente
        paquetes_ambinetes = Comex().getArmadoPallet(nroPallet, ambiente)
        aux = ''
        for paquete in paquetes_ambinetes:
            for piezas in paquete:
                aux += piezas + '-'
            aux += '@'
        cantidad = len(paquetes_ambinetes)
        self.cursor.execute("UPDATE [dbo].[ContenedoresCOMEX] SET auxiliar = ?, cantPaquetes = ? WHERE nroPallet = ? AND ambiente = ?", aux,  cantidad, nroPallet, ambiente)
        self.cursor.commit()
        self.close()
        
    def getNroPalletContenedor(self):
        self.cursor.execute("SELECT MAX(nroPallet) FROM PRODUCCION_PLANTA.dbo.ContenedoresCOMEX")
        records = self.cursor.fetchone()
        self.cursor.close()
        return records[0]
    
    def getNroPalletPaquete(self, nroPaquete):
        print(nroPaquete)
        self.cursor.execute("SELECT nroPallet FROM PRODUCCION_PLANTA.dbo.PalletsCOMEX WHERE nroPaquete = ?", nroPaquete)
        records = self.cursor.fetchone()
        print(records[0])
        return records[0]

    def cerrarPallet(self, nroPallet, ambiente):
        self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[PalletsCOMEX] SET estado = 'CERRADO' WHERE nroPallet = ? AND ambiente = ? ", nroPallet, ambiente)
        self.cursor.commit()
        self.close()
        
    def getContenedores(self):
        self.cursor.execute("SELECT DISTINCT nroContenedor, destino, fechaSalida FROM [PRODUCCION_PLANTA].[dbo].[contenedoresSalidaCOMEX] WHERE nroContenedor > 0")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getPalletsContenedor(self):
        self.cursor.execute("""SELECT  c.nroContenedor , c.nroPallet, c.Acuerdo, c.Ambiente, COUNT(nroPaquete) as 'CantPaquetes'  FROM [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] c 
                            INNER JOIN PRODUCCION_PLANTA.dbo.PalletsCOMEX p ON p.nroPallet = c.nroPallet
                            GROUP BY c.nroContenedor , c.nroPallet, c.Acuerdo, c.Ambiente""")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getPalletsPendientes(self):
        self.cursor.execute("SELECT DISTINCT cc.nroPallet, cc.Acuerdo, cc.Ambiente  FROM [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] cc INNER JOIN [PRODUCCION_PLANTA].[dbo].[PalletsCOMEX] pc ON cc.nroPallet = pc.nroPallet WHERE cc.nroContenedor IS NULL AND pc.estado = 'CERRADO' AND cc.nroPallet > 0")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def crearContenedor(self):
        self.cursor.execute("SELECT MAX(nroContenedor) FROM [PRODUCCION_PLANTA].[dbo].[contenedoresSalidaCOMEX]")
        redord = self.cursor.fetchone()
        self.cursor.execute("INSERT INTO [PRODUCCION_PLANTA].[dbo].[contenedoresSalidaCOMEX] (nroContenedor) VALUES (?)", redord[0]+1)
        self.cursor.commit()
        self.close()

    def eliminarPallet(self, nroPallet):
        self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] SET nroContenedor = NULL WHERE nroPallet = ?", nroPallet)
        self.cursor.commit()
        self.close()
        
    def agregarPallet(self, nroPallet, nroContenedor):
        self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[contenedoresCOMEX] SET nroContenedor = ? WHERE nroPallet = ?", nroContenedor, nroPallet)
        self.cursor.commit()
        self.close()
        
    def cerrarContenedor(self, nroContenedor, destino, fechaSalida):
        self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[ContenedoresSalidaCOMEX] SET destino = ?, fechaSalida = ? WHERE nroContenedor = ?", destino, fechaSalida, nroContenedor)
        self.cursor.execute("UPDATE [PRODUCCION_PLANTA].[dbo].[ContenedoresCOMEX] SET estado = 'CERRADO' WHERE nroContenedor = ?", nroContenedor)
        self.cursor.commit()
        self.close()
        
    def getSOs(self):
        self.cursor.execute("SELECT DISTINCT SO FROM [PRODUCCION_PLANTA].[dbo].[zzzzzz_comex]")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray
    
    #IMPRIMIR ETIQUETA
    def generar_barcode(self, idPieza, PIEZA_DESCRIPCION, SO, PRODUCTO_TERMINADO, OP, RUTA_ASIGNADA, idModulo,
                        PIEZA_CODIGORANURA, TAPACANTO_DERECHO, TAPACANTO_INFERIOR, TAPACANTO_IZQUIERDO,
                        TAPACANTO_SUPERIOR, PIEZA_CODIGO, maq_select, maq_detecto, lado):
        # generar las fonts
        fnt14 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 56)
        fnt14_1 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 46)
        fnt11 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 40)
        fnt10 = ImageFont.truetype('static/fuente/calibri-regular.ttf', 40)
        ftn8 = ImageFont.truetype('static/fuente/calibri-bold-italic.ttf', 34)

        # IMAGEN EN BLANCO
        im = Image.new('RGB', (1440, 720), (255, 255, 255))



        # ID PIEZA
        img2 = code128.image(idPieza)
        a = img2.resize((590, 180))
        nImg2 = a.transpose(Image.ROTATE_90)
        im.paste(nImg2, (1300, 120))

        #INFO1
        txt = Image.new('RGB', (400, 60), (0, 0, 0))
        d = ImageDraw.Draw(txt)
        d.text((100, 6), "COMEX ", font=fnt14, fill=(255, 255, 255))
        im.paste(txt, (0, 30))

        # INFO1_1
        txt1_1 = Image.new('RGB', (900, 100), (255, 255, 255))
        d = ImageDraw.Draw(txt1_1)
        d.text((0, 6), OP, font=fnt14_1, fill=(0, 0, 0))
        d.text((260, 66), RUTA_ASIGNADA, font=fnt11, fill=(0, 0, 0))
        im.paste(txt1_1, (460, 30))

        txt1_1 = Image.new('RGB', (200, 140), (255, 255, 255))
        d = ImageDraw.Draw(txt1_1)
        d.text((2, 6), str(idPieza), font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt1_1, (1040, 160))

        # ORDEN MANUFACTURA
        img = code128.image(idModulo)
        im.paste(img, (140, 100))

        #INFO2
        txt2 = Image.new('RGB', (1270, 400), (255, 255, 255))
        d = ImageDraw.Draw(txt2)
        d.text((280, 2), idModulo, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION) > 62:
            d.text((2, 52), PIEZA_DESCRIPCION[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 102), PIEZA_DESCRIPCION[62:] + ' ' + lado, font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 52), PIEZA_DESCRIPCION + ' ' + lado, font=fnt10, fill=(0, 0, 0))
        d.text((2, 150), SO, font=fnt11, fill=(0, 0, 0))
        if len(PRODUCTO_TERMINADO) > 128:
            d.text((2, 200), PRODUCTO_TERMINADO[:64], font=fnt10, fill=(0, 0, 0))
            d.text((2, 250), PRODUCTO_TERMINADO[64:128], font=fnt10, fill=(0, 0, 0))
            d.text((2, 300), PRODUCTO_TERMINADO[128:], font=fnt10, fill=(0, 0, 0))
        elif len(PRODUCTO_TERMINADO) > 64 and len(PRODUCTO_TERMINADO) <= 128:
            d.text((2, 200), PRODUCTO_TERMINADO[:64], font=fnt10, fill=(0, 0, 0))
            d.text((2, 250), PRODUCTO_TERMINADO[64:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 200), PRODUCTO_TERMINADO, font=fnt10, fill=(0, 0, 0, 180))
        d.text((70, 350), PIEZA_CODIGO, font=fnt10, fill=(0, 0, 0))
        im.paste(txt2, (16, 200))

        #CODIGO DE PLANO
        outPLANO = code128.image(PIEZA_CODIGO)
        im.paste(outPLANO, (44, 600))

        #INFO5
        txt5 = Image.new('RGB', (600, 140), (255, 255, 255))
        d = ImageDraw.Draw(txt5)
        d.text((2, 0), PIEZA_CODIGORANURA, font=ftn8, fill=(0, 0, 0))
        d.text((2, 40), "FILO DER " + TAPACANTO_DERECHO, font=ftn8, fill=(0, 0, 0))
        d.text((2, 65), "FILO INFERIOR " + TAPACANTO_INFERIOR, font=ftn8, fill=(0, 0, 0))
        d.text((2, 90), "FILO IZQ " + TAPACANTO_IZQUIERDO, font=ftn8, fill=(0, 0, 0))
        d.text((2, 115), "FILO SUPERIOR " + TAPACANTO_SUPERIOR, font=ftn8, fill=(0, 0, 0))
        im.paste(txt5, (640, 560))

        im.save('./static/images/etiquetaCOMEX.jpg')

    def imprimirEtiqueta(self, tipo):
        printer_name = 'ZDesigner GK420t COMEX'
        if tipo == 'pieza':
            file_name = "./static/images/etiquetaCOMEX.jpg"
        else:
            file_name = "./static/images/etiquetaCOMEX_PAQUETE.jpg"

        PHYSICALWIDTH = 110
        PHYSICALHEIGHT = 111

        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)

        bmp = Image.open(file_name)

        hDC.StartDoc(file_name)
        hDC.StartPage()

        dib = ImageWin.Dib(bmp)
        dib.draw(hDC.GetHandleOutput(), (0, 0, printer_size[0], printer_size[1]))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        
    def info_final(self, id):
        self.cursor.execute("SELECT idPieza, PIEZA_DESCRIPCION, SO, PRODUCTO_TERMINADO, OP, RUTA_ASIGNADA, "
                            "idModulo, PIEZA_CODIGORANURA, PIEZA_TAPACANTO_DERECHO, PIEZA_TAPACANTO_INFERIOR, "
                            "PIEZA_TAPACANTO_IZQUIERDO, PIEZA_TAPACANTO_SUPERIOR, PIEZA_CODIGO, "
                            "PIEZA_NOMBREMODOSUSTENTACION"
                            " FROM " + DataBase.Tablas.basePiezas + " WHERE idPieza = ?", id)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray[0]
    
    def info_paquetes(self, nroPaquete):
        self.cursor.execute("""
                            SELECT CASE WHEN COUNT(pc.idPIeza) > 1 THEN PIEZA_DESCRIPCION + ' X' + CONVERT(varchar(2), COUNT(pc.idPIeza)) ELSE PIEZA_DESCRIPCION END as PIEZA_DESCRIPCION 
                            FROM PRODUCCION_PLANTA.dbo.PaquetesCOMEX pc INNER JOIN PRODUCCION_PLANTA.produccion.basePiezas bp ON pc.idPIeza = bp.idPieza
                            WHERE nroPaquete = ?
                            GROUP BY PIEZA_DESCRIPCION  
                            """, nroPaquete)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        print(OutputArray)
        return OutputArray
    
    def getOP(self, nroPaquete):
        self.cursor.execute("SELECT OP FROM PRODUCCION_PLANTA.produccion.basePiezas WHERE idPieza = (SELECT TOP 1 idPieza FROM PRODUCCION_PLANTA.dbo.paquetesCOMEX WHERE nroPaquete = ?)", nroPaquete)
        return self.cursor.fetchone()[0]

    def generar_barcode_paquete(self, nroPaquete, PIEZA_DESCRIPCION1, PIEZA_DESCRIPCION2, PIEZA_DESCRIPCION3, PIEZA_DESCRIPCION4, PIEZA_DESCRIPCION5, PIEZA_DESCRIPCION6, OP):
        # generar las fonts
        fnt14 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 56)
        fnt14_1 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 46)
        fnt11 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 40)
        fnt10 = ImageFont.truetype('static/fuente/calibri-regular.ttf', 40)
        ftn8 = ImageFont.truetype('static/fuente/calibri-bold-italic.ttf', 34)

        # IMAGEN EN BLANCO
        im = Image.new('RGB', (1440, 720), (255, 255, 255))



        # NRO PAQUETE
        img2 = code128.image(nroPaquete)
        a = img2.resize((590, 180))
        nImg2 = a.transpose(Image.ROTATE_90)
        im.paste(nImg2, (1300, 120))

        #INFO1
        txt = Image.new('RGB', (420, 60), (0, 0, 0))
        d = ImageDraw.Draw(txt)
        d.text((60, 6), "CX - 777777" + str(nroPaquete), font=fnt14, fill=(255, 255, 255))
        im.paste(txt, (0, 30))

        # INFO1_1
        txt1_1 = Image.new('RGB', (900, 100), (255, 255, 255))
        d = ImageDraw.Draw(txt1_1)
        d.text((0, 6), OP, font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt1_1, (460, 30))

        #txt1_1 = Image.new('RGB', (200, 140), (255, 255, 255))
        #d = ImageDraw.Draw(txt1_1)
        #d.text((2, 6), 'Nro Paquete: ' + str(nroPaquete), font=fnt14_1, fill=(0, 0, 0))
        #im.paste(txt1_1, (1040, 60))

        #INFO3
        txt3 = Image.new('RGB', (1270, 600), (255, 255, 255))
        d = ImageDraw.Draw(txt3)
        if len(PIEZA_DESCRIPCION1) > 62:
            d.text((2, 10),'*' + PIEZA_DESCRIPCION1[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 60), PIEZA_DESCRIPCION1[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 10), '*' + PIEZA_DESCRIPCION1, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION2) > 62:
            d.text((2, 110),'*' + PIEZA_DESCRIPCION2[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 160), PIEZA_DESCRIPCION2[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 110), '*' + PIEZA_DESCRIPCION2, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION3) > 62:
            d.text((2, 210),'*' + PIEZA_DESCRIPCION3[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 260), PIEZA_DESCRIPCION3[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 210), '*' + PIEZA_DESCRIPCION3, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION4) > 62:
            d.text((2, 310),'*' + PIEZA_DESCRIPCION4[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 360), PIEZA_DESCRIPCION4[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 310), '*' + PIEZA_DESCRIPCION4, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION5) > 62:
            d.text((2, 410),'*' + PIEZA_DESCRIPCION5[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 460), PIEZA_DESCRIPCION5[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 410), '*' + PIEZA_DESCRIPCION5, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION6) > 62:
            d.text((2, 510),'*' + PIEZA_DESCRIPCION6[:62], font=fnt10, fill=(0, 0, 0))
            d.text((2, 560), PIEZA_DESCRIPCION6[62:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 510), '*' + PIEZA_DESCRIPCION6, font=fnt10, fill=(0, 0, 0))
        im.paste(txt3, (16, 100))
        im.save('./static/images/etiquetaCOMEX_PAQUETE.jpg')