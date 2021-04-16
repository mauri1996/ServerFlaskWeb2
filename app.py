# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 21:21:11 2021

@author: Mauricio C
"""

from flask import *
import requests
from bs4 import BeautifulSoup
import json
from flask_cors import CORS, cross_origin

app= Flask(__name__)
CORS(app)
@app.route('/search', methods = ['GET'])
def MercadoLibre():
    URL = request.args.get('url')
    # fase 1 - Datos generales del articulo
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    NombreArticulo = soup.find_all("h1", {"class": "ui-pdp-title"})[0].contents[0]
    NombreArticulo= NombreArticulo.replace("/"," ")
    precio = soup.find_all("span", {"class": "price-tag-fraction"})[0].contents[0]        
    Image_articulo = soup.find_all("figure", {"class": "ui-pdp-gallery__figure"})[0]
    Image_articulo= Image_articulo.find_all("img")[0]['data-zoom']
    
    ## si encuentra o no un modal en la 2 version de mercado libre
    ## Datos del vendedor
    try:
        # fase 2
        url = soup.find_all("a", {"class": "ui-pdp-media__action ui-box-component__action"})[0]['href']
    
    except:
        url = soup.find_all("a", {"class": "ui-pdp-action-modal__link"})[-1]['href']       
        # fase 2
        page_user_middleware = requests.get(url)
        soup_user_middleware = BeautifulSoup(page_user_middleware.content, 'html.parser')
        
        data = soup_user_middleware.find_all("p", {"class": "feedback-profile-link"})[0]
        url = data.find_all("a")[0]
        url = url['href']

    finally:
        # fase 2.1
        page_user = requests.get(url)
        soup_user = BeautifulSoup(page_user.content, 'html.parser')
        name_vendedor = soup_user.find_all("h3", {"class": "store-info__name"})[0].contents[0]        
        Califications = soup_user.find_all("span", {"class": "buyers-feedback-qualification"})
        calification_points = []
        for C in Califications:
            calification_points.append(C.contents[4]) 
        
        reputation = soup_user.find_all("div", {"class": "data-level__wrapper"})[0]
        reputation= reputation.find_all("span", {"class": "data-level__number"})
        recomendado = reputation[0].contents[0]
        ventas_completadas = reputation[1].contents[0]
        años_vendiendo = reputation[-1].contents[0]

        time = soup_user.find_all("p", {"class": "data-level__description"})[-1]
        time = time.find_all("span")[0].contents[-1].split(' ')[1]
        if(time == 'años'):
            time = 'anios'      

    # fase 3 - Comparativa con los demas articulos parecidos
    new_url = 'https://listado.mercadolibre.com.ec/'+NombreArticulo
    page_other_article = requests.get(new_url)
    soup_other_article = BeautifulSoup(page_other_article.content, 'html.parser')

    prices = soup_other_article.find_all("span", {"class": "price-tag-fraction"})
    sume = 0
    maxi = 0
    mini = 9999999
    for price in prices: 
        num = float(price.contents[0].replace(".",""))
        sume = sume + num
        if(num<mini):
            mini=num
        if (num>maxi):
            maxi=num
    if (len(prices) != 0):
        average= sume/len(prices)
        average= round(average,2)
    else:
        average = 0
    dicJson = {"Nombre" : NombreArticulo,"Image":Image_articulo,"Vendedor":name_vendedor,"Precio":precio ,"Puntos":calification_points, "Recomendado": recomendado, "Ventas":ventas_completadas,"Time":años_vendiendo,"typeTime":time,"Promedio":average, "Maximo":maxi,"Minimo": mini}
    return json.dumps(dicJson)

## Busqueda en Ebay
@app.route('/searchEbay', methods = ['GET'])
def Ebay():
    articulo = request.args.get('articulo')    
    URL = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="+ articulo    
    page_Ebay = requests.get(URL)
    soup_Ebay = BeautifulSoup(page_Ebay.content, 'html.parser')
    precios = soup_Ebay.find_all("span", {"class": "s-item__price"})

    if(len(precios) == 0):
        Name = articulo.split(' ')
        articulo = Name[0]+' '+Name[1]+' '+Name[2]+' '+Name[3]
        URL = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=" +articulo   
        page_Ebay = requests.get(URL)
        soup_Ebay = BeautifulSoup(page_Ebay.content, 'html.parser')  
        precios = soup_Ebay.find_all("span", {"class": "s-item__price"})  
    try:       
        sume = 0
        maxi = 0
        mini = 9999999

        for price in precios:
            num = float(price.contents[0].replace('USD',''))
            sume = sume + num
            if(num<mini):
                mini=num
            if (num>maxi):
                maxi=num
        if (len(precios) != 0):
            average= sume/len(precios)
            average= round(average,2)
        else:
            average = 0
    except :
        average = 0
        maxi = 0
        mini = 0

    dicJson = {"Promedio":average, "Maximo":maxi,"Minimo": mini, "Busqueda": articulo}
    return json.dumps(dicJson)
    
if __name__ == '__main__':
    app.run(port=5000)
