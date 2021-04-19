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
    
    def fase2(url):
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

        return [time,calification_points,recomendado,ventas_completadas,años_vendiendo,name_vendedor]
           
    def buscarInfo(NombreArticulo):
        # fase 3 - Comparativa con los demas articulos parecidos
        new_url = 'https://listado.mercadolibre.com.ec/'+NombreArticulo
        page_other_article = requests.get(new_url)
        soup_other_article = BeautifulSoup(page_other_article.content, 'html.parser')
        card = soup_other_article.find_all("img", {"class": "ui-search-result-image__element"})
        datos = []
        sume = 0
        maxi = 0
        mini = 9999999

        for item in card:
            # obtener precios
            price = soup_other_article.find_all("a", {"title": item['alt']})
            #print(price[1].find_all("span", {"class": "price-tag-fraction"}))
            try:
                num = float(price[1].find_all("span", {"class": "price-tag-fraction"})[0].contents[0])        
            except:
                search = soup_other_article.find_all("div", {"class": "andes-card andes-card--flat andes-card--default ui-search-result ui-search-result--core andes-card--padding-default"})
                for c in search:
                    if (item['alt'] == c.contents[0].contents[0]['title']):
                        num = float(c.contents[1].find_all("span", {"class": "price-tag-fraction"})[0].contents[0])
            finally:
                sume = sume + num
                if(num<mini):
                    mini=num
                if (num>maxi):
                    maxi=num
                ## generacion de json
                datos.append({'Nombre': item['alt'],  'Url': price[0]['href'], 'Image': item['data-src'], 'Precio': num})            
        average= sume/len(card)
        average = round(average,2) 
        return [average,mini,maxi,datos]

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
        fas2 = fase2(url)
        fas3 = buscarInfo(NombreArticulo)

    except:        
        url = soup.find_all("a", {"class": "ui-pdp-action-modal__link"})[-1]['href']
        # fase 2
        page_user_middleware = requests.get(url)
        soup_user_middleware = BeautifulSoup(page_user_middleware.content, 'html.parser')
        try:
            data = soup_user_middleware.find_all("p", {"class": "feedback-profile-link"})[0]
            url = data.find_all("a")[0]
            url = url['href']
            fas2 = fase2(url)
            fas3 = buscarInfo(NombreArticulo)

        except:
            fas2 = ['años',0,0,0,0,""]
            fas3 = buscarInfo(NombreArticulo)

    finally:        
        dicJson = {"Nombre" : NombreArticulo,"Image":Image_articulo,"Vendedor":fas2[5],"Precio":precio ,"Puntos":fas2[1], "Recomendado": fas2[2], "Ventas":fas2[3],"Time":fas2[4],"typeTime":fas2[0],"Promedio":fas3[0], "Maximo":fas3[2],"Minimo": fas3[1],'otrosDatos': fas3[3]}
        return json.dumps(dicJson)

## Busqueda en Ebay
@app.route('/searchEbay', methods = ['GET'])
def Ebay():
    try: 
        articulo = request.args.get('articulo')    
        URL = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="+ articulo    
        page_Ebay = requests.get(URL)
        soup_Ebay = BeautifulSoup(page_Ebay.content, 'html.parser')
        card = soup_Ebay.find_all("div", {"class": "s-item__wrapper clearfix"})
        card.pop(0)

        if(len(card) == 0):
            dicJson = {}
            return json.dumps(dicJson),404

        sume = 0
        maxi = 0
        mini = 9999999

        datos = []
        for item in card:            
            try:        
                data = item.contents[0].find_all("a")[0].find_all("img")[0]
                                    
                num = float(item.contents[1].find_all("span", {"class": "s-item__price"})[0].contents[0].replace(' ','').replace(',','').replace('$','')) # Deploy
                #num = float(item.contents[1].find_all("span", {"class": "s-item__price"})[0].contents[0].replace(' ','').replace(',','').replace('USD',''))   # Desarrollo
                
                sume = sume + num
                if(num<mini):
                    mini=num
                if (num>maxi):
                    maxi=num
            
                ## generacion de json
                datos.append({'Nombre': data['alt'],  'Url': item.contents[0].find_all("a")[0]['href'] , 'Image': data['src'], 'Precio': num})         
            except:
                pass
        
        average= sume/len(datos)
        average = round(average,2) 

        dicJson = dicJson = {"Promedio":average, "Maximo":maxi,"Minimo": mini, "otrosDatos":datos}        
        return json.dumps(dicJson),200
    except:
        dicJson = {}
        return json.dumps(dicJson),404

## Busqueda en Olx
@app.route('/searchOlx', methods = ['GET'])
def Olx():
    try:
        articulo = request.args.get('articulo')    
        URL = "https://www.olx.com.ec/items/q-"+ articulo    
        page_Olx = requests.get(URL)
        soup_Olx = BeautifulSoup(page_Olx.content, 'html.parser')
        card = soup_Olx.find_all("li", {"data-aut-id": "itemBox"}) 

        if(len(card) == 0):
            dicJson = {}
            return json.dumps(dicJson),404
            
        sume = 0
        maxi = 0
        mini = 9999999

        datos = []
        for item in card:
            values= item.contents[0].find_all("img")[0]
            num = float(item.contents[0].find_all("span", {"data-aut-id": "itemPrice"})[0].contents[0].replace(' ','').replace('$','').replace(',',''))    
            
            sume = sume + num
            if(num<mini):
                mini=num
            if (num>maxi):
                maxi=num

            ## generacion de json
            datos.append({'Nombre': values['alt'],  'Url': 'https://www.olx.com.ec'+item.contents[0]['href'], 'Image': values['src'], 'Precio': num})
            
        average= sume/len(card)
        average = round(average,2) 

        dicJson = dicJson = {"Promedio":average, "Maximo":maxi,"Minimo": mini, "otrosDatos":datos}
        dicJson
        return json.dumps(dicJson),200
    except:
        dicJson = {}
        return json.dumps(dicJson),404

if __name__ == '__main__':
    app.run(port=5000)
