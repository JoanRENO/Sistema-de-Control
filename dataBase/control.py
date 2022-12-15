from .connection import DataBase
from .helpers import fecha
import requests
from flask import url_for
from PIL import Image, ImageDraw, ImageFont, ImageWin
import code128
import win32ui

class Control(DataBase):
    def getTabla(self, maquina):
        hoy = fecha().date()
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "SELECT TOP 8 idOrdenManufactura, PT_PRODUCTO FROM " + DataBase.Tablas.baseModulos + \
                       " where CONVERT (DATE, fechaLecturaHORNO) = ? ORDER BY fechaLecturaHorno DESC"
        else:
            complete = "SELECT TOP 8 idPieza, PIEZA_DESCRIPCION FROM " + DataBase.Tablas.basePiezas + \
                       " where CONVERT (DATE, fechaLectura" + maquina + ") = ? ORDER BY fechaLectura" + maquina + " DESC"
        self.cursor.execute(complete, hoy)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def verificar_cod(self, codigo, maquina):
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "SELECT (CASE WHEN lecturahorno >= 1 THEN 1 ELSE 0 END) as VER FROM " + DataBase.Tablas.baseModulos + \
                       " WHERE idOrdenManufactura=?"
        elif maquina == "AGUJEREADO" or maquina == "PEGADO" or maquina == "PLACARD":
            complete = "SELECT (CASE WHEN lectura" + maquina + " >= 1 THEN 1 ELSE 0 END) FROM " + DataBase.Tablas.basePiezas + \
                        " WHERE idPieza=?"
        else:
            complete = "SELECT (CASE WHEN lectura" + maquina + " >= 1 THEN 1 ELSE 0 END) FROM  " + DataBase.Tablas.basePiezas + \
                        " WHERE idPieza=? AND RUTA_ASIGNADA LIKE '%" + maquina + "%'"
        self.cursor.execute(complete, codigo)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
        return data

    def updatePM(self, codigo, maquina):
        if maquina == "HORNO" or maquina == "PLTER":
            complete = "UPDATE " + DataBase.Tablas.baseModulos + " SET fechaLecturaHorno = ?, lecturaHorno = 1 " \
                       "WHERE idOrdenManufactura = ?"
        else:
            complete = "UPDATE " + DataBase.Tablas.basePiezas + " SET fechaLectura" + maquina + " = ?, lectura" + maquina + " = 1 " \
                        "WHERE idPieza = ?"
        self.cursor.execute(complete, fecha(), codigo)
        self.cursor.commit()
        self.close()

    def putQtyProduced(self, om, idOM):
        self.cursor.execute("SELECT COUNT(idModulo) FROM " + DataBase.Tablas.baseModulos +
                            " WHERE ORDEN_MANUFACTURA = ? AND lecturaHorno >= 1", om)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]

        headers = {'Content-type': 'application/json', 'Accept': 'application/json',
                   'Authorization': 'Basic e7d942c4-5bc4-4529-b24a-8d0b6bc01da5'}

        username = "batch"
        password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"

        contents = '{"x_pqty": ' + str(data) + ' ,"x_estado": "a_procesar"}'
        bytes(contents, encoding="utf-8")
        print(contents)

        url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production/' + str(idOM)
        response = requests.put(url, auth=(username, password), data=contents, headers=headers)

        # Imprime los resultados
        status = response.status_code

        responseGet = requests.get(url, auth=(username, password))

        getStatus = str(status) + str(responseGet.json())

        Control().logOdoo(idOM, om, status, getStatus)
        return str(status)

    #def verificarComplete(self, om):
    #    print("PASO 2")
    #    self.cursor.execute(
    #        "SELECT CASE WHEN COUNT(idModulo) = SUM(CASE WHEN lecturaHorno >= 1 THEN 1 ELSE 0 END) THEN 1 ELSE 0 END as VER FROM " + DataBase.Tablas.baseModulos +
    #        " WHERE ORDEN_MANUFACTURA = ?", om)
    #    data = self.cursor.fetchone()
    #    self.close()
    #    if data is not None:
    #        data = data[0]
    #    print(data)
    #    return data

    def getIdOdoo(self, om):
        try:
            print("PASO 3")
            username = "batch"
            password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"

            args = {"args": [[["name", "=", om]]]}
            url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production'
            print(url)

            response = requests.patch(url, auth=(username, password), json=args)

            # Imprime los resultados
            status = response.status_code
            if status == 200:
                getResult = response.json()
                idOdoo = getResult[0]['id']
                return status, idOdoo
            else:
                return 0, 0
        except:
            return 0, 0

    #def putOdoo(self, idOM):
    #    print("PASO 4")
    #    headers = {'Content-type': 'application/json', 'Accept': 'application/json',
    #               'Authorization': 'Basic e7d942c4-5bc4-4529-b24a-8d0b6bc01da5'}

    #    username = "batch"
    #    password = "e7d942c4-5bc4-4529-b24a-8d0b6bc01da5"


    #    contents = '{"x_estado": "a_procesar"}'
    #    bytes(contents, encoding="utf-8")
    #    print(contents)

    #    url = 'https://prod.renodirector.com/api/v1/infopostot/mrp.production/' + str(idOM)
    #    response = requests.put(url, auth=(username, password), data=contents, headers=headers)

        # Imprime los resultados
    #    status = response.status_code
    #    print(status)

    #    response = requests.get(url, auth=(username, password))

        # Imprime los resultados
    #    getStatus = str(response.status_code) + str(response.json())
    #    print(getStatus)
    #    return str(status), getStatus

    def logOdoo(self, idOM, OM, status, getStatus):
        self.cursor.execute("""
                                INSERT INTO [dbo].[logPUT]
                                        (idOM, fecha, OM, status, getResult)
                                    VALUES
                                        (?,?,?,?,?)
                            """, idOM, fecha(), OM, status, getStatus)
        self.cursor.commit()
        self.close()
        
    def logTablaOdoo(self, OM):
        self.cursor.execute("""
                                INSERT INTO [dbo].[logPUT]
                                        (idOM, fecha, OM, status, getResult)
                                    VALUES
                                        ('1',?,?,'1',null)
                            """, fecha(), OM)
        self.cursor.commit()
        self.close()

    def getOM(self, idOM):
        print("PASO 1")
        self.cursor.execute(
            "SELECT ORDEN_MANUFACTURA FROM " + DataBase.Tablas.baseModulos + " WHERE idOrdenManufactura = ?", idOM)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
        print(data)
        return data
    
    def imprimir_etiqueta(self, prmo):
        self.cursor.execute("""
                            SELECT [idOrdenManufactura]
                            ,[ORDEN_MANUFACTURA]
                            ,[SO]
                            ,[FRANQUICIA]
                            ,[CLIENTE_FINAL]
                            ,[PT_PRODUCTO]
                            ,[OP]
                            ,ReferenciaInterna
                        FROM [PRODUCCION_PLANTA].[produccion].[baseModulos] bm
                        INNER JOIN [PRODUCCION_PLANTA].[dbo].[BaseOM_Codigo] co ON co.Referencia = bm.ORDEN_MANUFACTURA
                        WHERE idOrdenManufactura = ?
                            """, prmo)
        info = self.cursor.fetchone()
        print(info)
        PRODUCTO = info[5]
        REFERENCIA: str = info[7]
        Cliente = info[4] 
        Franquicia = info[3] 
        SO = info[2] 
        OP = info[6] 
        PR = info[1]
        REFERENCIA = REFERENCIA.replace("-", "")
        # generar las fonts
        fnt14 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 56)
        fnt14_1 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 34)
        fnt11 = ImageFont.truetype('static/fuente/FontsFree-Net-arial-bold.ttf', 40)
        fnt10 = ImageFont.truetype('static/fuente/calibri-regular.ttf', 28)

        # IMAGEN EN BLANCO
        im = Image.new('RGB', (1000, 750), (255, 255, 255))

        # CODE BAR
        img2 = code128.image(REFERENCIA)
        a = img2.resize((900, 140))
        im.paste(a, (50, 560))
        
        #TITULO 
        txt = Image.new('RGB', (400, 60), (0, 0, 0))
        d = ImageDraw.Draw(txt)
        d.text((40, 6), "DESPACHO", font=fnt14, fill=(255, 255, 255))
        im.paste(txt, (0, 10))
        
        #INFO1.1
        txt = Image.new('RGB', (600, 40), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        d.text((0, 0), OP, font=fnt11, fill=(0, 0, 0))
        im.paste(txt, (440 , 10))
        
        #INFO1.2
        txt = Image.new('RGB', (600, 40), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        d.text((50, 0), PR, font=fnt11, fill=(0, 0, 0))
        im.paste(txt, (440 , 60))
        
        #INFO2
        txt = Image.new('RGB', (980, 180), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        print(len(PRODUCTO))
        if len(PRODUCTO) > 192:
            d.text((2, 0), PRODUCTO[:64], font=fnt10, fill=(0, 0, 0))
            d.text((2, 40), PRODUCTO[64:128], font=fnt10, fill=(0, 0, 0))
            d.text((2, 80), PRODUCTO[128:192], font=fnt10, fill=(0, 0, 0))
            d.text((2, 120), PRODUCTO[192:], font=fnt10, fill=(0, 0, 0))
        elif len(PRODUCTO) > 128 and len(PRODUCTO) <= 192:
            d.text((2, 0), PRODUCTO[:64], font=fnt10, fill=(0, 0, 0))
            d.text((2, 40), PRODUCTO[64:128], font=fnt10, fill=(0, 0, 0))
            d.text((2, 80), PRODUCTO[128:], font=fnt10, fill=(0, 0, 0))
        elif len(PRODUCTO) > 64 and len(PRODUCTO) <= 128:
            d.text((2, 0), PRODUCTO[:64], font=fnt10, fill=(0, 0, 0, 180))
            d.text((2, 40), PRODUCTO[64:], font=fnt10, fill=(0, 0, 0))
        else:
            d.text((2, 0), PRODUCTO, font=fnt10, fill=(0, 0, 0, 180))
        im.paste(txt, (20, 120))
        
        #INFO3
        txt = Image.new('RGB', (980, 120), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        if len(SO) > 104:
            d.text((2, 0), SO[:52], font=fnt14_1, fill=(0, 0, 0))
            d.text((2, 40), SO[52:104], font=fnt14_1, fill=(0, 0, 0))
            d.text((2, 80), SO[104:], font=fnt14_1, fill=(0, 0, 0))
        elif len(SO) > 52 and len(SO) <= 104:
            d.text((2, 0), SO[:52], font=fnt14_1, fill=(0, 0, 0))
            d.text((2, 40), SO[52:], font=fnt14_1, fill=(0, 0, 0))
        else:
            d.text((2, 0), SO, font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt, (20 , 300))
        
        #INFO4
        txt = Image.new('RGB', (980, 60), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        d.text((2, 0), Franquicia, font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt, (20 , 420))
        
        #INFO4
        txt = Image.new('RGB', (980, 60), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        d.text((2, 0), Cliente, font=fnt14_1, fill=(0, 0, 0))
        im.paste(txt, (20 , 470))
        
        #INFO5
        txt = Image.new('RGB', (980, 60), (255, 255, 255))
        d = ImageDraw.Draw(txt)
        d.text((2, 0), REFERENCIA, font=fnt11, fill=(0, 0, 0))
        im.paste(txt, (380 , 500))

        im.save('./static/images/ETIQ_DESPACHO.jpg')
        
        #IMPRIMIR ETIQUETA
        printer_name = 'HPRT HT300 - ZPL'
        file_name = "./static/images/ETIQ_DESPACHO.jpg"

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
