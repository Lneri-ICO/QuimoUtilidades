import psycopg2
import csv
from io import StringIO
import re
from configparser import ConfigParser

# Configuración de la base de datos (se lee del archivo config.ini)
config = ConfigParser()
config.read('config.ini')

try:
    db_config = config['database']
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    cursor = conn.cursor()
    print("Conexión a la base de datos exitosa.")

except (Exception, psycopg2.Error) as error:
    print(f"Error al conectar a la base de datos: {error}")
    exit()

def obtener_datos_csv():
    """Analiza los archivos CSV y extrae productos, materias primas y fórmulas."""
    # Archivos CSV proporcionados por el usuario
    archivos_csv = {
        "Algo.xlsx - Hoja 1.csv": """AMINA JB,,,Área:,,Mezcla Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,SULFATO DE AMONIO ,,19.23,0,,,,,,,,
2,TRIETANOLAMINA ,,3.07,0,,,,,,,,
3,ÁCIDO TIOGLICÓLICO,,0.77,0,,,,,,,,
4,AGUA,,76.93,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
AMINA JAF,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,130
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,SULFATO DE AMONIO ,,23,0,,,,,,,,
2,TRIETANOLAMINA ,,3.1,0,,,,,,,,
3,ÁCIDO TIOGLICÓLICO,,1.15,0,,,,,,,,
4,AGUA,,73,0,,,,,,,,
,,TOTAL,100.25,0,,,,,,,,
,,,,,,,,,,,,
ENZIM REM,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,50
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,ENZIMA PC WET-1,,2,0,,,,,,,,
2,CAOLÍN INDUSTRIAL ,,98,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
ENZIM RND,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,200
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,ACTASE NF 10,,2,0,,,,,,,,
2,CAOLÍN INDUSTRIAL ,,98,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
ENZIM PEL,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,25
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,ENZIMA PC LIN 1,,2,0,,,,,,,,
2,CAOLÍN INDUSTRIAL ,,98,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
DESENGRAS BIO 78,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir 
(Kg): ,,,,,1000
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,77.5,0,,,,,,,,
2,ADBS ,,10,0,,,,,,,,
3,LESS ,,10,0,,,,,,,,
4,SOSA DILUIDA,,2.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
DESLIZANTE,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,100
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,GOMA GUAR ,,25,0,,,,,,,,
2,HARINA ,,25,0,,,,,,,,
3,CAOLÍN INDUSTRIAL ,,50,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
IMPEOIL SOFT,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,400
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,ACEITE MINERAL,,42,0,,,,,,,,
2,LAURICO 7 MOLES,,7,0,,,,,,,,
3,ADBS ,,1.5,0,,,,,,,,
4,AGUA,,47.746,0,,,,,,,,
5,SOSA ESCAMAS,,0.375,0,,,,,,,,
6,PEG-150-DE,,1.13,0,,,,,,,,
7,FORMOL,,0.25,0,,,,,,,,
,,TOTAL,100.001,0,,,,,,,,
,,,,,,,,,,,,
IMPEHUM HB,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,SOSA LÍQUIDA  AL 50%,,2.5,0,,,,,,,,
2,ADBS ,,10,0,,,,,,,,
3,AGUA,,87.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
IMPEHUM HB,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,SOSA LÍQUIDA  AL 50%,,2.5,0,,,,,,,,
2,ADBS ,,10,0,,,,,,,,
3,AGUA,,87.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FIXQUIMO,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,100
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,FIXQUIMO MP,,1,0,,,,,,,,
2,AGUA,,99,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FIXQUIMO PREDILUIDO,,,Área:,,Mezclado Quimo ,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,50
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,FIXQUIMO MP,,1,0,,,,,,,,
2,AGUA,,99,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
SUAVIZANTE DE ROPA,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,180
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,SUAVIPASTA,,3,0,,,,,,,,
2,ANTIESPUMANTE ,,0.25,0,,,,,,,,
3,AGUA,,95.72,0,,,,,,,,
4,PROPILENGLICOL,,0.15,0,,,,,,,,
5,FRAGANCIA BLUE FRESH,,0.5,0,,,,,,,,
6,BENZOATO DE SODIO,,0.03,0,,,,,,,,
7,COLORANTE DILUIDO AZUL CIELO,,0.35,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
DESLIZANTE,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,100
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,GOMA GUAR,,25,0,,,,,,,,
2,HARINA,,25,0,,,,,,,,
3,CAOLÍN INDUSTRIAL,,50,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
IMPEFAST SP,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,89.88,0,,,,,,,,
2,ÁCIDO CÍTRICO,,0.2,0,,,,,,,,
3,CLORURO DE BENZALCONIO,,1.5,0,,,,,,,,
4,ALCOHOL ISOPROPÍLICO,,7.02,0,,,,,,,,
5,LESS,,1,0,,,,,,,,
6,FRAGANCIA LIMÓN,,0.2,0,,,,,,,,
7,COLORANTE VERDE,,0.2,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FANTÁSTICO LIMÓN,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,150
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,LESS ,,0.66,0,,,,,,,,
2,NONIL FENOL 10 MOL ,,0.41,0,,,,,,,,
3,ALCOHOL ISOPROPÍLICO ,,0.83,0,,,,,,,,
4,BENZOATO DE SODIO,,0.03,0,,,,,,,,
5,FRAGANCIA LIMÓN,,0.5,0,,,,,,,,
6,PROPILENGLICOL,,0.33,0,,,,,,,,
7,AGUA,,96.78,0,,,,,,,,
8,COLORANTE LÍQUIDO COLOR VERDE LIMÓN,,0.46,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
JABÓN PARA MANOS LIQUIDO,,,,Área:,,Mezclado Quimo Clean,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,300
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,LESS ,,5.4,0,,,,,,,,
2,GLICERINA,,0.5,0,,,,,,,,
3,EDTA,,0.1,0,,,,,,,,
4,AMIDA DE COCO,,2.5,0,,,,,,,,
5,BETAINA DE COCO,,2,0,,,,,,,,
6,FRAGANCIA JABÓN DE MANOS,,0.2,0,,,,,,,,
7,AGUA,,88.75,0,,,,,,,,
8,BENZOATO DE SODIO,,0.05,0,,,,,,,,
9,COLORANTE LIQUIDO NARANJA,,0.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FANTÁSTICO PRIMAVERA,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,200
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,LESS ,,0.67,0,,,,,,,,
2,NONIL FENOL 10 MOL ,,0.42,0,,,,,,,,
3,ALCOHOL ISOPROPÍLICO ,,0.83,0,,,,,,,,
4,BENZOATO DE SODIO,,0.03,0,,,,,,,,
5,FRAGANCIA PRIMAVERA,,0.5,0,,,,,,,,
6,PROPILENGLICOL,,0.33,0,,,,,,,,
7,AGUA,,96.76,0,,,,,,,,
8,COLORANTE LÍQUIDO COLOR AZUL,,0.46,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
AROMATIZANTE ,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,10,,
1,TWEEN 20,,1.5,0,,,,,,,,
2,FRAGANCIA PRIMAVERA,,1.5,0,,,,,,,,
3,PROPILENGLICOL,,1.5,0,,,,,,,,
4,AGUA,,94.5,0,,,,,,,,
5,COLORANTE,,1,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
VINIL PARA INTERIORES,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,20,,
1,AGUA,,71.8,0,,,,,,,,
2,GLICERINA,,15,0,,,,,,,,
3,EMULSIÓN DE SILICÓN,,10,0,,,,,,,,
4,CERA,,,3,0,,,,,,,,
5,FRAGANCIA,,0.2,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
SARRIGEL,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,LESS,,25,0,,,,,,,,
2,ÁCIDO CLORHÍDRICO (MURIATICO),,25,0,,,,,,,,
3,NONIL FENOL 10 MOL,,5.83,0,,,,,,,,
4,COLORANTE DILUIDO ROSA BRILLANTE,,0.75,0,,,,,,,,
5,AGUA,,43.42,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
MÁS NEGRO,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,67.51,0,,,,,,,,
2,EDTA,,0.17,0,,,,,,,,
3,BENZOATO DE SODIO,,0.2,0,,,,,,,,
4,DETERCON,,16,0,,,,,,,,
5,LESS,,11.67,0,,,,,,,,
6,AMIDA DE COCO,,2,0,,,,,,,,
7,FRAGANCIA MÁS COLOR,,0.18,0,,,,,,,,
8,COLORANTE NEGRO,,0.21,0,,,,,,,,
9,SAL,,1.4,0,,,,,,,,
10,PROPILENGLICOL,,0.75,0,,,,,,,,
,,TOTAL,100.09000000000002,0,,,,,,,,
,,,,,,,,,,,,
ACEITE PARA MOP,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,ACEITE MINERAL,,70,0,,,,,,,,
2,GASOLINA BLANCA,,30,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
CLORO CLEAN,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,200
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,HIPOCLORITO DE SODIO ,,30.56,0,,,,,,,,
2,AGUA,,69.34,0,,,,,,,,
3,EDTA,,0.1,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
JABÓN PARA TRASTES LÍQUIDO LIMÓN,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,68.425,0,,,,,,,,
2,DETERCON,,12.5,0,,,,,,,,
3,LESS,,15,0,,,,,,,,
4,AMIDA DE COCO,,1,0,,,,,,,,
5,FRAGANCIA LIMÓN,,0.05,0,,,,,,,,
6,COLORANTE VERDE ESMERALDA,,0.025,0,,,,,,,,
7,SAL,,3,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
DETERGENTE LÍQUIDO PARA ROPA DE COLOR,,,,Área:,,Mezclado Quimo Clean,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg):,,,120,,
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,79.72,0,,,,,,,,
2,DETERCON,,5.91,0,,,,,,,,
3,LESS,,9.85,0,,,,,,,,
4,BETAINA DE COCO,,1.48,0,,,,,,,,
5,FRAGANCIA MÁS COLOR,,0.05,0,,,,,,,,
6,COLORANTE AZUL,,0.01,0,,,,,,,,
7,SAL,,2.96,0,,,,,,,,
8,BLANQUEADOR ÓPTICO,,0.02,0,,,,,,,,
,,TOTAL,99.999999999999986,0,,,,,,,,
,,,,,,,,,,,,
DETERCON,,,Área:,,Mezclado Quimo Clean,,,,,,,
MATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,
1,AGUA,,82.26,0,,,,,,,,
2,ADBS,,14.52,0,,,,,,,,
3,SOSA AL 50 %,,3.23,0,,,,,,,,
,,TOTAL,100.01,0,,,,,,,,
,,,,,,,,,,,,
FINATELA FLOR DE LUNA,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,190,,
1,SUAVIPASTA,,3,0,,,,,,,,
2,ANTIESPUMANTE ,,0.25,0,,,,,,,,
3,BENZOATO DE SODIO,,0.03,0,,,,,,,,
4,AGUA,,95.72,0,,,,,,,,
5,PROPILENGLICOL,,0.15,0,,,,,,,,
6,FRAGANCIA FLOR DE LUNA,,0.35,0,,,,,,,,
7,COLORANTE DILUIDO MORADO,,0.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FINATELA PRIMAVERA,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,1,,
1,SUAVIPASTA,,3,0,,,,,,,,
2,ANTIESPUMANTE ,,0.25,0,,,,,,,,
3,BENZOATO DE SODIO,,0.03,0,,,,,,,,
4,AGUA,,95.72,0,,,,,,,,
5,PROPILENGLICOL,,0.15,0,,,,,,,,
6,FRAGANCIA SUAVITEL,,0.5,0,,,,,,,,
7,COLORANTE DILUIDO AZUL,,0.5,0,,,,,,,,
,,TOTAL,100.15,0,,,,,,,,
,,,,,,,,,,,,
AROMATIZANTE RECARGADO,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,5,,
1,PROPILENGLICOL,,3,0,,,,,,,,
2,AGUA,,93.4,0,,,,,,,,
3,FRAGANCIA ,,1.8,0,,,,,,,,
4,TWEEN 20,,1.8,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
VINIL PARA INTERIORES,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,20,,
1,AGUA,,71.8,0,,,,,,,,
2,GLICERINA,,15,0,,,,,,,,
3,EMULSIÓN DE SILICÓN,,10,0,,,,,,,,
4,CERA,,,3,0,,,,,,,,
5,FRAGANCIA,,0.2,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
""",
        "Algo.xlsx - Angel.csv": """SARRIGEL,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,LESS,,25,0,,,,,,,,\n2,ÁCIDO CLORHÍDRICO (MURIATICO),,25,0,,,,,,,,\n3,NONIL FENOL 10 MOL,,5.83,0,,,,,,,,\n4,COLORANTE DILUIDO ROSA BRILLANTE,,0.75,0,,,,,,,,\n5,AGUA,,43.42,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nMÁS NEGRO,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,67.51,0,,,,,,,,\n2,EDTA,,0.17,0,,,,,,,,\n3,BENZOATO DE SODIO,,0.2,0,,,,,,,,\n4,DETERCON,,16,0,,,,,,,,\n5,LESS,,11.67,0,,,,,,,,\n6,AMIDA DE COCO,,2,0,,,,,,,,\n7,FRAGANCIA MÁS COLOR,,0.18,0,,,,,,,,\n8,COLORANTE NEGRO,,0.21,0,,,,,,,,\n9,SAL,,1.4,0,,,,,,,,\n10,PROPILENGLICOL,,0.75,0,,,,,,,,\n,,TOTAL,100.09000000000002,0,,,,,,,,\n,,,,,,,,,,,,\nACEITE PARA MOP,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,ACEITE MINERAL,,70,0,,,,,,,,\n2,GASOLINA BLANCA,,30,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nCLORO CLEAN,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,200\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,HIPOCLORITO DE SODIO ,,30.56,0,,,,,,,,\n2,AGUA,,69.34,0,,,,,,,,\n3,EDTA,,0.1,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nJABÓN PARA TRASTES LÍQUIDO LIMÓN,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,68.425,0,,,,,,,,\n2,DETERCON,,12.5,0,,,,,,,,\n3,LESS,,15,0,,,,,,,,\n4,AMIDA DE COCO,,1,0,,,,,,,,\n5,FRAGANCIA LIMÓN,,0.05,0,,,,,,,,\n6,COLORANTE VERDE ESMERALDA,,0.025,0,,,,,,,,\n7,SAL,,3,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nDETERGENTE LÍQUIDO PARA ROPA DE COLOR,,,,Área:,,Mezclado Quimo Clean,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg):,,,120,,\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,79.72,0,,,,,,,,\n2,DETERCON,,5.91,0,,,,,,,,\n3,LESS,,9.85,0,,,,,,,,\n4,BETAINA DE COCO,,1.48,0,,,,,,,,\n5,FRAGANCIA MÁS COLOR,,0.05,0,,,,,,,,\n6,COLORANTE AZUL,,0.01,0,,,,,,,,\n7,SAL,,2.96,0,,,,,,,,\n8,BLANQUEADOR ÓPTICO,,0.02,0,,,,,,,,\n,,TOTAL,99.999999999999986,0,,,,,,,,\n,,,,,,,,,,,,\nDETERCON,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,82.26,0,,,,,,,,\n2,ADBS,,14.52,0,,,,,,,,\n3,SOSA AL 50 %,,3.23,0,,,,,,,,\n,,TOTAL,100.01,0,,,,,,,,\n,,,,,,,,,,,,\nIMPEFAST SP,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,89.88,0,,,,,,,,\n2,ÁCIDO CÍTRICO,,0.2,0,,,,,,,,\n3,CLORURO DE BENZALCONIO,,1.5,0,,,,,,,,\n4,ALCOHOL ISOPROPÍLICO,,7.02,0,,,,,,,,\n5,LESS,,1,0,,,,,,,,\n6,FRAGANCIA LIMÓN,,0.2,0,,,,,,,,\n7,COLORANTE VERDE,,0.2,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nFANTÁSTICO PRIMAVERA,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,200\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,LESS ,,0.67,0,,,,,,,,\n2,NONIL FENOL 10 MOL ,,0.42,0,,,,,,,,\n3,ALCOHOL ISOPROPÍLICO ,,0.83,0,,,,,,,,\n4,BENZOATO DE SODIO,,0.03,0,,,,,,,,\n5,FRAGANCIA PRIMAVERA,,0.5,0,,,,,,,,\n6,PROPILENGLICOL,,0.33,0,,,,,,,,\n7,AGUA,,96.76,0,,,,,,,,\n8,COLORANTE LÍQUIDO COLOR AZUL,,0.46,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nJABÓN PARA TRASTES LÍQUIDO,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,68.425,0,,,,,,,,\n2,DETERCON,,12.5,0,,,,,,,,\n3,LESS,,15,0,,,,,,,,\n4,AMIDA DE COCO,,1,0,,,,,,,,\n5,FRAGANCIA MANZANA,,0.05,0,,,,,,,,\n6,COLORANTE VERDE ESMERALDA,,0.025,0,,,,,,,,\n7,SAL,,3,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nLIMPIA PISOS,,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,120\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,95,0,,,,,,,,\n2,LESS ,,2,0,,,,,,,,\n3,NONIL FENOL 10 MOL ,,0.5,0,,,,,,,,\n4,DETERCON,,2,0,,,,,,,,\n5,FORMOL,,0.05,0,,,,,,,,\n6,FRAGANCIA PINAL,,0.2,0,,,,,,,,\n7,COLORANTE,,,0.25,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n,,,,,,,,,,,,\nVINIL PARA INTERIORES,,Área:,,Mezclado Quimo Clean,,,,,,,\nMATERIALES,,,,,,,Cantidad a producir (Kg): ,,,,,20\nN°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,,,,,,\n1,AGUA,,71.8,0,,,,,,,,\n2,GLICERINA,,15,0,,,,,,,,\n3,EMULSIÓN DE SILICÓN,,10,0,,,,,,,,\n4,CERA,,,3,0,,,,,,,,\n5,FRAGANCIA,,0.2,0,,,,,,,,\n,,TOTAL,100,0,,,,,,,,\n""",
        "Algo.xlsx - Neri.csv": """DESENGRAS 2000,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,Cantidad a producir (Kg): ,,,,,120
1,AGUA,,75.47,0,,,,,,,,
2,ADBS ,,15,0,,,,,,,,
3,NONIL FENOL 10 MOL ,,2,0,,,,,,,,
4,ACEITE DE PINO,,1,0,,,,,,,,
5,BUTIL CELLASOLVE ,,5,0,,,,,,,,
6,SOSA ESCAMAS,,1.5,0,,,,,,,,
7,BENZOATO DE SODIO,,0.03,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
JABÓN QUIMO LÍQUIDO,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad programada (Kg),Cantidad agregada (Kg),Hora,Cantidad a producir (Kg): ,,,,,200
1,JABÓN RALLADO QUIMO,,5,0,,,,,,,,
2,VINAGRE,,6,0,,,,,,,,
3,FRAGANCIA,,0.5,0,,,,,,,,
4,AGUA,,88.4,0,,,,,,,,
5,EDTA,,0.1,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FINISH,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg): ,,,,,20
1,AGUA,,75,0,,,,,,,,
2,EDTA,,0.2,0,,,,,,,,
3,LESS,,16,0,,,,,,,,
4,NONIL FENOL 10 MOL,,4,0,,,,,,,,
5,BUTIL CELLOSOLVE,,1,0,,,,,,,,
6,PERÓXIDO DE HIDROGENO,,3,0,,,,,,,,
7,BLANQUEADOR OPTICO,,0.1,0,,,,,,,,
8,FRAGANCIA STAIN ERASER,,0.5,0,,,,,,,,
9,COLORANTE ROSA BRILLANTE,,0.2,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
TIPO VANISH LÍQUIDO,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg): ,,,,,20
1,AGUA,,90,0,,,,,,,,
2,LESS,,5.02,0,,,,,,,,
3,NONIL FENOL 10 MOL,,0.0502,0,,,,,,,,
4,PERÓXIDO DE HIDROGENO,,3.77,0,,,,,,,,
5,FRAGANCIA STAIN ERASER,,0.05,0,,,,,,,,
6,COLORANTE LÍQUIDO ROSA BRILLANTE,,1.2,0,,,,,,,,
,,TOTAL,100.0902,0,,,,,,,,
,,,,,,,,,,,,
FINATELA FLOR DE LUNA,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,190,,
1,SUAVIPASTA,,3,0,,,,,,,,
2,ANTIESPUMANTE ,,0.25,0,,,,,,,,
3,BENZOATO DE SODIO,,0.03,0,,,,,,,,
4,AGUA,,95.72,0,,,,,,,,
5,PROPILENGLICOL,,0.15,0,,,,,,,,
6,FRAGANCIA FLOR DE LUNA,,0.35,0,,,,,,,,
7,COLORANTE DILUIDO MORADO,,0.5,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
FINATELA PRIMAVERA,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,1,,
1,SUAVIPASTA,,3,0,,,,,,,,
2,ANTIESPUMANTE ,,0.25,0,,,,,,,,
3,BENZOATO DE SODIO,,0.03,0,,,,,,,,
4,AGUA,,95.72,0,,,,,,,,
5,PROPILENGLICOL,,0.15,0,,,,,,,,
6,FRAGANCIA SUAVITEL,,0.5,0,,,,,,,,
7,COLORANTE DILUIDO AZUL,,0.5,0,,,,,,,,
,,TOTAL,100.15,0,,,,,,,,
,,,,,,,,,,,,
AROMATIZANTE ,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,10,,
1,TWEEN 20,,1.5,0,,,,,,,,
2,FRAGANCIA PRIMAVERA,,1.5,0,,,,,,,,
3,PROPILENGLICOL,,1.5,0,,,,,,,,
4,AGUA,,94.5,0,,,,,,,,
5,COLORANTE,,1,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
AROMATIZANTE RECARGADO,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,5,,
1,PROPILENGLICOL,,3,0,,,,,,,,
2,AGUA,,93.4,0,,,,,,,,
3,FRAGANCIA ,,1.8,0,,,,,,,,
4,TWEEN 20,,1.8,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
,,,,,,,,,,,,
VINIL PARA INTERIORES,,,,,,,,,,,,
MATERIALES,,,,,,,,,,,,
N°,Materia prima,Lote,%,Cantidad a producir (Kg):,,,20,,
1,AGUA,,71.8,0,,,,,,,,
2,GLICERINA,,15,0,,,,,,,,
3,EMULSIÓN DE SILICÓN,,10,0,,,,,,,,
4,CERA,,,3,0,,,,,,,,
5,FRAGANCIA,,0.2,0,,,,,,,,
,,TOTAL,100,0,,,,,,,,
"""
    }

    productos = {}
    current_producto = None
    current_area = None
    parsing_mp = False

    for filename, content in archivos_csv.items():
        reader = csv.reader(StringIO(content))
        for row in reader:
            row = [cell.strip() for cell in row]
            if not any(row):
                continue
            
            # Reemplazar valores vacíos para manejar correctamente los índices
            row_normalized = [cell if cell else '' for cell in row]
            
            # Búsqueda de nombre de producto
            if row_normalized[0] and not row_normalized[0].isdigit() and row_normalized[0].upper() not in ["TOTAL", "MATERIALES", "N°"]:
                current_producto = row_normalized[0].replace("(Kg):", "").strip()
                parsing_mp = False
                area_match = re.search(r"Área:,?(.+?),?", ",".join(row_normalized))
                if area_match:
                    area_raw = area_match.group(1).strip()
                    if "Clean" in area_raw:
                        current_area = "QUIMO CLEAN"
                    else:
                        current_area = "QUIMO"
                else:
                    current_area = "QUIMO"
                
                if current_producto not in productos:
                    productos[current_producto] = {'area': current_area, 'formulas': []}
                continue

            # Búsqueda del inicio de la sección de materias primas
            if "N°" in row_normalized and "Materia prima" in row_normalized:
                parsing_mp = True
                continue

            # Extracción de datos de materias primas
            if parsing_mp and current_producto:
                try:
                    if row_normalized[0].isdigit() and row_normalized[1] and "TOTAL" not in row_normalized[1].upper():
                        mp_nombre = row_normalized[1].strip()
                        
                        # Buscar el porcentaje en las celdas después del nombre de la MP
                        porcentaje_str = None
                        for cell in row_normalized[2:]:
                            if cell and is_float(cell):
                                porcentaje_str = cell
                                break
                        
                        if porcentaje_str is not None:
                            porcentaje = float(porcentaje_str)
                            productos[current_producto]['formulas'].append({'nombre': mp_nombre, 'porcentaje': porcentaje})
                except (ValueError, IndexError):
                    continue
    
    return productos

def is_float(value):
    """Verifica si una cadena puede ser convertida a float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def insertar_datos_en_bd(cursor, productos):
    """Inserta los datos extraídos en las tablas de la BD."""
    try:
        productos_existentes = {}
        materias_primas_existentes = {}

        # Cargar productos existentes
        cursor.execute("SELECT id_producto, nombre_producto FROM public.productos")
        for id_prod, nombre_prod in cursor.fetchall():
            productos_existentes[nombre_prod] = id_prod

        # Cargar materias primas existentes
        cursor.execute("SELECT id_mp, nombre_mp FROM public.materiasprimas")
        for id_mp, nombre_mp in cursor.fetchall():
            materias_primas_existentes[nombre_mp] = id_mp

        # Insertar nuevos productos
        for nombre_prod, data in productos.items():
            if nombre_prod and nombre_prod not in productos_existentes:
                area = data.get('area', 'QUIMO')
                insert_prod_query = "INSERT INTO public.productos (nombre_producto, unidad_medida_producto, area_producto, cantidad_producto, estatus_producto) VALUES (%s, 'KG', %s, 0, TRUE) RETURNING id_producto"
                cursor.execute(insert_prod_query, (nombre_prod, area))
                new_id = cursor.fetchone()[0]
                productos_existentes[nombre_prod] = new_id
                print(f"Producto insertado: {nombre_prod} con id {new_id}")

        # Insertar nuevas materias primas
        materias_primas_nuevas = set()
        for data in productos.values():
            for formula in data['formulas']:
                materias_primas_nuevas.add(formula['nombre'])
        
        for nombre_mp in materias_primas_nuevas:
            if nombre_mp and nombre_mp not in materias_primas_existentes:
                insert_mp_query = "INSERT INTO public.materiasprimas (nombre_mp, unidad_medida_mp, cantidad_comprada_mp, proveedor, costo_unitario_mp, tipo_moneda, total_mp, estatus_mp) VALUES (%s, 'KG', 0, 1, 0, 'MXN', 0, TRUE) RETURNING id_mp"
                cursor.execute(insert_mp_query, (nombre_mp,))
                new_id = cursor.fetchone()[0]
                materias_primas_existentes[nombre_mp] = new_id
                print(f"Materia prima insertada: {nombre_mp} con id {new_id}")

        # Insertar fórmulas
        for nombre_prod, data in productos.items():
            if nombre_prod in productos_existentes:
                id_producto = productos_existentes[nombre_prod]
                for formula in data['formulas']:
                    nombre_mp = formula['nombre']
                    porcentaje = formula['porcentaje']
                    
                    if nombre_mp in materias_primas_existentes:
                        id_mp = materias_primas_existentes[nombre_mp]
                        cursor.execute("SELECT id_formula_mp FROM public.formulas WHERE id_producto = %s AND id_mp = %s", (id_producto, id_mp))
                        if cursor.fetchone() is None:
                            insert_formula_query = "INSERT INTO public.formulas (id_producto, id_mp, porcentaje) VALUES (%s, %s, %s)"
                            cursor.execute(insert_formula_query, (id_producto, id_mp, porcentaje))
                            print(f"Fórmula insertada para el producto '{nombre_prod}' y materia prima '{nombre_mp}' con porcentaje {porcentaje}")

        conn.commit()
        print("\n¡Proceso de población de la base de datos completado exitosamente!")

    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print(f"\nError en la inserción de datos: {error}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    datos_extraidos = obtener_datos_csv()
    if datos_extraidos:
        insertar_datos_en_bd(cursor, datos_extraidos)