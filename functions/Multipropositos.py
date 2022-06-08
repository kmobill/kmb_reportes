from datetime import datetime, date, timedelta
from functions.dataBase import consulta

def numOfDays(date1, date2):  # recibe tipo date de datetime
    return (date2 - date1).days

def stringToDateType(fecha):  # recibe strings
    date_time_str = fecha
    date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d")
    return date_time_obj

def formatear_arreglo(arreglo):
    result_final = []
    for res in arreglo:
        result_final.append(res[0])
    return result_final

def añadiendo_dias(
    date, number_days
):  # recibe tipo date de datetime y el numero de dias en int
    return date + timedelta(days=number_days)


def restando_dias(
    date, number_days
):  # recibe tipo date de datetime y el numero de dias en int
    return date - timedelta(days=number_days)

def obtener_arreglo_dias(dateI, dateE):  # recibe dos fechas del tipo date
    auxD1 = dateI
    auxD2 = dateE
    date_array = []
    auxD = auxD1
    for i in range(numOfDays(auxD1, auxD2) + 1):
        date_array.append(auxD.strftime("%Y-%m-%d"))
        auxD = añadiendo_dias(auxD, 1)
    return date_array

def lastDay(month):
    todayYear = date.today().year
    todayYear = str(todayYear)
    if month != "-1":
        lastday = consulta(
            "SELECT substr(LAST_DAY('{year}-{M}-01'),9,10)".format(
                M=month, year=todayYear
            )
        )
        return lastday[0][0]
    return "-1"