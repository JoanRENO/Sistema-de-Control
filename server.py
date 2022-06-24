import werkzeug.exceptions
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import pyodbc
import os
import re
from os import remove
from werkzeug.utils import secure_filename
from waitress import serve
from dataBase.control import Control
from dataBase.lecturaMasiva import LecturaMasiva
from dataBase.despacho import Despacho
from dataBase.AB_ModulosPiezas import ABM
from dataBase.plano import Plano
from dataBase.informes import Informe
from dataBase.reproceso import Reproceso
from dataBase.pallet import Pallet
from dataBase.restos import Resto
from dataBase.produccion import Produccion

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './'

# setings
app.secret_key = "mysecretkey"


# HOME
@app.route('/')
def menu():
    return render_template("menu.html")


# TURNO / PARADA
@app.route("/turno/<string:template>/<string:maquina>", methods=["POST"])
def turno(template, maquina):
    if request.method == 'POST':
        estado = Produccion().consultarEstadoTurno(maquina)
        usuarios = []
        if estado == "0":
            legajo1 = request.form['legajo1']
            usuario = LecturaMasiva().verificar_pin(legajo1)
            usuarios.append(legajo1)
            if usuario is None:
                flash('Error: Legajo ingresado incorrecto')
                return redirect(url_for('control', maquina=maquina))
            for i in range(2, 6):
                print(i)
                if request.values.get('legajo' + str(i)) is not None:
                    legajo = request.form['legajo' + str(i)]
                    print(legajo)
                    usuario = LecturaMasiva().verificar_pin(legajo)
                    print(usuario)
                    if usuario is None:
                        flash('Error: Legajo ingresado incorrecto')
                        return redirect(url_for('control', maquina=maquina))
                    usuarios.append(legajo)
        Produccion().cambiarEstadoTurno(maquina, usuarios)
    return redirect(url_for(template, maquina=maquina))


@app.route("/parada/<string:template>/<string:maquina>/<string:tipo>", methods=["POST"])
def parada(template, maquina, tipo):
    if request.method == 'POST':
        if tipo == '1':
            Produccion().iniciarParada(maquina)
        if tipo == '2':
            observacion = request.form['observacion']
            Produccion().finalizarParada(maquina, observacion)
        return redirect(url_for(template, maquina=maquina))


# CONTROL
@app.route('/control/<string:maquina>')
def control(maquina):
    estado = Produccion().consultarEstadoTurno(maquina)
    if estado == "0":
        botonTurnoStyle = "success"
        botonTurnoTexto = "Inicio Turno"
        botonTurnoDisabled = ""
        botonParadaStyle = "disabled"
        botonParadaTexto = "Parada de Maquina"
        botonInput = "disabled"
        piezas = []
    else:
        opc = Produccion().consultarProceso(maquina)
        if opc == "1":
            botonTurnoDisabled = ""
            botonParadaTexto = "Parada de Maquina"
            botonInput = ""
        else:
            botonTurnoDisabled = "disabled"
            botonParadaTexto = "Parada de Maquina: ACTIVO"
            botonInput = "disabled"
        botonParadaStyle = ""
        botonTurnoStyle = "danger"
        botonTurnoTexto = "Finalizar Turno"
        piezas = Control().getTabla(maquina)
    return render_template("control.html", maquina=maquina, piezas=piezas, botonTurnoStyle=botonTurnoStyle, botonTurnoTexto=botonTurnoTexto,
                           botonTurnoDisabled=botonTurnoDisabled, botonParadaStyle=botonParadaStyle, botonParadaTexto=botonParadaTexto
                           , botonInput=botonInput)


@app.route('/control_escanear/<string:maquina>', methods=['POST'])
def control_escanear(maquina):
    if request.method == 'POST':
        codigo = request.form['cod_escaneado']
        try:
            if Control().verificar_cod(codigo, maquina) == 1:
                flash('El codigo ' + codigo + ' ya fue escaneado', 'warning')
            elif Control().verificar_cod(codigo, maquina) is None:
                flash('El codigo ingresado no existe o la maquina no pertenece a la ruta de la pieza', 'warning')
            else:
                Control().updatePM(codigo, maquina)
        except pyodbc.ProgrammingError:
            flash("Error: el codigo ingresado es incorrecto. Intente nuevamente")
        return redirect(url_for('control', maquina=maquina))

# LECTURA MASIVA
@app.route('/lectura/<string:maquina>', methods=["POST", "GET"])
def lectura(maquina):
    estado = Produccion().consultarEstadoTurno(maquina)
    if estado == "0":
        botonTurnoStyle = "success"
        botonTurnoTexto = "Inicio Turno"
        botonTurnoDisabled = ""
        botonParadaStyle = "disabled"
        botonParadaTexto = "Parada de Maquina"
        botonInput = "disabled"
    else:
        opc = Produccion().consultarProceso(maquina)
        if opc == "1":
            botonTurnoDisabled = ""
            botonParadaTexto = "Parada de Maquina"
            botonInput = ""
        else:
            botonTurnoDisabled = "disabled"
            botonParadaTexto = "Parada de Maquina: ACTIVO"
            botonInput = "disabled"
        botonParadaStyle = ""
        botonTurnoStyle = "danger"
        botonTurnoTexto = "Finalizar Turno"
    return render_template('lectura_masiva.html', maquina=maquina, ops=LecturaMasiva().lista_ops(maquina)
                           , ops_masivo=LecturaMasiva().getTablaLecturaMasiva(maquina),
                           botonTurnoStyle=botonTurnoStyle, botonTurnoTexto=botonTurnoTexto, botonTurnoDisabled=botonTurnoDisabled
                           , botonParadaStyle=botonParadaStyle, botonParadaTexto=botonParadaTexto, botonInput=botonInput)


@app.route('/lectura_masiva/<string:maquina>', methods=['POST'])
def lectura_masiva(maquina):
    try:
        if request.method == 'POST':
            pin = request.form['pin']
            usuario = LecturaMasiva().verificar_pin(pin)
            if usuario is None:
                flash("Error: el PIN ingresado es incorrecto", 'danger')
                return redirect(url_for('lectura', maquina=maquina))
            op = request.form['ops']
            color = request.form['colores']
            espesor = request.form['espesores']
            pieza = request.form['piezas']
            if pieza == "":
                cant = 0
            else:
                cant = request.form['cant']
            piezas = LecturaMasiva().verificar_lectura(op, color, espesor, pieza, maquina, cant)
            if piezas == 1:
                flash("Esta lectura masiva ya se a realizado. OP: " + op + " "
                      "| COLOR: " + color + " | ESPESOR: " + espesor + " | PIEZA: " + pieza,
                      'warning')
                return redirect(url_for('lectura', maquina=maquina))
            LecturaMasiva().updateMasivo(piezas, maquina)
            if pieza == '':
                LecturaMasiva().log_lecturaMasiva(usuario, op, color, espesor, maquina, None, 0)
            else:
                LecturaMasiva().log_lecturaMasiva(usuario, op, color, espesor, maquina, pieza, cant)
            flash("Lectura masiva realizada con exito. \n OP: " + op + " | COLOR: " + color + " | ESPESOR: " + espesor
                  + " | PIEZA: " + pieza)
            return redirect(url_for('lectura', maquina=maquina))
    except pyodbc.DataError:
        flash("Error: Por favor ingrese todos los campos", 'danger')
        return redirect(url_for('lectura', maquina=maquina))

@app.route("/ops", methods=["POST", "GET"])
def ops():
    global OutputArray
    if request.method == 'POST':
        op = request.form['op']
        maquina = request.form['maquina']
        print(maquina)
        print(op)
        OutputArray = LecturaMasiva().lista_colores(op, maquina)
    return jsonify(OutputArray)


@app.route("/colores", methods=["POST", "GET"])
def colores():
    global OutputArray
    if request.method == 'POST':
        color = request.form['color']
        op = request.form['op']
        maquina = request.form['maquina']
        print(color)
        OutputArray = LecturaMasiva().lista_espesores(color, op, maquina)
    return jsonify(OutputArray)


@app.route("/espesores", methods=["POST", "GET"])
def espesores():
    global piezas
    if request.method == 'POST':
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        maquina = request.form['maquina']
        print(espesor)
        piezas = LecturaMasiva().lista_piezas(op, color, espesor, maquina)
    return jsonify(piezas)


@app.route("/espesores_cantidad", methods=["POST", "GET"])
def espesores_cantidad():
    global cantidad
    if request.method == 'POST':
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        maquina = request.form['maquina']
        cantidad = LecturaMasiva().calcular_cant(op, color, espesor, 1, maquina)
    return jsonify(cantidad)


@app.route("/piezas", methods=["POST", "GET"])
def piezas():
    global cantidad
    if request.method == 'POST':
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        pieza = request.form['pieza']
        maquina = request.form['maquina']
        print(espesor + " , " + color + " , " + op + " , " + pieza)
        cantidad = LecturaMasiva().calcular_cant(op, color, espesor, pieza, maquina)
    return jsonify(cantidad)


# INFORME
@app.route('/informe/<string:maquina>', methods=["POST", "GET"])
def informe(maquina):
    try:
        return render_template('informe.html', maquina=maquina,
                           piezas_noleidas=Informe().piezas_noleidas(maquina, request.form['op_informe'], request.form['tipobusqueda']),
                           ids_noleidas=Informe().ids_noleidas(maquina, request.form['op_informe'], request.form['tipobusqueda']))
    except werkzeug.exceptions.BadRequestKeyError:
        return render_template('informe.html', maquina=maquina)


@app.route("/lista_ops_informe", methods=["POST", "GET"])
def lista_ops_informe():
    global OutputArray
    if request.method == 'POST':
        tipo = request.form['tipoBusqueda']
        maquina = request.form['maquina']
        print(tipo)
        OutputArray = Informe().lista_ops(maquina, tipo)
    return jsonify(OutputArray)


@app.route('/informeDiario/<string:maquina>')
def informeDiario(maquina):
    return render_template("informeDiario.html", maquina=maquina, piezas=Informe().getInformeDiarioTabla(maquina),
                           ops=Informe().getInformeDiarioOP(maquina),
                           total=Informe().getInformeDiarioTotal(maquina))


# PRODUCTO TERMINADO
@app.route('/producto_terminado/<string:maquina>')
def producto_terminado(maquina):
    return render_template('producto_terminado.html', maquina=maquina, piezas=Control().getTabla(maquina))


@app.route('/escanear_PT/<string:maquina>', methods=['POST'])
def escanear_PT(maquina):
    if request.method == 'POST':
        codigo = request.form['cod_escaneado']
        try:
            if Control().verificar_cod(codigo, maquina) == 1:
                flash('El ' + codigo + ' ya fue escaneado', 'warning')
                return redirect(url_for('producto_terminado', maquina=maquina))
            elif Control().verificar_cod(codigo, maquina) is None:
                flash('El PR/MO ingresado no existe')
                return redirect(url_for('producto_terminado', maquina=maquina))
            else:
                Control().updatePM(codigo, maquina)
                return redirect(url_for('producto_terminado', maquina=maquina))
        except pyodbc.DataError:
            flash("Error: el PR/MO ingresado es incorrecto. Intente nuevamente")
            return redirect(url_for('producto_terminado', maquina=maquina))


# DESPACHO
@app.route('/despacho')
def despacho():
    return render_template("despacho.html", sos=Despacho().lista_so(0), clientes=Despacho().lista_cf(0))


@app.route("/buscar_cf", methods=["POST", "GET"])
def buscar_cf():
    if request.method == 'POST':
        cf = request.form['op']
        print(cf)
        return jsonify(Despacho().lista_cf(cf))


@app.route("/buscar_so", methods=["POST", "GET"])
def buscar_so():
    if request.method == 'POST':
        so = request.form['color']
        print(so)
        return jsonify(Despacho().lista_so(so))


# Alta y Baja de Piezas/Modulos
@app.route('/AB_ModulosPiezas/<string:ventana>')
def index4(ventana):
    if ventana == "1":
        display1 = ""
        display2 = "display:none;"
        display3 = "display:none;"
        display4 = "display:none;"
        return render_template("index4.html", ops_modulos=ABM().lista_opModulos(), ops_piezas=ABM().lista_opPiezas(),
                               display1=display1, display2=display2, display3=display3, display4=display4, logs=ABM().getLogAB())
    elif ventana == "2":
        display1 = "display:none;"
        display2 = ""
        display3 = "display:none;"
        display4 = "display:none;"
        return render_template("index4.html", ops_modulos=ABM().lista_opModulos(), ops_piezas=ABM().lista_opPiezas(),
                               display1=display1, display2=display2, display3=display3, display4=display4, logs=ABM().getLogAB())
    elif ventana == "4":
        display1 = "display:none;"
        display2 = "display:none;"
        display3 = "display:none;"
        display4 = ""
        return render_template("index4.html", ops_modulos=ABM().lista_opModulos(), ops_piezas=ABM().lista_opPiezas(),
                               display1=display1, display2=display2, display3=display3, display4=display4, logs=ABM().getLogAB())


@app.route('/desglosar_piezas', methods=['POST'])
def desglosar_piezas():
    if request.method == 'POST':
        try:
            archivo = request.files['archivo']
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(archivo.filename)
            ABM().desglose_piezas(archivo.filename)
            print("OPERACION DESGLOSE DE PIEZAS: COMPLETADA")
            flash('OPERACION DESGLOSE DE PIEZAS: COMPLETADA')
            return redirect(url_for('index4', ventana=4))
        except PermissionError:
            print("OPERACION DESGLOSE DE PIEZAS:  CANCELADA")
            flash("Error: No se a cargado ningun archivo", 'danger')
            return redirect(url_for('index4', ventana=4))
        except KeyError:
            archivo = request.files['archivo']
            remove(archivo.filename)
            print("OPERACION DESGLOSE DE PIEZAS:  CANCELADA")
            flash("Error: Archivo equivocado, no cumple con el formato establecido", 'danger')
            return redirect(url_for('index4', ventana=4))


@app.route('/subir_archivo', methods=['POST'])
def subir_archivo():
    if request.method == 'POST':
        try:
            tipo = request.form['tipo_subida']
            archivo = request.files['archivo']
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if tipo == 'baseModulos':
                ABM().Alta_Modulos(archivo.filename)
                print("OPERACION SUBIDA DE DATOS: COMPLETADA")
                flash('Los MODULOS se han subido correctamente')
                return redirect(url_for('index4', ventana=1))
            elif tipo == 'basePiezas':
                ABM().Alta_Piezas(archivo.filename)
                print("OPERACION SUBIDA DE DATOS:  COMPLETADA")
                flash('Las PIEZAS se han subido correctamente')
                return redirect(url_for('index4', ventana=1))
        except PermissionError:
            print("OPERACION SUBIDA DE DATOS:  CANCELADA")
            flash("Error: No se a cargado ningun archivo", 'danger')
            return redirect(url_for('index4', ventana=1))
        except KeyError:
            archivo = request.files['archivo']
            remove(archivo.filename)
            print("OPERACION SUBIDA DE DATOS:  CANCELADA")
            flash("Error: Archivo equivocado, no cumple con el formato establecido", 'danger')
            return redirect(url_for('index4', ventana=1))
        except pyodbc.IntegrityError as error:
            archivo = request.files['archivo']
            tipo = request.form['tipo_subida']
            remove(archivo.filename)
            if tipo == 'basePiezas':
                remove('basePiezasLimpia.xlsx')
            elif tipo == 'baseModulos':
                remove('baseModulosLimpia.xlsx')
                remove('baseModulosDesglosada.xlsx')
            print("OPERACION SUBIDA DE DATOS:  CANCELADA")
            flash(error.args[1] + " | LA OPERACION SE CANCELO, NO SE SUBIO NINGUN DATO", 'warning')
            return redirect(url_for('index4', ventana=1))


@app.route('/baja_modulos', methods=['POST'])
def baja_modulos():
    if request.method == 'POST':
        borrar_todo = request.form['borrar_todo']
        op = request.form['op_modulo']
        if borrar_todo == 'NO':
            cantidad = ABM().getCant("Modulo", op)
            ABM().elimar_Modulos(op)
            ABM().setLogAB("BAJA", "Modulo", op, cantidad)
            print("BAJA MODULOS | OP: " + op)
            flash('Los MODULOS se han borrado correctamente')
            return redirect(url_for('index4', ventana=2))
        elif borrar_todo == 'SI':
            cant_modulos = ABM().getCant("Modulo", op)
            cant_piezas = ABM().getCant("Pieza", op)
            ABM().elimar_Modulos(op)
            ABM().elimar_Piezas(op)
            ABM().setLogAB("BAJA", "Modulo", op, cant_modulos)
            ABM().setLogAB("BAJA", "Pieza", op, cant_piezas)
            print("BAJA MODULOS Y PIEZAS | OP: " + op)
            flash('PIEZAS y MODULOS se han borrado correctamente')
            return redirect(url_for('index4', ventana=2))


@app.route('/baja_piezas', methods=['POST'])
def baja_piezas():
    if request.method == 'POST':
        op = request.form['op_pieza']
        cantidad = ABM().getCant("Pieza", op)
        ABM().elimar_Piezas(op)
        ABM().setLogAB("BAJA", "Pieza", op, cantidad)
        print("BAJA PIEZAS | OP: " + op)
        flash('Las PIEZAS se han borrado correctamente')
        return redirect(url_for('index4', ventana=2))


# Planos
@app.route('/planos/<string:plano>')
def planos(plano):
    return render_template("planos.html", plano=plano, produccion=Plano().produccion_diaria())


@app.route('/leer_plano', methods=['POST'])
def leer_plano():
    if request.method == 'POST':
        plano = request.form['plano']
        print(plano)
        if plano == "":
            return redirect(url_for('planos', plano=0))
        if "/" in plano:
            return redirect(url_for('planos', plano=1))
        return redirect(url_for('planos', plano=plano))


@app.route('/buscar_plano/<string:plano>')
def buscar_plano(plano):
    if plano == "0":
        return "BUSCAR PLANO"
    if len(plano) > 12:
        aux = "/" + plano[:3]
        path = 'E:\COMPARTIDOS\Ing de Producto\Productos - VISTAS Y PLANOS\Desenhos' + aux + '/' + plano + '.pdf'
        if os.path.isfile(path):
            return send_from_directory('E:\COMPARTIDOS\Ing de Producto\Productos - VISTAS Y PLANOS\Desenhos' + aux,
                                       plano + '.pdf')
        else:
            return "PLANO NO ENCONTRADO"
    else:
        path = 'E:\COMPARTIDOS\Ing de Producto\Productos - VISTAS Y PLANOS\Desenhos' + '/' + plano + '.pdf'
        if os.path.isfile(path):
            return send_from_directory('E:\COMPARTIDOS\Ing de Producto\Productos - VISTAS Y PLANOS\Desenhos',
                                       plano + '.pdf')
        else:
            return "PLANO NO ENCONTRADO"


# REPROCESO
@app.route('/reproceso/<string:display>')
def reproceso(display):
    if display == "1":
        display1 = ""
        display2 = "display:None;"
        display3 = "display:None;"
        id = request.args.get('idPieza')
        if id is None:
            return render_template("reproceso.html", display1=display1, display2=display2, display3=display3, check1="checked")
        ruta = Reproceso().infoID(id)
        if id is not None:
            return render_template("reproceso.html", idPieza="IdPieza: " + id + " | RUTA ASIGNADA: " + ruta,
                                   maqs_1=re.split("-", ruta), idP=id,
                                   display1=display1, display2=display2, display3=display3, check1="checked")
    if display == "2":
        display1 = "display:None;"
        display2 = ""
        display3 = "display:None;"
        return render_template("reproceso.html", display1=display1, display2=display2, display3=display3, check2="checked")
    if display == "3":
        display1 = "display:None;"
        display2 = "display:None;"
        display3 = ""
        om = request.args.get('om')
        if om is None:
            return render_template("reproceso.html", display1=display1, display2=display2, display3=display3, check3="checked")
        if om is not None:
            if Reproceso().buscar_om(om) is None:
                flash("Orden Manufactura no encontrada")
                return render_template("reproceso.html", display1="display:None;", display2="display:None;",
                                       display3="",
                                       check3="checked")
            return render_template("reproceso.html", om=om, ordenManu="OrdenManu: " + om,
                               piezas=Reproceso().buscar_om(om), modulo=Reproceso().buscar_om(om)[0]['PT_PRODUCTO']
                                   , display1=display1, display2=display2, display3=display3, check3="checked")
    if display[0] == "4":
        if display[2] == "0":
            flash("Este REPROCESO ya se a generado. ")
        else:
            flash("Por favor ingrese todos los campos")
        if display[1] == "1":
            return render_template("reproceso.html", display1="", display2="display:None;", display3="display:None;",
                                   check1="checked")
        if display[1] == "2":
            return render_template("reproceso.html", display1="display:None;", display2="", display3="display:None;",
                                    check2="checked")
        if display[1] == "3":
            return render_template("reproceso.html", display1="display:None;", display2="display:None;", display3="",
                                   check3="checked")


@app.route('/separaruta', methods=["POST", "GET"])
def separaruta():
    if request.method == 'POST':
        idPieza = request.form['idP']
        maq_select = request.form['maq_1']
        print(idPieza + "----" + maq_select)
        maqs = Reproceso().infoID(idPieza)
        print(maqs)
        maquinas = re.split("-", maqs)
        print(maquinas)
        for x in maquinas:
            if maq_select == x:
                pos = maquinas.index(x)
        data = []
        for x in maquinas:
            data.append(x)
            if maquinas.index(x) >= pos:
                break
        print(data, type(data))
    return jsonify(data)


@app.route("/ops_reproceso", methods=["POST", "GET"])
def ops_reproceso():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        print(maquina)
        OutputArray = Reproceso().lista_ops(maquina)
    return jsonify(OutputArray)


@app.route("/colores_reproceso", methods=["POST", "GET"])
def colores_reproceso():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        op = request.form['op']
        print(maquina, op)
        OutputArray = Reproceso().lista_colores(op, maquina)
    return jsonify(OutputArray)


@app.route("/espesores_reproceso", methods=["POST", "GET"])
def espesores_reproceso():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        op = request.form['op']
        color = request.form['color']
        print(maquina, op, color)
        OutputArray = Reproceso().lista_espesores(op, color, maquina)
    return jsonify(OutputArray)


@app.route("/piezas_reproceso", methods=["POST", "GET"])
def piezas_reproceso():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        print(maquina, op, color, espesor)
        OutputArray = Reproceso().lista_piezas(op, color, espesor, maquina)
    return jsonify(OutputArray)

@app.route("/info_piezas", methods=["POST", "GET"])
def info_piezas():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        pieza = request.form['pieza']
        print(maquina, op, color, espesor, pieza)
        OutputArray = Reproceso().info_piezas(op, color, espesor, maquina, pieza)
    return jsonify(OutputArray)

@app.route("/maquina2", methods=["POST", "GET"])
def maquina2():
    global OutputArray
    if request.method == 'POST':
        maquina = request.form['maquina']
        op = request.form['op']
        color = request.form['color']
        espesor = request.form['espesor']
        pieza = request.form['pieza']
        OutputArray = Reproceso().info_piezas(op, color, espesor, maquina, pieza)
        ruta = OutputArray[0]['RUTA_ASIGNADA']
        maquinas = re.split("-", ruta)
        for x in maquinas:
            if maquina == x:
                pos = maquinas.index(x)
        data = []
        if maquina in ["LP", "LM", "LC"]:
            a = len(maquinas)
            for x in maquinas:
                data.append(x)
                if maquinas.index(x) == (a-2):
                    break
        else:
            for x in maquinas:
                data.append(x)
                if maquinas.index(x) >= pos:
                    break
        return jsonify(data)


@app.route("/ruta_prmo", methods=["POST", "GET"])
def ruta_prmo():
    global OutputArray
    if request.method == 'POST':
        idPieza = request.form['id_prmo']
        ruta = re.split("-",  Reproceso().infoID(idPieza))
        print(ruta)
        return jsonify(ruta)


@app.route("/generar_reproceso/<string:tipo>", methods=["POST", "GET"])
def generar_reproceso(tipo):
    if request.method == 'POST':
        if tipo == "ID":
            print(tipo)
            maq_select = request.form['maq_2']
            maq_detecto = request.form['maq_1']
            causa = request.form['causa1']
            if request.form['maq_1'] != 'Maq' and request.form['maq_2'] != 'Maq' and request.form['idP'] != "":
                ver = Reproceso().verificarReproceso(request.form['idP'])
                if ver == 1:
                    return redirect(url_for('reproceso', display="410"))
                idPieza = request.form['idP']
                info = Reproceso().info_final(idPieza)
                Reproceso().actualizarTabla(info['RUTA_ASIGNADA'], idPieza, maq_detecto, maq_select)
                Reproceso().log_reproceso(idPieza, maq_select, info['PIEZA_DESCRIPCION'], maq_detecto, 1,
                                          info['RUTA_ASIGNADA'], info['OP'], causa)
                Reproceso().generar_barcode(info['idPieza'], info['PIEZA_DESCRIPCION'], info['SO'],
                                            info['PRODUCTO_TERMINADO'], info['OP'], info['RUTA_ASIGNADA'],
                                            info['PIEZA_NOMBREMODOSUSTENTACION'],
                                            info['PIEZA_CODIGORANURA'], info['PIEZA_TAPACANTO_DERECHO'],
                                            info['PIEZA_TAPACANTO_INFERIOR'], info['PIEZA_TAPACANTO_IZQUIERDO'],
                                            info['PIEZA_TAPACANTO_SUPERIOR'], info['PIEZA_CODIGO'], maq_select, maq_detecto, "")
            else:
                return redirect(url_for('reproceso', display="41"))
            Reproceso().imprimirEtiqueta()
            return redirect(url_for('reproceso', display="1"))
        if tipo == "OP":
            print(tipo)
            op = request.form['ops']
            color = request.form['colores']
            espesor = request.form['espesores']
            pieza = request.form['piezas']
            maq_select = request.form['maquina2']
            maq_detecto = request.form['maquina1_1']
            cantidad = request.form['cantidad']
            lado = request.form['lado']
            print(lado)
            causa = request.form['causa2']
            print("Cant: " + cantidad)
            if maq_detecto != 'Maquina' and op != 'Op' and color != 'Color' and espesor != 'Espesor' and pieza != 'Pieza' and maq_select != 'Maq' and cantidad != "":
                ids_op = Reproceso().ids_op(op, color, espesor, maq_detecto, maq_select, pieza, cantidad)
                for x in ids_op:
                    info = Reproceso().info_final(x['idPieza'])
                    Reproceso().actualizarTabla(info['RUTA_ASIGNADA'], info['idPieza'], maq_detecto, maq_select)
                    Reproceso().generar_barcode(info['idPieza'], info['PIEZA_DESCRIPCION'], info['SO'],
                                                info['PRODUCTO_TERMINADO'], info['OP'], info['RUTA_ASIGNADA'],
                                                info['PIEZA_NOMBREMODOSUSTENTACION'],
                                                info['PIEZA_CODIGORANURA'], info['PIEZA_TAPACANTO_DERECHO'],
                                                info['PIEZA_TAPACANTO_INFERIOR'], info['PIEZA_TAPACANTO_IZQUIERDO'],
                                                info['PIEZA_TAPACANTO_SUPERIOR'], info['PIEZA_CODIGO'], maq_select, maq_detecto, lado)
                    Reproceso().imprimirEtiqueta()
                    Reproceso().log_reproceso(info['idPieza'], maq_select, info['PIEZA_DESCRIPCION'], maq_detecto, 1,
                                              info['RUTA_ASIGNADA'], info['OP'], causa)
            else:
                return redirect(url_for('reproceso', display="42"))
            return redirect(url_for('reproceso', display="2"))
        if tipo == "PRMO":
            idprmo = request.form['id_prmo']
            maq_select = request.form['maq_om']
            causa = request.form['causa3']
            if idprmo != "Id" and maq_select != 'Maq':
                ver = Reproceso().verificarReproceso(idprmo)
                if ver == 1:
                    return redirect(url_for('reproceso', display="430"))
                info = Reproceso().info_final(idprmo)
                Reproceso().actualizarTabla(info['RUTA_ASIGNADA'], idprmo, "ARMADO/EMBALADO", maq_select)
                Reproceso().log_reproceso(idprmo, maq_select, info['PIEZA_DESCRIPCION'], "ARMADO/EMBALADO", 1, info['RUTA_ASIGNADA'], info['OP'], causa)
                Reproceso().generar_barcode(info['idPieza'], info['PIEZA_DESCRIPCION'], info['SO'],
                                            info['PRODUCTO_TERMINADO'], info['OP'], info['RUTA_ASIGNADA'],
                                            info['PIEZA_NOMBREMODOSUSTENTACION'],
                                            info['PIEZA_CODIGORANURA'], info['PIEZA_TAPACANTO_DERECHO'],
                                            info['PIEZA_TAPACANTO_INFERIOR'], info['PIEZA_TAPACANTO_IZQUIERDO'],
                                            info['PIEZA_TAPACANTO_SUPERIOR'], info['PIEZA_CODIGO'], maq_select, "LINEA", "")
                Reproceso().imprimirEtiqueta()
            else:
                return redirect(url_for('reproceso', display="43"))
            return redirect(url_for('reproceso', display="3"))


#PALLET
@app.route("/pallet/<string:tipo>", methods=["POST", "GET"])
def pallet(tipo):
    if tipo == "0":
        return render_template('pallet.html', pallets=Pallet().getTablaPallets(),
                               modulos=Pallet().getTablaModulosPallets(), idPallet2=0)
    if tipo == "1":
        Pallet().crearPallet()
        return render_template('pallet.html', pallets=Pallet().getTablaPallets(),
                               modulos=Pallet().getTablaModulosPallets(), idPallet2=0)
    if tipo == "2":
        idPallet = request.values.get('cerrar')
        print(idPallet)
        Pallet().cerrarPallet(idPallet)
        return render_template('pallet.html', pallets=Pallet().getTablaPallets(),
                               modulos=Pallet().getTablaModulosPallets(), idPallet2=0)
    if tipo == "3":
        idPallet = request.values.get('idPallet')
        if idPallet == '':
            flash('Por favor seleccione un pallet')
        else:
            om = request.args.get('cod_escaneado')
            if Pallet().verificarModulo(om) == 1:
                if Pallet().verificarModuloPallet(om) == 0:
                    Pallet().agregarModulo(om, idPallet)
                else:
                    flash('El modulo ya esta cargado en un pallet')
            elif Pallet().verificarModulo(om) == 0:
                flash('El modulo no a sido leido', 'danger')
            else:
                flash('Modulo inexistente', 'danger')
        print(idPallet)
        return render_template('pallet.html', pallets=Pallet().getTablaPallets(),
                               modulos=Pallet().getTablaModulosPallets(), idPallet2=int(idPallet))
    if tipo[0] == "4":
        om = request.values.get('idOM')
        indicador = Pallet().getIndicador(om)
        Pallet().eliminarModulo(om)
        return render_template('pallet.html', pallets=Pallet().getTablaPallets(),
                               modulos=Pallet().getTablaModulosPallets(), idPallet2=indicador)


@app.route("/imprimir_pallet")
def imprimir_pallet():
    return render_template('imprimirPallet.html', pallets=Pallet().getTablaImprimir())


@app.route("/PL/<string:numPallet>/<string:op>")
def PL(numPallet, op):
    tabla = Pallet().getTablaPalletImprimir(numPallet, op)
    acuerdos, ambientes, barcodes, cant = Pallet().obtenerDatos(numPallet, op)
    cantidad = str((cant/14)+1)[0]
    return render_template('PL.html', numPallet=numPallet, tabla=tabla, OP=tabla[0]['OP'],
                           fInicio=tabla[0]['fechaInicio'], fFin=tabla[0]['fechaFin']
                           , acuerdos=acuerdos, ambientes=ambientes, barcodes=barcodes, cantidad=int(cantidad), total=cant)

@app.route('/getTablaPallet', methods=["POST", "GET"])
def getTablaPallet():
    if request.method == 'POST':
        idPallet = request.form['idPallet']
        print(idPallet)
        data = Pallet().getTablaPallet(idPallet)
    return jsonify(data)

#GESTION DE RESTOS
@app.route('/gestion_restos/<string:ventana>', methods=["POST", "GET"])
def gestion_restos(ventana):
    if Resto().verificarOP():
        flash('Optiplanning Activadado, funciones de Alta y Baja desahabilitadas')
        return render_template("gestionRestos.html", display1="display:None;", display2="display:None;", display3="",
                               buttons1="disabled",  buttons2="", backgroundcolor="green")
    if ventana == "1":
        display1 = ""
        display2 = "display:None;"
        display3 = "display:None;"
    elif ventana == "2":
        display1 = "display:None;"
        display2 = ""
        display3 = "display:None;"
    elif ventana == "3":
        display1 = "display:None;"
        display2 = "display:None;"
        display3 = ""
    return render_template("gestionRestos.html", display1=display1, display2=display2, display3=display3,
                           coloresBAJA=Resto().listaColoresBAJA(), coloresALTA=Resto().listaColoresALTA(),
                           buttons1="",  buttons2="disabled", backgroundcolor="red")


@app.route('/alta_resto', methods=["POST"])
def alta_resto():
    try:
        if request.method == 'POST':
            color = request.form['color']
            medidas = request.form['medidas']
            print(color)
            print(medidas)
            Resto().altaResto(color, medidas)
            flash('Ingresado con exito', 'success')
    except IndexError:
        flash('Error: ingrese todas las medidas', 'danger')
    return redirect(url_for('gestion_restos', ventana='1'))


@app.route('/restos_piezas', methods=["POST"])
def restos_piezas():
    if request.method == 'POST':
        color = request.form['color']
        piezas = Resto().listaPiezas(color)
        print(piezas)
        medidas = []
        for x in piezas:
            medidas.append(str(x['alto']) + 'X' + str(x['ancho']))
        print(medidas)
        return jsonify(medidas)


@app.route('/baja_resto', methods=["POST"])
def baja_resto():
    try:
        if request.method == 'POST':
            color = request.form['color_baja']
            medidas = request.form['pieza_baja']
            print(color)
            print(medidas)
            Resto().bajaResto(color, medidas)
            flash('Baja realizado con exito', 'success')
    except IndexError:
        flash('Error: ingrese todas las medidas', 'danger')
    return redirect(url_for('gestion_restos', ventana='2'))


@app.route('/activarOP', methods=["POST"])
def activarOP():
    Resto().activarOP('ACTIVADO')
    return redirect(url_for('gestion_restos', ventana='3'))


@app.route('/desactivarOP', methods=["POST"])
def desactivarOP():
    Resto().activarOP('DESACTIVADO')
    return redirect(url_for('gestion_restos', ventana='3'))



#serve(app, host='0.0.0.0', port=5000, threads=6) # WAITRESS!

# starting the app
if __name__ == "__main__":
    app.run(port=3000, debug=True)
