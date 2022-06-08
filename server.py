from flask import Flask, jsonify, render_template, request, Response
import json

from functions.cryptography import encryption, decryption
from functions.generateKeys import read_private, read_public
from functions.dataBase import consulta, consultaOneRow
from functions.Analisis import regresion_lineal,predecir
from functions.Multipropositos import obtener_arreglo_dias,lastDay,formatear_arreglo,stringToDateType
from functions.dataToSend import dataForDashboard,generar_detalles_reporte,getDatosLlamada,generar_reportes,eficienciaAgente

#functions to encrypt
from functions.cryptography import encryption,decryption
from functions.generateKeys import read_private,read_public

# variables para dashboard
selectedCooperativaDashboard = {}
selectedAgentDashboard = {}
selectedMonthDashboard = {}

############aplicacion flask#############

app = Flask(
    __name__, static_folder="./build/static", template_folder="./build"
)  # cuando se necesite cargar desde flask las templates de REACT


@app.route("/")
def index():
    return render_template("index.html")


# PARA QUE TODAS LAS RUTAS SE REDIRIJAN A index.html
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


##############RUTAS PARA GENERAR LA REGRESION Y PREDECIR#############
@app.route("/api/regresion", methods=["POST"])
def data_llamadas():
    if request.method == "POST":
        request_data = json.loads(request.data)
        cooperativa = request_data.get("cooperativa", False)
        cooperativas = consultaOneRow(
            "Select distinct (Cooperativa) FROM campaniasinbound.trx"
        )
        if cooperativa == False:
            return jsonify("No se encontro una cooperativa")
        if len(cooperativa) == 0:
            return jsonify("la cooperativa no puede estar vacia")
        if (
            cooperativa in cooperativas
        ):  # verifica que la cooperativa existe para no ejecutar el analisis en vano
            result = getDatosLlamada(cooperativa)
            result["coeficientes"] = regresion_lineal(result)
            return jsonify(result=result)
        return jsonify("La cooperativa ingresada no existe en la BD")


@app.route("/api/predecir", methods=["POST"])
def data_predecir():
    if request.method == "POST":
        request_data = json.loads(request.data)
        dateBase = request_data.get("dateBase", False)
        dateI = request_data.get("dateI", False)
        dateE = request_data.get("dateE", False)
        coeficientes = request_data.get("coeficientes", False)
        if (
            dateBase == False
            and dateI == False
            and dateE == False
            and coeficientes == False
        ):
            return jsonify("Uno de los datos no se han encontrado")

        result = predecir(dateI, dateE, dateBase, coeficientes)
        if result == None:
            return jsonify("Coeficientes no encontrados")
        result["dates_array"] = obtener_arreglo_dias(
            stringToDateType(dateI), stringToDateType(dateE)
        )
        return jsonify(result)


##########################RUTAS PARA CARGAR LOS DATOS EN VARIABLES GLOBALES ############
# SE DEBE CAMBIAR EL METODO PARA NO USAR VARIABLES GLOBALES
@app.route("/api/selectedAgent", methods=["POST"])
def selectedAgent():
    global selectedAgentDashboard
    if request.method == "POST":
        selectedAgent = json.loads(request.data)
        selectedAgentDashboard = selectedAgent["data"]
        return jsonify(Agent=selectedAgent)


@app.route("/api/selectedMonthDashboard", methods=["POST"])
def selectedMonthDashboard():
    global selectedMonthDashboard
    if request.method == "POST":
        request_data_date = json.loads(request.data)
        selectedMonthDashboard = request_data_date["mes"]
        return jsonify(MonthDashboard=selectedMonthDashboard)


@app.route("/api/selectedCooperativaDashboard", methods=["POST"])
def selectedCooperativaDashboard():
    global selectedCooperativaDashboard
    if request.method == "POST":
        request_data = json.loads(request.data)
        selectedCooperativaDashboard = request_data["data"]
        return jsonify(CooperativaDashboard=selectedCooperativaDashboard)


@app.route("/api/selectedMonth", methods=["POST", "GET"])
def selectedMonth():
    global selectedMonth_global
    if request.method == "POST":
        request_data_date = json.loads(request.data)
        selectedMonth_global = request_data_date["mes"]
    return {
        "mes": str(selectedMonth_global),
        "ult_dia": str(lastDay(selectedMonth_global)),
    }


########################RUTAS DE EJEMPLO#######################
@app.route("/api/encrypt_decrypt", methods=["POST"])
def example_encrypt_decrypt():
    if request.method == "POST":
        request_data = json.loads(request.data)
        user = request_data.get("user", False)
        password = request_data.get("password", False)
        if user == False or password == False:
            return jsonify("falta un campo")
        cypher_text = encryption(user.encode("utf-8"), read_public())
        print("cifrado:", cypher_text.decode("utf-8"))
        return jsonify(
            encryption=cypher_text.decode("utf-8"),
            descrytion=(decryption(cypher_text, read_private())).decode("utf-8"),
        )


#################METODO PARA LA VERIFICACION########################
@app.route("/api/verification", methods=["POST"])
def userData():
    global selectedUser
    if request.method == "POST":
        request_data = json.loads(request.data)
        selectedUser = request_data.get("user",False)
        selectedPassword = request_data.get("password",False)
        # Password = consulta("Select Id from cck where IdUser ='{user}'".format(user = selectedUser[0]))

        if(selectedUser==False or selectedPassword ==False):
            return jsonify(verificacion = False)
            
        print(selectedPassword)
        print(selectedUser)

        if (selectedPassword == "admin") & (selectedUser == "admin"):
            # return jsonify(verificacion=True,status = "admin")
            return jsonify(verificacion=True, status=1)
        if (selectedPassword == "client_user") & (selectedUser == "client_user"):
            # return jsonify(verificacion=True,status = "client")
            return jsonify(verificacion=True, status=2)
        if (selectedPassword == "operator_user") & (selectedUser == "operator_user"):
            # return jsonify(verificacion=True,status = "operator")
            return jsonify(verificacion=True, status=3)
        
        password_encryption =  encryption(selectedPassword.encode("utf-8"), read_public())
        user_encryption = encryption(selectedUser.encode("utf-8"), read_public())

        """ dataUsuario = consulta(
            "Select Password,UserGroup from cck.user where Id ='{USER}'".format(
                USER=user_encryption
            )
        ) 
        dataUsuario[0] = dataUsuario[0].decode("utf-8")
        """
        #dataUsuario = [[encryption(selectedPassword.encode("utf-8"), read_public())],[1]]
        dataUsuario = [[encryption(selectedPassword.encode("utf-8"), read_public())]]
        print(dataUsuario)
        if isinstance(dataUsuario,list):
            if(len(dataUsuario) > 0):
                if(len(dataUsuario) == 2):   
                    [dataPassword,dataUserGroup] = dataUsuario
                    if(decryption(dataPassword[0],read_private()) == selectedPassword.encode("utf-8")):
                        return jsonify(verificacion=True , status =dataUserGroup[0])
        return jsonify(verificacion=False)


################################RUTAS PARA LOS DATOS DE LOS SELECTS##################
@app.route("/api/agentes")
def agents():
    agentes = consulta(
        "Select distinct (Agent) FROM campaniasinbound.trx where StartedManagement like '2022-%' group by Agent  order by count(ID) desc"
    )
    return jsonify(agentes)


@app.route("/api/años")
def getAños():
    c1 = "select distinct(substr(tmstmp,1,4)) from campaniasinbound.trx where tmstmp not like '0000%'"
    años = consulta(c1)
    return jsonify(formatear_arreglo(años))


@app.route("/api/cooperativas")
def cooperativas():
    cooperativas = consulta("Select distinct (Cooperativa) FROM campaniasinbound.trx")
    return jsonify(formatear_arreglo(cooperativas))


#################### PARA GENERAR LOS REPORTES #####################
@app.route("/api/detalles_reporte", methods=["POST"])
def detalles_reporte():
    if request.method == "POST":
        request_data = json.loads(request.data)
        cooperativa = request_data.get("cooperativa", False)
        mes = request_data.get("mes", False)
        if cooperativa == False or mes == False:
            return jsonify("falta un campo")
        if cooperativa == "":
            return jsonify(generar_detalles_reporte(mes))
        return jsonify(generar_detalles_reporte(mes, cooperativa))


@app.route("/api/reporte_diario", methods=["POST"])
def reporte_diario():
    if request.method == "POST":
        request_data = json.loads(request.data)
        cooperativa = request_data.get("cooperativa", False)
        mes = request_data.get("mes", False)
        if cooperativa == False or mes == False:
            return jsonify("falta un campo")
        if cooperativa == "":
            return jsonify(generar_reportes(mes))
        return jsonify(generar_reportes(mes, cooperativa))


##################PARA GENERAR LOS DASHBOARD####################
# USO DE VARIABLES GLOBALES
@app.route("/api/dataDashboard")
def dataDashboard():
    eficienciaAgenteGlobal = eficienciaAgente(
        selectedAgentDashboard, selectedCooperativaDashboard, selectedMonthDashboard
    )
    return jsonify(data=eficienciaAgenteGlobal)


@app.route("/api/Dashboard2", methods=["POST"])
def dashboard2():
    if request.method == "POST":
        request_data = json.loads(request.data)
        options = request_data.get("options", False)
        data = request_data.get("data", False)
        if options == False:
            if data == False:
                result = "data and options not found"
            else:
                result = "options not found"
        else:
            if data == False:
                result = "data not found"
            else:
                result = json.dumps(dataForDashboard(options, data))
        return Response(result, status=201, mimetype="application/json")


if __name__ == "__main__":
    app.run()
