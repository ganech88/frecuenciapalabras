from flask import Flask, request, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from nltk.tokenize import regexp_tokenize
from bson import json_util
import os
import json
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://meli:meli@cluster0.m7rsa.mongodb.net/desafio?retryWrites=true&w=majority")
db = client.get_database()

def cargar_base():
    ruta='/code/coleccion_2022/coleccion_2022/'
    documentos=[]
    titulo_libro=[]
    frec_dic = {}
    list_lib = []
    list_dir =[]
    i = 0
    sacar_letra = "á,é,í,ó,ú"
    direccion=os.listdir(ruta)
    for elemento in direccion:
        if elemento.endswith('.txt'):
            titulo_libro.append(elemento)
            f=open(os.path.join(ruta,elemento), encoding="UTF-8")
            palb=f.read()
            documentos.append(palb)
            f.close()
    for docu in documentos:
        frec_index = {}
        text_norm =[]
        list_lib = []
        g=str(docu).lower()
        for caracter in sacar_letra:
            g= g.replace(caracter, "")
        text_norm = regexp_tokenize(g, "[\w]+") #Aca utilizo esta funcion para separar cada palabra de un documento
        for word in text_norm:
            if word in frec_dic:
                frec_dic[word] += 1            
            else:
                frec_dic[word] = 1
            if word in frec_index:
                frec_index[word] += 1            
            else:
                frec_index[word] = 1
        values_list_libro = list(frec_index.values())
        keys_list_libro = list(frec_index.keys())
        for libr in range(len(values_list_libro)): #Aca genero la lista de diccionarios de la frecuencia de palabras en un libro en particular
            palabra = {"palabra": None, "frecuencia": None}
            palabra["palabra"] = (keys_list_libro[libr])
            palabra["frecuencia"] = (values_list_libro[libr])
            list_lib.append(palabra)
        mycol = db[titulo_libro[i]]
        mycol.insert_many(list_lib)
        i+=1
    
    values_list_dir = list(frec_dic.values())
    keys_list_dir = list(frec_dic.keys())
    for dire in range(len(values_list_dir)): #Aca genero la lista de diccionarios de la frecuencia de palabras de todo el directorio.
        pal_dir = {"palabra": None, "frecuencia": None}
        pal_dir["palabra"] = (keys_list_dir[dire])
        pal_dir["frecuencia"] = (values_list_dir[dire])
        list_dir.append(pal_dir)
    mycol = db.directorio
    mycol.insert_many(list_dir)


@app.route('/', methods=['GET']) #Esta Query hace que si no me informan el nombre del docuemento, informo la totalidad de frecuencia en el directorio
def frecuencia_libro():
    doc_name = request.args.get('doc_name')
    term = request.args.get('term')
    if(not doc_name):
        col = db.directorio
        lib = col.find({"palabra": term}, {"palabra":0,"_id":0} ) 
        response = json_util.dumps(lib)
        return Response(response, mimetype = 'application/json')
    else:
        col = db.get_collection(doc_name)
        lib = col.find({"palabra": term}, {"palabra":0,"_id":0} ) 
        response = json_util.dumps(lib)
        return Response(response, mimetype = 'application/json')

vacio=db.directorio.find()
resultado= list(vacio)
if(len(resultado)==0): #Aca pregunto si la base esta vacia para ver si tengo que cargarla
    cargar_base()
else: print("La base ya se encuentra cargada")

if __name__  == "__main__":
    app.run(debug=False)
