import requests
from datetime import datetime

fh = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
linea = 12
#sentido = 1

HOST = "https://reddelineas.tussam.es/API/infotus-ui"


def obtenerLineas():
    """ Obtiene todas las lineas activas actualmente de Tussam
    """
    fh = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
    request = f"{HOST}/lineas/{fh}"
    response = requests.get(request)
    datos = response.json()
    return datos["result"]["lineasDisponibles"]


def obtenerParadasLinea(linea:int, sentido:int):
    """ Dada una línea (int) y su sentido (int) obtiene todas
    las paradas que visita en su ruta
    """
    fh = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
    fh = str(fh).replace(":","%3A")
    request = f"{HOST}/nodosLinea/{linea}/{sentido}/{fh}"
    response = requests.get(request)
    datos = response.json()
    return datos["result"]


def formarVertices():
    lineas = obtenerLineas()
    vertices = list()
    for linea in lineas:
        for sentido in linea["destinos"]:
            paradas = obtenerParadasLinea(linea["linea"],sentido["sentido"])
            for parada in paradas:
                vertice = Vertice(codigo=parada["codigo"],
                                  coordenadas=(parada["posicion"]["latitudE6"],parada["posicion"]["longitudE6"]),
                                  nombre=parada["descripcion"]["texto"])
                print(vertice)
                vertices.append(vertice)
    return vertices


def formarAristas():
    lineas = obtenerLineas()
    aristas = list()
    for linea in lineas:
        for sentido in linea["destinos"]:
            paradas = obtenerParadasLinea(linea["linea"],sentido["sentido"])
            for po,pd in zip(paradas,paradas[1:]):
                arista = Arista(linea=linea["labelLinea"],
                                origen=po["codigo"],
                                destino=pd["codigo"],
                                distancia=pd["distancia"]-po["distancia"])
                print(arista)
                aristas.append(arista)
    return aristas

class Vertice:
    codigo: int
    coordenadas: (int,int)
    nombre: str

    def __init__(self, codigo, coordenadas, nombre):
        self.codigo = codigo
        self.coordenadas = coordenadas
        self.nombre = nombre

    def __str__(self):
        return f"Parada: {self.nombre} Codigo: {self.codigo} Coordenadas: {self.coordenadas}"
    
    def __write__(self):
        return f"{self.codigo}, {self.nombre.replace(',','')}, {self.coordenadas}"

class Arista:
    linea: int
    origen: int
    destino: int
    distancia: int

    def __init__(self, linea, origen, destino, distancia):
        self.linea = linea
        self.origen = origen
        self.destino = destino
        self.distancia = distancia

    def __str__(self):
        return f"Linea: {self.linea} Origen: {self.origen} Destino: {self.destino} Distancia: {self.distancia}"
    
    def __write__(self):
        return f"{self.origen}, {self.destino}, {self.linea}, {self.distancia}"


vertices = formarVertices()
aristas = formarAristas()


print(f"Vertices: {len(vertices)}")
print(f"Aristas: {len(aristas)}")

with open("db.txt","w", encoding='utf-8') as file:
    file.write("#VERTEX#")
    for vertex in vertices:
        file.write(f"\n{vertex.__write__()}")

    file.write("\n#EDGE#")
    for edge in aristas:
        file.write(f"\n{edge.__write__()}")
