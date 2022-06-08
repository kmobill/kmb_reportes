import pandas as pd
from sklearn import linear_model
import numpy as np
from sklearn.metrics import r2_score

from functions.Multipropositos import numOfDays,stringToDateType

def regresion_lineal(datos):
    dfy = pd.DataFrame(datos["num_call"])
    dfx = pd.DataFrame(datos["x_array"])
    x = dfx[0]
    y = dfy[0]
    regr = linear_model.LinearRegression()
    X = x[:, np.newaxis]
    regr.fit(X, y)
    regr.coef_
    m = regr.coef_[0]
    b = regr.intercept_
    y_p = m * X + b
    r2_score(y,y_p)
    return {"m": m, "b": b}

def predecir(dateI, dateF, dateBase, coeficientes):
    if "m" in coeficientes and "b" in coeficientes:
        auxCoeficientes = coeficientes
        cant_dias = numOfDays(stringToDateType(dateI), stringToDateType(dateF))
        x_init = numOfDays(stringToDateType(dateBase), stringToDateType(dateI))
        x_end = x_init + cant_dias
        y_total = []
        for i in range(x_init, x_end + 1):
            y_aux = auxCoeficientes["m"] * i + auxCoeficientes["b"]
            y_total.append(y_aux)
        return {"resultados": y_total}
    return None