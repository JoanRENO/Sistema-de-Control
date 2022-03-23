from .connection import DataBase
from .helpers import fecha
import code128

class Pallet(DataBase):
    def getTablaPallets(self):
        self.cursor.execute("SELECT * FROM " + DataBase.Tablas.pallets +" WHERE estado = 'ABIERTO'")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getTablaModulosPallets(self):
        self.cursor.execute("SELECT mp.idModulo, mp.idOrdenManufactura, mp.idPallet, mp.PT_PRODUCTO, p.estado FROM "
                            + DataBase.Tablas.modulosPallets + " mp INNER JOIN " + DataBase.Tablas.pallets +
                            " p ON p.idPallet = mp.idPallet WHERE estado = 'ABIERTO'")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def crearPallet(self):
        self.cursor.execute("INSERT INTO " + DataBase.Tablas.pallets + " (idPallet, fechaInicio, estado) "
                            "VALUES ((SELECT MAX(idPallet+1) FROM " + DataBase.Tablas.pallets + "), ?, 'ABIERTO')", fecha())
        self.cursor.commit()

    def cerrarPallet(self, idPallet):
        self.cursor.execute("UPDATE " + DataBase.Tablas.pallets + " SET fechaFin = ?, estado = 'CERRADO' WHERE idPallet = ?",
                            fecha(), idPallet)
        self.cursor.commit()

    def verificarModulo(self, OM):
        self.cursor.execute("SELECT (CASE WHEN lecturaHorno >= 1 THEN 1 ELSE 0 END) FROM " + DataBase.Tablas.baseModulos +
                            " WHERE idOrdenManufactura = ?", OM)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
        return data

    def verificarModuloPallet(self, OM):
        self.cursor.execute("SELECT idOrdenManufactura FROM " + DataBase.Tablas.modulosPallets +
                            " WHERE idOrdenManufactura = ?", OM)
        data = self.cursor.fetchone()
        self.close()
        if data is not None:
            data = data[0]
            return data
        else:
            return 0

    def agregarModulo(self, OM, idPallet):
        self.verificarAcuerdo(idPallet, OM)
        self.cursor.execute("SELECT idModulo, idOrdenManuFactura, PT_PRODUCTO, SO FROM " + DataBase.Tablas.baseModulos +
                            " WHERE idOrdenManufactura = ? ", OM)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        for x in OutputArray:
            self.cursor.execute("INSERT INTO " + DataBase.Tablas.modulosPallets + " (idModulo, idPallet, idOrdenManuFactura, PT_PRODUCTO, SO, fecha) "
                                "VALUES (?, ?, ?, ?, ?, ?)", x['idModulo'], idPallet, OM, x['PT_PRODUCTO'], x['SO'], fecha())
            self.cursor.commit()

    def eliminarModulo(self, OM):
        self.cursor.execute("DELETE FROM " + DataBase.Tablas.modulosPallets + " WHERE idOrdenManufactura = ?", OM)
        self.cursor.commit()
        self.close()

    def getTablaImprimir(self):
        self.cursor.execute("""
        SELECT TOP 10 p.idPallet
      ,fechaInicio
      ,fechaFin
      ,estado
	  ,OP
	  , COUNT(p.idPallet) AS CANT_MODULOS
      FROM """ + DataBase.Tablas.pallets + """ p INNER JOIN """ + DataBase.Tablas.modulosPallets + """ mp ON p.idPallet = mp.idPallet 
      WHERE estado = 'CERRADO' 
      GROUP BY P.idPallet, P.fechaInicio, P.fechaFin, P.estado, OP
      ORDER BY fechaFin DESC
        """)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def getTablaPalletImprimir(self, numPallet, OP):
        self.cursor.execute("""
        SELECT SUBSTRING(mp.idOrdenManufactura, 0,14) as om,
		COUNT(SUBSTRING(mp.idOrdenManufactura, 0,14)) as cant 
      ,mp.[idPallet]
      ,mp.[PT_PRODUCTO]
      ,mp.[SO]
      ,p.[OP]
	  ,p.fechaInicio
	  ,p.fechaFin
  FROM """ + DataBase.Tablas.modulosPallets + """ mp INNER JOIN """ + DataBase.Tablas.pallets + """ p ON mp.idPallet = p.idPallet 
  WHERE mp.idPallet = ? AND OP = ?
  GROUP BY SUBSTRING(mp.idOrdenManufactura, 0,14), mp.idPallet,PT_PRODUCTO, SO, OP, p.fechaInicio, p.fechaFin
  ORDER BY SO, PT_PRODUCTO
        """, numPallet, OP)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        return OutputArray

    def obtenerDatos(self, numPallet, OP):
        tabla = self.getTablaPalletImprimir(numPallet, OP)
        acuerdos = []
        ambientes = []
        barcodes = []
        i = 0
        for t in tabla:
            i = i + 1
            so = str(t['SO'])
            acuerdo = so[:so.find(' ')]
            ambiente = so[so.find('-') + 1:]
            acuerdos.append(acuerdo)
            ambientes.append(ambiente)
            aux = code128.image(t['om'])
            aux2 = aux.resize((460, 100))
            ruta = 'static/images/barcodePRMO' + str(i) + '.png'
            aux2.save(ruta)
            barcodes.append(ruta[14:])
        return acuerdos, ambientes, barcodes, i

    def verificarAcuerdo(self, idPallet, om):
        self.cursor.execute("SELECT COUNT(idModulo) FROM " + DataBase.Tablas.modulosPallets + " WHERE idPallet = ?"
                            , idPallet)
        cant = self.cursor.fetchone()[0]
        if cant == 0:
            self.cursor.execute("SELECT SO, OP FROM " + DataBase.Tablas.baseModulos + " WHERE idOrdenManufactura = ?"
                                , om)
            aux = self.cursor.fetchone()
            so = aux[0]
            acuerdo = so[:so.find(' ')]
            op = aux[1]
            self.cursor.execute("UPDATE " + DataBase.Tablas.pallets + " SET acuerdo = ?, op = ? WHERE idPallet = ?",
                                acuerdo, op, idPallet)
            self.cursor.commit()

    def getIndicador(self, idPieza):
        if "pr/mo" in str(idPieza).lower():
            print(idPieza)
            self.cursor.execute("SELECT idPallet FROM " + DataBase.Tablas.modulosPallets + " WHERE idOrdenManufactura"
                                " = ? ", idPieza)
            idPieza = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(idPallet) as indicador FROM " + DataBase.Tablas.pallets +
                            " WHERE estado = 'ABIERTO' AND idPallet <= ?", idPieza)
        indicador = self.cursor.fetchone()[0]
        self.close()
        return indicador






