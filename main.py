import io
import json
import logging
import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError

# Configuración básica de mensajes
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Configuración exacta de tu entorno de AWS
REGION = 'us-east-1'
BUCKET_NAME = 'practica1-karla'

# Inicializar cliente de S3
s3_client = boto3.client('s3', region_name=REGION)

def cargar_y_perfilar_s3(file_key, is_json=False):
    """
    Descarga archivos directamente a la memoria (RAM) desde AWS S3
    y genera un resumen estadístico de los datos.
    """
    print(f"\n==================================================")
    print(f" PROCESANDO ARCHIVO: {file_key}")
    print(f"==================================================")

    try:
        # Descarga desde S3 a memoria
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        body = response['Body'].read()

        # Carga del contenido usando BytesIO (sin guardar en disco)
        if is_json:
            data_json = json.loads(body.decode('utf-8'))
            df = pd.json_normalize(data_json)
        else:
            df = pd.read_csv(io.BytesIO(body))

        # Perfilamiento de datos
        print(f"\nDimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas\n")
        
        print("--- Resumen de Columnas y Valores Nulos ---")
        perfil = pd.DataFrame({
            'Tipo_Dato': df.dtypes,
            'Nulos': df.isnull().sum(),
            '%_Nulos': (df.isnull().sum() / len(df)) * 100
        })
        print(perfil)

        print("\n--- Estadísticos Descriptivos (Cuantitativos) ---")
        print(df.describe().T)

        return df

    except NoCredentialsError:
        print("\n[ERROR]: No se encontraron credenciales de AWS. Asegúrate de configurar tus credenciales.")
    except ClientError as e:
        codigo = e.response['Error']['Code']
        if codigo in ['404', 'NoSuchKey']:
            print(f"\n[ERROR]: El archivo '{file_key}' no existe en el bucket '{BUCKET_NAME}'.")
        elif codigo in ['403', 'AccessDenied']:
            print(f"\n[ERROR]: Acceso denegado o tus credenciales temporales han expirado.")
        else:
            print(f"\n[ERROR AWS]: {e}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO]: {e}")
    
    return None

if __name__ == "__main__":
    # Rutas exactas directo en la raíz del bucket
    df_transacciones = cargar_y_perfilar_s3('transacciones.csv', is_json=False)
    df_logs = cargar_y_perfilar_s3('logs_m2m.json', is_json=True)