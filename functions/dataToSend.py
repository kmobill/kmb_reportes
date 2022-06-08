from functions.dataBase import consulta
from datetime import date
from functions.Multipropositos import (
    lastDay,
    stringToDateType,
    numOfDays,
    añadiendo_dias,
    obtener_arreglo_dias,
)


def getDatosLlamada(cooperativa):
    dateI = consulta(
        "select substr(StartedManagement,1,10) as 'fecha de primera operacion' from trx where ID = (Select min(ID) FROM trx where Cooperativa = '{cooperativa}')".format(
            cooperativa=cooperativa
        )
    )
    dateE = consulta(
        "select substr(StartedManagement,1,10) as 'fecha de ultima operacion' from trx where ID = (Select max(ID) FROM trx where Cooperativa = '{cooperativa}')".format(
            cooperativa=cooperativa
        )
    )
    data = consulta(
        "Select count(ID),substr(StartedManagement,1,10) from campaniasinbound.trx where Cooperativa = '{cooperativa}' and StartedManagement BETWEEN  '{dateI}%' AND '{dateE}%' GROUP BY substr(StartedManagement,1,10)".format(
            dateI=dateI[0][0], dateE=dateE[0][0], cooperativa=cooperativa
        )
    )
    num_call = []
    date_call = []
    x_array = []
    i = 0
    for key, value in data:
        num_call.append(key)
        date_call.append(value)
        x_array.append(i)
        i = i + 1
    return {
        "cooperativa": cooperativa,
        "dateI": dateI[0][0],
        "dateE": dateE[0][0],
        "num_call": num_call,
        "date_call": date_call,
        "x_array": x_array,
    }


def eficienciaAgente(agente, cooperativa, mes):
    c1 = "SELECT EstadoLlamada, count(ID) FROM campaniasinbound.trx where Agent = '{agente}' group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
        agente=agente
    )
    auxc1 = consulta(c1)
    todayYear = date.today().year
    todayYear = str(todayYear)
    ld = lastDay(mes)
    dI = stringToDateType("{todayYear}-{M}-01".format(M=mes, todayYear=todayYear))
    dF = stringToDateType(
        "{todayYear}-{M}-{LD}".format(M=mes, LD=ld, todayYear=todayYear)
    )
    # se calcula el numero de llamadas segun el estado y un mes seleccionado
    c1Mes = "SELECT EstadoLlamada, count(ID) FROM campaniasinbound.trx where Agent = '{agente}' and TMSTMP BETWEEN '{di} 00:00:00' AND '{df} 23:59:59' group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
        agente=agente, di=dI, df=dF
    )
    c1MesCooperativa = "SELECT EstadoLlamada, count(ID) FROM campaniasinbound.trx where Agent = '{agente}' and Cooperativa ='{cooperativa}' and TMSTMP BETWEEN '{di} 00:00:00' AND '{df} 23:59:59' group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
        agente=agente, di=dI, df=dF, cooperativa=cooperativa
    )
    cant_dias = numOfDays(dI, dF)

    # INFORMES DE EFICIENCIA DIARIOS

    auxfechainicial = dI.date()
    resultadoC1Diario = []
    resultadoC1CooperativaDiario = []
    resultadoDias = []
    for i in range(cant_dias + 1):
        c1Diario = consulta(
            "SELECT EstadoLlamada,count(ID) FROM campaniasinbound.trx where Agent = '{agente}' and StartedManagement like '{auxfechainicial}%'  group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
                agente=agente, auxfechainicial=auxfechainicial
            )
        )
        c1CooperativaDiario = consulta(
            "SELECT EstadoLlamada,count(ID) FROM campaniasinbound.trx where Agent = '{agente}' and Cooperativa = '{cooperativa}' and StartedManagement like '{auxfechainicial}%'  group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
                agente=agente, auxfechainicial=auxfechainicial, cooperativa=cooperativa
            )
        )
        resultadoC1Diario.append(c1Diario)
        resultadoC1CooperativaDiario.append(c1CooperativaDiario)
        auxfechainicial = añadiendo_dias(auxfechainicial, 1)
        resultadoDias.append(i + 1)

    auxc1Mes = consulta(c1Mes)
    auxc1MesCooperativa = consulta(c1MesCooperativa)
    # se calcula el numero de llamadas segun el estado y una cooperaiva seleccionada
    c1Cooperativa = "SELECT EstadoLlamada, count(ID) FROM campaniasinbound.trx where Agent = '{agente}' and Cooperativa = '{cooperativa}' group by EstadoLlamada ORDER BY COUNT(ID) desc".format(
        agente=agente, cooperativa=cooperativa
    )

    auxc1Cooperativa = consulta(c1Cooperativa)
    aux = []
    eficienciaAgenteGlobal = {}
    eficienciaAgenteGlobal["llamadas_global"] = auxc1
    eficienciaAgenteGlobal["llamadas_mes_" + mes] = auxc1Mes
    eficienciaAgenteGlobal[
        "llamadas_mes_" + mes + "_" + cooperativa
    ] = auxc1MesCooperativa
    eficienciaAgenteGlobal[
        "llamadas_global_cooperativa_" + cooperativa
    ] = auxc1Cooperativa
    eficienciaAgenteGlobal["llamadas_diario_mes_" + mes] = resultadoC1Diario
    eficienciaAgenteGlobal[
        "llamadas_diario_mes_" + mes + "_cooperativa_" + cooperativa
    ] = resultadoC1CooperativaDiario
    eficienciaAgenteGlobal["dias"] = resultadoDias
    eficienciaAgenteGlobal["cooperativa"] = cooperativa
    eficienciaAgenteGlobal["agente"] = agente
    eficienciaAgenteGlobal["mes"] = mes

    r = eficienciaAgenteGlobal
    return r


def generar_detalles_reporte(mes, cooperativa="COOPERATIVA CACPE GUALAQUIZA"):
    lastD = lastDay(mes)
    todayYear = date.today().year
    todayYear = str(todayYear)
    dateI = "{todayYear}-{mes}-01".format(mes=mes, todayYear=todayYear)
    dateE = "{todayYear}-{mes}-{lastDay}".format(
        mes=mes, lastDay=lastD, todayYear=todayYear
    )
    return [
        consulta(
            "SELECT AGENT,substr(tmstmp,1,10) as Fecha, substr(StartedManagement,12,8) as HORA_INICIO, substr(TmStmp,12,8) AS HORA_FIN,  substr(timediff(TMSTMP,StartedManagement),1,8) AS TIEMPO, EstadoLlamada, Identificacion, NombreCliente, CiudadCliente, Convencional, Celular, Correo AS CORREO,EstadoCliente, MotivoLlamada, SubmotivoLlamada, Observaciones FROM campaniasinbound.trx WHERE Cooperativa = '{cooperativa}' AND TMSTMP BETWEEN '{dateI} 00:00:00' AND '{dateE} 23:59:59'".format(
                dateI=dateI, dateE=dateE, cooperativa=cooperativa
            )
        ),
        cooperativa,
    ]


def generar_reportes(mes, cooperativa="COOPERATIVA CACPE GUALAQUIZA"):  # "02"
    tEntrantes = 0
    tContestadas = 0
    tAbandonadas = 0
    pServicio = 0
    pAbandonado = 0
    todayYear = date.today().year
    todayYear = str(todayYear)
    llamadas_entrantes = []
    llamadas_atendidas = []
    llamadas_abandonadas = []
    nivel_servicio = []
    nivel_abandono = []
    ld = lastDay(mes)
    dI = stringToDateType("{todayYear}-{M}-01".format(M=mes, todayYear=todayYear))
    dF = stringToDateType(
        "{todayYear}-{M}-{LD}".format(M=mes, LD=ld, todayYear=todayYear)
    )
    dias = obtener_arreglo_dias(dI, dF)
    for dia in dias:
        auxLlamadaT = consulta(
            "SELECT count(ID) from  trx where Cooperativa = '{cooperativa}' AND StartedManagement like '{d} %'".format(
                d=dia, cooperativa=cooperativa
            )
        )
        llamadas_entrantes.append(auxLlamadaT)
        tEntrantes += int(auxLlamadaT[0][0])

        auxLlamada = consulta(
            "SELECT count(ID) from  trx where EstadoLlamada = 'Atendida' AND Cooperativa = '{cooperativa}' AND StartedManagement like '{d} %'".format(
                d=dia, cooperativa=cooperativa
            )
        )
        llamadas_atendidas.append(auxLlamada)
        tContestadas += int(auxLlamada[0][0])
        if auxLlamadaT[0][0] != 0:
            auxS = (auxLlamada[0][0] / auxLlamadaT[0][0]) * 100
        else:
            auxS = "100"
        nivel_servicio.append(auxS)
        pServicio += int(auxS)
        auxLlamada = consulta(
            "SELECT count(ID) from  trx where EstadoLlamada = 'Abandonada' AND Cooperativa = '{cooperativa}' AND StartedManagement like '{d} %'".format(
                d=dia, cooperativa=cooperativa
            )
        )
        llamadas_abandonadas.append(auxLlamada)
        tAbandonadas += int(auxLlamada[0][0])
        if auxLlamadaT[0][0] != 0:
            auxA = (auxLlamada[0][0] / auxLlamadaT[0][0]) * 100
        else:
            auxA = "0"
        nivel_abandono.append(auxA)
        pAbandonado += int(auxA)

    pAbandonado /= len(dias)
    pServicio /= len(dias)
    return {
        "dias": dias,
        "llamadas_entrantes": llamadas_entrantes,
        "llamadas_atendidas": llamadas_atendidas,
        "llamadas_abandonadas": llamadas_abandonadas,
        "nivel_abandono": nivel_abandono,
        "nivel_servicio": nivel_servicio,
        "TEntrantes": tEntrantes,
        "TContestadas": tContestadas,
        "TAbandonadas": tAbandonadas,
        "PServicio": pServicio,
        "PAbandono": pAbandonado,
    }


""" def generar_reporte(mes, cooperativa="COOPERATIVA CACPE GUALAQUIZA"):
    lastD = lastDay(mes)
    dateI = "2022-{mes}-01".format(mes=mes)
    dateE = "2022-{mes}-{lastDay}".format(mes=mes, lastDay=lastD)

    llamadasTotalesDiarias = consulta(
        "Select count(ID) as 'llamadas totales',substr(StartedManagement,1,10) as 'fecha de llamada' from campaniasinbound.trx where Cooperativa = '{cooperativa}' and StartedManagement BETWEEN  '{dateI} 00:00:00' AND '{dateE} 23:59:59' GROUP BY substr(StartedManagement,1,10)".format(
            cooperativa=cooperativa, dateI=dateI, dateE=dateE
        )
    )
    llamadasAtendidasDiarias = consulta(
        "Select count(ID) as 'llamadas atendidas',substr(StartedManagement,1,10) as 'fecha de llamada atendida' from campaniasinbound.trx where Cooperativa = '{cooperativa}' and EstadoLlamada = 'Atendida' and StartedManagement BETWEEN  '{dateI} 00:00:00' AND '{dateE} 23:59:59' GROUP BY substr(StartedManagement,1,10)".format(
            cooperativa=cooperativa, dateI=dateI, dateE=dateE
        )
    )
    llamadasAbandonadasDiarias = consulta(
        "Select count(ID) as 'llamadas Abandondas',substr(StartedManagement,1,10) as 'fecha de llamada abandonada' from campaniasinbound.trx where Cooperativa = '{cooperativa}' and EstadoLlamada = 'Abandonada' and StartedManagement BETWEEN  '{dateI} 00:00:00' AND '{dateE} 23:59:59' GROUP BY substr(StartedManagement,1,10)".format(
            cooperativa=cooperativa, dateI=dateI, dateE=dateE
        )
    )
    llamadasAbandonadasTotales = consulta(
        "Select count(ID) as 'total de llamadas Abandonadas'  from campaniasinbound.trx where Cooperativa = '{cooperativa}' and EstadoLlamada = 'Abandonada' and StartedManagement BETWEEN  '{dateI} 00:00:00' AND '{dateE} 23:59:59'".format(
            cooperativa=cooperativa, dateI=dateI, dateE=dateE
        )
    )
    llamadasAtendidasTotales = consulta(
        "Select count(ID) as 'total de llamadas atendidas'  from campaniasinbound.trx where Cooperativa = '{cooperativa}' and EstadoLlamada = 'Atendida' and StartedManagement BETWEEN  '{dateI} 00:00:00' AND '{dateE} 23:59:59'".format(
            cooperativa=cooperativa, dateI=dateI, dateE=dateE
        )
    )

    return {
        "llamadasTotalesDiarias": llamadasTotalesDiarias,
        "llamadasAtendidasDiarias": llamadasAtendidasDiarias,
        "llamadasAbandonadasDiarias": llamadasAbandonadasDiarias,
        "llamadasAbandonadasTotales": llamadasAbandonadasTotales[0][0],
        "llamadasAtendidasTotales": llamadasAtendidasTotales[0][0],
    } """


def dataForDashboard(options, data):
    if options["totalOrCooperativaSelection"] == "Cooperativa":
        # consultas por Cooperativa
        if options["period"] == "Anual":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where  Cooperativa ='{cooperativa}' and Agent!='' and StartedManagement like '{año}%' group by Agent,EstadoLlamada order by Agent".format(
                año=data["año"], cooperativa=data["cooperativa"]
            )
        if options["period"] == "Mensual":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where  Cooperativa ='{cooperativa}' and Agent!='' and StartedManagement like '{año}-{mes}-%' group by Agent,EstadoLlamada order by Agent".format(
                año=data["año"], mes=data["mes"], cooperativa=data["cooperativa"]
            )
        if options["period"] == "Total":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where  Cooperativa ='{cooperativa}' and Agent!='' group by Agent,EstadoLlamada order by Agent".format(
                cooperativa=data["cooperativa"]
            )
    elif options["totalOrCooperativaSelection"] == "Total":
        # consultas TOTALES
        if options["period"] == "Anual":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where Agent!='' and StartedManagement like '{año}%' group by Agent,EstadoLlamada order by Agent".format(
                año=data["año"],
            )
        if options["period"] == "Mensual":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where Agent!='' and StartedManagement like '{año}-{mes}-%' group by Agent,EstadoLlamada order by Agent".format(
                año=data["año"],
                mes=data["mes"],
            )
        if options["period"] == "Total":
            consulta1 = "Select Agent,EstadoLlamada,count(ID)from campaniasinbound.trx where Agent!='' group by Agent,EstadoLlamada order by Agent"

    return consulta(consulta1)
