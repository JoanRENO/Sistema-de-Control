#from dataBase.control import Control

#Control().imprimir_etiqueta('PR/MO/3647388/1')

from dataBase.reproceso import Reproceso

info = Reproceso().info_final(2024007)

Reproceso().generar_barcode(info['idPieza'], info['PIEZA_DESCRIPCION'], info['SO'],
                                            info['PRODUCTO_TERMINADO'], info['OP'], info['RUTA_ASIGNADA'],
                                            info['PIEZA_NOMBREMODOSUSTENTACION'],
                                            info['PIEZA_CODIGORANURA'], info['PIEZA_TAPACANTO_DERECHO'],
                                            info['PIEZA_TAPACANTO_INFERIOR'], info['PIEZA_TAPACANTO_IZQUIERDO'],
                                            info['PIEZA_TAPACANTO_SUPERIOR'], info['PIEZA_CODIGO'], 'CPT', 'CPT', "")
Reproceso().imprimirEtiqueta()
