import mysql.connector
from mysql.connector import Error

credentials = {
    "host": "172.19.10.78",
    "user": "kimobill",
    "password": "sIst2m1s2020",
    "database": "campaniasinbound",
    "port": "3306",
}

def formatear_arreglo(arreglo):

    result_final = []
    for res in arreglo:
        result_final.append(res[0])
    return result_final


def consulta(operation):
    try:
        connection = mysql.connector.connect(
            host=credentials["host"],
            user=credentials["user"],
            password=credentials["password"],
            database=credentials["database"],
            port=credentials["port"],
        )
        if connection.is_connected():
            db_Info = connection.get_server_info()
    except Error as e:
        print("Error al conectarse a MySQL", e)
    cursor = connection.cursor()
    cursor.execute(operation)
    result = cursor.fetchall()
    if connection.is_connected():
        connection.close()
        cursor.close()
    return result


def consultaOneRow(operation):
    try:
        connection = mysql.connector.connect(
            host="172.19.10.78",
            user="kimobill",
            password="sIst2m1s2020",
            database="campaniasinbound",
            port="3306",
        )
        if connection.is_connected():
            db_Info = connection.get_server_info()
    except Error as e:
        print("Error al conectarse a MySQL", e)
    cursor = connection.cursor()
    cursor.execute(operation)
    result = cursor.fetchall()
    resulTotal = formatear_arreglo(result)
    if connection.is_connected():
        connection.close()
        cursor.close()
    return resulTotal
