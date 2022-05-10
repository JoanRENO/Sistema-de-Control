from .connection import DataBase
from PIL import Image, ImageDraw, ImageFont, ImageWin
import code128
import re
import win32ui
from dataBase.helpers import fecha


class Reproceso(DataBase):
    def lista_ops(self, maquina):
        if maquina in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' ORDER BY OP")
        else:
            self.cursor.execute("SELECT DISTINCT OP FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND lectura" + maquina + " = 0 ORDER BY OP")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_colores(self, op, maquina):
        if maquina in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT DISTINCT PIEZA_NOMBRECOLOR FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ?"
                                " ORDER BY PIEZA_NOMBRECOLOR", op)
        else:
            self.cursor.execute("SELECT DISTINCT PIEZA_NOMBRECOLOR FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ? AND lectura"+ maquina +" = 0 "
                                "ORDER BY PIEZA_NOMBRECOLOR", op)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_espesores(self, op, color, maquina):
        if maquina in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT DISTINCT PIEZA_PROFUNDO FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ?"
                                " AND PIEZA_NOMBRECOLOR = ? "
                                " ORDER BY PIEZA_PROFUNDO", op, color)
        else:
            self.cursor.execute("SELECT DISTINCT PIEZA_PROFUNDO FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ?"
                                " AND PIEZA_NOMBRECOLOR = ? AND lectura" + maquina + " = 0 "
                                "ORDER BY PIEZA_PROFUNDO", op, color)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def lista_piezas(self, op, color, espesor, maquina):
        if maquina in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT DISTINCT PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? "
                                "ORDER BY PIEZA_DESCRIPCION", op, color, espesor)
        else:
            self.cursor.execute("SELECT DISTINCT PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? AND lectura" + maquina + " = 0 "
                                "ORDER BY PIEZA_DESCRIPCION", op, color, espesor)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def info_piezas(self, op, color, espesor, maquina, pieza):
        if maquina in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT COUNT(idPieza) as CANTIDAD, RUTA_ASIGNADA, PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? AND PIEZA_DESCRIPCION = ? "
                                " GROUP BY RUTA_ASIGNADA, PIEZA_DESCRIPCION", op, color, espesor, pieza)
        else:
            self.cursor.execute("SELECT COUNT(idPieza) as CANTIDAD, RUTA_ASIGNADA, PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maquina + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? AND PIEZA_DESCRIPCION = ? AND lectura" + maquina + " = 0 "
                                "GROUP BY RUTA_ASIGNADA, PIEZA_DESCRIPCION", op, color, espesor, pieza)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            if 'LATERAL' in record[2][:16]:
                record[2] = 'LATERAL'
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def ids_op(self, op, color, espesor, maq_detecto, maq_select, pieza, cantidad):
        if maq_detecto in ["LM", "LP", "LC"]:
            self.cursor.execute("SELECT TOP " + cantidad + " idPieza FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maq_detecto + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? AND PIEZA_DESCRIPCION = ? AND RUTA_ASIGNADA LIKE '%"
                                + maq_select + "%'", op, color, espesor, pieza)
        else:
            self.cursor.execute("SELECT TOP " + cantidad + " idPieza FROM " + DataBase.Tablas.basePiezas +
                                " WHERE RUTA_ASIGNADA LIKE '%" + maq_detecto + "%' AND OP = ? AND PIEZA_NOMBRECOLOR = ?"
                                " AND PIEZA_PROFUNDO = ? AND PIEZA_DESCRIPCION = ? AND lectura" + maq_detecto + " = 0 "
                                "AND RUTA_ASIGNADA LIKE '%" + maq_select + "%'", op, color, espesor, pieza)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        return OutputArray

    def infoID(self, ids):
        self.cursor.execute("SELECT RUTA_ASIGNADA FROM " + DataBase.Tablas.basePiezas + " WHERE idPieza = ?", ids)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        if OutputArray == []:
            return "ID no encontrada"
        return OutputArray[0]['RUTA_ASIGNADA']

    def buscar_om(self, om):
        self.cursor.execute("SELECT a.idModulo, a.PT_PRODUCTO, b.idPieza, b.PIEZA_DESCRIPCION, b.PIEZA_NOMBRECOLOR, "
                            "b.PIEZA_PROFUNDO, b.OP, b.SO FROM " + DataBase.Tablas.baseModulos + " a "
                            "LEFT JOIN " + DataBase.Tablas.basePiezas + " b ON a.idOrdenManufactura = b.idModulo "
                            "WHERE a.idOrdenManufactura = ?", om)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print(OutputArray)
        if OutputArray == []:
            return None
        return OutputArray

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
        txt = Image.new('RGB', (660, 60), (0, 0, 0))
        d = ImageDraw.Draw(txt)
        d.text((100, 6), "REPROCESO - " + maq_select, font=fnt14, fill=(255, 255, 255))
        im.paste(txt, (0, 30))

        # INFO1_1
        txt1_1 = Image.new('RGB', (780, 100), (255, 255, 255))
        d = ImageDraw.Draw(txt1_1)
        d.text((0, 6), OP, font=fnt14_1, fill=(0, 0, 0))
        d.text((100, 66), RUTA_ASIGNADA, font=fnt11, fill=(0, 0, 0))
        im.paste(txt1_1, (680, 30))

        # INFO1_2
        txt1_1 = Image.new('RGB', (300, 140), (0, 0, 0))
        d = ImageDraw.Draw(txt1_1)
        d.text((100, 6), maq_detecto, font=fnt14_1, fill=(255, 255, 255))
        im.paste(txt1_1, (720, 160))

        txt1_1 = Image.new('RGB', (200, 140), (255, 255, 255))
        d = ImageDraw.Draw(txt1_1)
        d.text((2, 6), str(idPieza), font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt1_1, (1040, 160))

        # ORDEN MANUFACTURA
        img = code128.image(idModulo)
        im.paste(img, (140, 100))

        #INFO2
        txt2 = Image.new('RGB', (1250, 400), (255, 255, 255))
        d = ImageDraw.Draw(txt2)
        d.text((280, 2), idModulo, font=fnt10, fill=(0, 0, 0))
        if len(PIEZA_DESCRIPCION) > 64:
            d.text((2, 52), PIEZA_DESCRIPCION[:64], font=fnt10, fill=(0, 0, 0))
            d.text((2, 102), PIEZA_DESCRIPCION[64:] + ' ' + lado, font=fnt10, fill=(0, 0, 0))
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

        #INFO4
        #txt4 = Image.new('RGB', (200, 50), (255, 255, 255))
        #d = ImageDraw.Draw(txt4)
        #d.text((2, 2), str(idPieza), font=fnt10, fill=(0, 0, 0))
        #im.paste(txt4, (1260, 110))

        #INFO5
        txt5 = Image.new('RGB', (600, 140), (255, 255, 255))
        d = ImageDraw.Draw(txt5)
        d.text((2, 0), PIEZA_CODIGORANURA, font=ftn8, fill=(0, 0, 0))
        d.text((2, 40), "FILO DER " + TAPACANTO_DERECHO, font=ftn8, fill=(0, 0, 0))
        d.text((2, 65), "FILO INFERIOR " + TAPACANTO_INFERIOR, font=ftn8, fill=(0, 0, 0))
        d.text((2, 90), "FILO IZQ " + TAPACANTO_IZQUIERDO, font=ftn8, fill=(0, 0, 0))
        d.text((2, 115), "FILO SUPERIOR " + TAPACANTO_SUPERIOR, font=ftn8, fill=(0, 0, 0))
        im.paste(txt5, (640, 560))

        im.save('./static/images/etiquetaREPROCESO.jpg')

    def imprimirEtiqueta(self):
        printer_name = 'ZDesigner GK420t'
        file_name = "./static/images/etiquetaREPROCESO.jpg"

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

    def log_reproceso(self, idPieza, maq_select, pieza_descripcion, maq_detecto, cantidad, ruta, OP, causa):
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.logReproceso + " (maqDetecto, maqReproceso, fecha, cantidad,"
                            " idPieza, descripcion, ruta_asignada, OP, causa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", maq_detecto, maq_select, fecha(),
                            cantidad, idPieza, pieza_descripcion, ruta, OP, causa)
        self.cursor.commit()
        self.close()

    def actualizarTabla(self, ruta, idPieza, maq_detecto, maq_select):
        maquinas = re.split("-", ruta)
        for x in maquinas:
            if x == "LP.C" or x == "LP.P":
                maquinas[maquinas.index(x)] = "LP"
        if maq_detecto == "LP.C" or maq_detecto == "LP.P":
            maq_detecto = "LP"
        print(maquinas)
        print(maq_detecto)
        for x in maquinas:
            if maq_detecto == x:
                pos = maquinas.index(x)
        if maq_detecto == "ARMADO/EMBALADO":
            pos = len(maquinas)-1
        data = []
        for x in maquinas:
            data.append(x)
            if maquinas.index(x) >= pos:
                break
        for x in data:
            if maq_select == x:
                pos2 = maquinas.index(x)
        data2 = []
        for x in data:
            if data.index(x) >= pos2:
                data2.append(x)
        for maq in data2:
            if maq in ['GBN1', 'SLC', 'NST', 'GBM', 'STF', 'IDM', 'MRT1', 'MRT2', 'MRT3', 'MRT4', 'RVR', 'KBT1',
                       'KBT2', 'CHN', 'FTAL1', 'VTP1', 'LEA', 'PRS', 'ALU', 'TGO', 'FAB']:
                    self.cursor.execute("UPDATE " + DataBase.Tablas.basePiezas + " SET lectura" + maq + " = ?, fechaLectura" + maq +
                                        " = ? WHERE idPieza = ? ", 0, None, idPieza)
                    self.cursor.commit()
        self.close()

    def verificarReproceso(self, idPieza):
        self.cursor.execute("SELECT maqDetecto FROM " + DataBase.Tablas.logReproceso + " WHERE idPieza = ?", idPieza)
        aux = self.cursor.fetchone()[0]
        print(aux)
        if aux is not None:
            self.cursor.execute("SELECT lectura" + aux + " FROM " + DataBase().Tablas.basePiezas + " WHERE idPieza = ?"
                                , idPieza)
            aux = self.cursor.fetchone()[0]
            print(aux)
            if aux == 0:
                return 1

