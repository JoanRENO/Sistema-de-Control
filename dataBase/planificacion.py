from .connection import DataBase
from .helpers import fecha


class Planificacion(DataBase):
    def reportePlanificacion(self, maquina):
        print("PASO 1: ")
        self.cursor.execute("""
        SELECT [Programa]
            ,[bloque]
            ,[Maquina]
            ,[CantProgramado]
            ,[CantidadProcesada]
            ,[CantDeuda]
            ,[PorcCump]
            ,[Reproceso]
            ,[InicioPlanificado]
            ,[InicioReal]
            ,[FinalTeorico]
            ,[FinalReal]
            ,[TiempoSTD_Dias]
            ,DATEDIFF(day, InicioPlanificado, InicioReal) as DifInicio
            ,DATEDIFF(day, FinalTeorico, FinalReal) as DifFin
        FROM [PRODUCCION_PLANTA].[dbo].PlanificacionReporte""" + maquina + " WHERE CantDeuda > 0 OR CantDeuda IS NULL  ORDER BY Programa, bloque")
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print("PASO 1: FIN")
        return OutputArray

    def reportePlaMaqEsp(self, maquina):
        print("PASO 3 : INICIO")
        self.cursor.execute("""
              SELECT [Programa]
              ,[bloque]
              ,rom.Maquina
              ,rom.OP
              ,[CantProgramado]
              ,[CantidadProcesada]
              ,[Deuda]
              ,CONVERT(varchar, (CantidadProcesada * 100 / CantProgramado)) + '%' as PorcCumpl
              ,[PIEZA_NOMBREMATERIAL]
              ,[PIEZA_PROFUNDO]
              ,[PIEZA_NOMBRECOLOR]
              ,[Reproceso]
              ,[id]
			  ,pn.Descripcion as Nota
          FROM (
		  SELECT Programa, bloque, Maquina, OP, COUNT(idPieza) AS CantProgramado, SUM(lectura) AS CantidadProcesada, 
			SUM(CASE WHEN lectura >= 1 THEN 0 ELSE 1 END) AS Deuda, PIEZA_NOMBREMATERIAL, PIEZA_PROFUNDO, PIEZA_NOMBRECOLOR
			, SUM(Reproceso) AS Reproceso, 
			CAST(Programa AS varchar) + '-' + CAST(bloque AS varchar) + '-' + Maquina AS id
			FROM            dbo.TableroBase_""" + maquina + """
			GROUP BY Maquina, Programa, bloque, OP, PIEZA_NOMBREMATERIAL, PIEZA_PROFUNDO, PIEZA_NOMBRECOLOR
		  ) as rom
		  LEFT JOIN PRODUCCION_PLANTA.dbo.PlanificacionNotas pn ON pn.OP = rom.OP AND pn.Maquina = rom.Maquina
		  AND pn.Pieza = CONCAT(rom.PIEZA_NOMBREMATERIAL, ' ',rom.PIEZA_PROFUNDO, ' ', rom.PIEZA_NOMBRECOLOR)
          WHERE Programa IS NOT NULL AND bloque IS NOT NULL
                """)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print("PASO 3: FIN")
        return OutputArray

    def reportePlaMaqPiezas(self, maquina):
        print("PASO 4 : INICIO")
        self.cursor.execute("""
                    SELECT [Programa]
              ,[bloque]
              ,rom.Maquina
              ,rom.OP
              ,rom.RUTA_ASIGNADA
              ,[CantProgramado]
              ,[CantidadProcesada]
              ,[Deuda]
              ,[PIEZA_NOMBREMATERIAL]
              ,[PIEZA_PROFUNDO]
              ,[PIEZA_NOMBRECOLOR]
			  ,PIEZA_DESCRIPCION
              ,[Reproceso]
              ,[id]
          FROM (
		  SELECT Programa, bloque, Maquina, OP, RUTA_ASIGNADA, COUNT(idPieza) AS CantProgramado, SUM(lectura) AS CantidadProcesada, 
			SUM(CASE WHEN lectura >= 1 THEN 0 ELSE 1 END) AS Deuda, PIEZA_NOMBREMATERIAL, PIEZA_PROFUNDO, PIEZA_NOMBRECOLOR,
			PIEZA_DESCRIPCION, SUM(Reproceso) AS Reproceso, 
			CAST(Programa AS varchar) + '-' + CAST(bloque AS varchar) + '-' + Maquina AS id
			FROM            dbo.TableroBase_""" + maquina + """
			WHERE Programa IS NOT NULL AND bloque IS NOT NULL
			GROUP BY Maquina, Programa, bloque, OP, RUTA_ASIGNADA, PIEZA_NOMBREMATERIAL, PIEZA_PROFUNDO, PIEZA_NOMBRECOLOR, PIEZA_DESCRIPCION
		  ) as rom
          WHERE Deuda >= 1
          ORDER BY PIEZA_DESCRIPCION      
                """)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print("PASO 4: FIN")
        return OutputArray

    def reportePlaMaqOPs(self, maquina):
        print("PASO 2: INICIO")
        self.cursor.execute("""
                SELECT [Programa]
              ,[bloque]
              ,rom.Maquina
              ,rom.OP
              ,SUM(CantProgramado) as CantProgramado
              ,SUM(CantidadProcesada) as CantidadProcesada
              ,SUM(Deuda) as Deuda
              ,SUM(Reproceso) as Reproceso
              ,CONVERT(varchar, (SUM(CantidadProcesada) * 100 / SUM(CantProgramado))) + '%' as PorcCumpl
			  ,pn.Descripcion as Nota
          FROM (
				SELECT Programa, bloque, Maquina, OP, COUNT(idPieza) AS CantProgramado, SUM(lectura) AS CantidadProcesada, 
			SUM(CASE WHEN lectura >= 1 THEN 0 ELSE 1 END) AS Deuda, PIEZA_DESCRIPCION, SUM(Reproceso) AS Reproceso, 
			CAST(Programa AS varchar) + '-' + CAST(bloque AS varchar) + '-' + Maquina AS id
			FROM            dbo.TableroBase_""" + maquina + """
			GROUP BY Programa, OP, PIEZA_DESCRIPCION, Maquina, bloque
		  ) rom
		  LEFT JOIN PRODUCCION_PLANTA.dbo.PlanificacionNotas pn ON pn.OP = rom.OP AND pn.Maquina = rom.Maquina AND pn.Pieza IS NULL
          WHERE Programa IS NOT NULL AND bloque IS NOT NULL
          GROUP BY Programa, bloque, rom.Maquina, rom.OP, pn.Descripcion
          HAVING SUM(Deuda) > 0
          ORDER BY Programa, bloque, rom.Maquina, rom.OP
                """)
        records = self.cursor.fetchall()
        OutputArray = []
        columnNames = [column[0] for column in self.cursor.description]
        for record in records:
            OutputArray.append(dict(zip(columnNames, record)))
        self.close()
        print("PASO 2: FIN")
        return OutputArray

    def insertarNota(self, maquina, op, pieza, desc):
        self.cursor.execute("""
        INSERT INTO [dbo].[PlanificacionNotas]
           ([OP]
           ,[Pieza]
           ,[Descripcion]
           ,[Maquina])
        VALUES
           (?,?,?,?)
        """, op, pieza, desc, maquina)
        self.cursor.commit()
        self.close()

    def updateNota(self, maquina, op, pieza, desc):
        if pieza is None:
            self.cursor.execute("""
            UPDATE [dbo].[PlanificacionNotas] SET Descripcion = ? WHERE OP = ? AND maquina = ? AND PIEZA IS NULL
            """, desc, op, maquina)
        else:
            self.cursor.execute("""
            UPDATE [dbo].[PlanificacionNotas] SET Descripcion = ? WHERE OP = ? AND maquina = ? AND PIEZA = ?
            """, desc, op, maquina, pieza)
        self.cursor.commit()
        self.close()
