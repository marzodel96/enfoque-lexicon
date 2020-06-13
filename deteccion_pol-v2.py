import re, string, unicodedata, os
import nltk
import csv
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer

finalpol = [0,0,0] #[POS,NEU,NEG]
palabrapositiva = [] #array pos
palabranegativa = [] #array neg
palabraneutra = [] #array neu

# // Tratamiento intensificador y negacion // #
listado_de_intensificadores = ["tanto", "demasiado", "bastante", "mucho", "harto", "muy", "ultra", "demasiada", "mucha", "tan", "muchísimo", "muchísima", "mega", "hiper"]
listado_de_negaciones = ["nadie", "jamás", "tampoco", "no", "ni", "nunca", "nada", "ningún", "ninguna", "ninguno", "ni siquiera"]

cambiopol = False
total_de_badwords = 0 #para contabilizar malas palabras encontradas
cant_intensificador = 0 #cantidad de veces que aparece el intensificador
cant_aum_intensificador = 1 #cantidad que debe aumentar el intensificador para realizar el cambio
cant_camb_intensificador = 0 #cantidad de veces que debe cambiar el intensificador

# // Necesario para leer texto en directorio donde se encuentra  // #
directorio = "testeo/"
dirs = os.listdir(directorio)
dir = [directorio + archivo for archivo in dirs]

# // Función que limpia el texto ingresado // #
def limpieza_texto(lector):
    text = lector.replace('!','') # Eliminacion signo ! #
    text = lector.replace('¡','') # Eliminacion signo ¡ #
    text = lector.replace('?','') # Eliminacion signo ? #
    text = lector.replace('¿','') # Eliminacion signo ¿ #
    text = lector.replace('.','') # Eliminacion punto . #
    text = lector.lower()  # Cambio de mayúsculas a minúsculas #
    return text #retorna el texto con los cambios pertinentes

# // Función que remueve las stopwords del texto ingresado // #
def eliminar_stopwords(words):
    limpieza = []
    for word in words:
        if word not in stopwords.words('spanish'):
            limpieza.append(word)
    return limpieza

# // Función que retorna el lemma de cada palabra del texto ingresado // #
def lemma_texto(words):
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

# // Lectura + limpieza del archivo a ingresar (limpieza_texto,eliminar_stopwords,lemma_texto) // #
for archivo in dir:
    with open(archivo, encoding="utf-8") as f:
        lector = f.read()
        print("Texto original:\n\n"+lector)
        #print("\n")
        lector = limpieza_texto(lector)
        words = nltk.word_tokenize(lector)
        words = eliminar_stopwords(words)
        lemmas = lemma_texto(words) #Variable final 'lemmas' es la que se va al procesamiento con lexicon y badwords

# // Función para cargar lexicon sentimiento en formato .csv // #
# // Lexicon-SENTIMIENTO.xlsx fue cambiado de formato a .csv con otro código que no forma parte de este desarrollo // *
def carga_lexsent(lexiconsentimiento):
    with open(lexiconsentimiento, mode='r') as archivo_csv:
        reader = csv.DictReader(archivo_csv, delimiter=',')
        instancias_ls = []
        for row in reader:
            instancias_ls.append(row["palabra"] + " " + row["polaridad"]) #se agregan nombres a las columnas del .csv para ser leídas de mejor manera
        return instancias_ls

# // Función para cargar badWords en formato .csv // #
def carga_bwords(badwords):
    with open(badwords, mode='r') as archivo_csv:
        reader = csv.DictReader(archivo_csv, delimiter=',')
        instancias_bw = []
        for row in reader:
            instancias_bw.append(row["badwords"]) #se agrega nombre a la columna del .csv para ser leída de mejor manera
        return instancias_bw

# // Tratamiento de polaridad // #
def deteccionpol(pol,cambiopol,finalpol):
    pol_neutro = ["neutro"]
    pol_positiva = ["positivo"] 
    pol_negativa = ["negativo"] 

    #si lo que llega de pol es positivo, negativo o neutro...
    if pol == pol_neutro:
        finalpol[1] += 1 #se le suma 1 al array -> posición neutro

    #cambiopol afectado a polnegativa y polpositiva...
    if pol in pol_negativa: #tratamiento negativo
        if cambiopol:
            finalpol[0] += 1
        else:
            finalpol[2] += 1

    if pol in pol_positiva: #tratamiento positivo
        if cambiopol: 
            finalpol[2] += 1 
        else:
            finalpol[0] += 1
    
# // Carga de lexicon sentimiento y badWords utilizando funciones // #
lexiconload = carga_lexsent('resultadolexicon.csv')
bwordsload = carga_bwords('badWords.csv')

# // Tratamiento de lexicon y badwords con lemma final // #
for i in range(0, len(lemmas)):

    if lemmas[i] in bwordsload: #Cuenta las badWords que existen en texto pre-procesado (lemma)
        total_de_badwords += 1 
    
    if cant_intensificador > 0: #como cant_intensificador tiene valor 2
        cant_intensificador -= 1 #cant_intensificador = 1
        if cant_intensificador == 0:
            cant_aum_intensificador = 1

    if cant_camb_intensificador > 0: #como cant_camb_intensificador tiene valor 2
        cant_camb_intensificador -= 1 #cant_camb_intensificador = 1
        if cant_camb_intensificador == 0:
            cambiopol = False
    
    if lemmas[i] in listado_de_intensificadores: #si lemma posee palabras del listado de intensificadores
        cant_intensificador = 2 #cambio de valor a variable
        cant_aum_intensificador = 2 #cambio de valor a variable
        i += 1 #aumentar una posición en lemma (cambiar a siguiente palabra del array para seguir la revisión)
    elif lemmas[i] in listado_de_negaciones: #si lemma posee palabras del listado de negaciones
        cant_camb_intensificador = 2 #cambio de valor a variable
        cambiopol = True #cambiopol cambia valor booleano
        i += 1 #aumentar una posición en lemma (cambiar a siguiente palabra del array para seguir la revisión)

    for j in range(0, len(lexiconload)): #Analizando texto ingresado con lexicon sentimiento
        columna_lexicon = lexiconload[j].split(" ")
        if lemmas[i] == columna_lexicon[0]:
            if columna_lexicon[1] == "negativo":
                palabranegativa.append(columna_lexicon[0]) #va agregando a un array todas las palabras ingresadas que correspondan a la clasificación "negativo"
            if columna_lexicon[1] == "neutro":
                palabraneutra.append(columna_lexicon[0]) #va agregando a un array todas las palabras ingresadas que correspondan a la clasificación "neutro"
            if columna_lexicon[1] == "positivo":
                palabrapositiva.append(columna_lexicon[0])  #va agregando a un array todas las palabras ingresadas que correspondan a la clasificación "positivo"
            deteccionpol(columna_lexicon[1], cambiopol, finalpol) #le pasa a la función deteccionpol si es neg,pos,neu - cambio de polaridad y la polaridad final


# // Aquí se muestra el resultado final de la polaridad del texto ingresado contabilizando las badWords encontradas // #
print("--- RESULTADO FINAL DE POLARIDAD PARA TEXTO INGRESADO: ---\n")
if finalpol[0] > finalpol[2]:
    print("El texto tiene polaridad POSITIVA con "+ str(total_de_badwords) + " malas palabras.\n")
else:
    if finalpol[0] < finalpol[2]:
        print("El texto tiene polaridad NEGATIVA con "+ str(total_de_badwords) + " malas palabras.\n")
    else:
        print("El texto tiene polaridad NEUTRA con "+ str(total_de_badwords) + " malas palabras.\n")

# END #