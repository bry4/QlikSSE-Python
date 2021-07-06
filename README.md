# Connectar Python a Qlik Sense - Ejemplo práctico
## Descripción:
Aprovechando las características de reporting de Qlik Sense (QS) y el uso de funciones matemáticas, estadisticas o generación de modelos Machine Learning en Python, se muestra un ejemplo práctico para poder conectar ambas herramientas en uno o múltiples ambientes.

## Requerimientos:
- Qlik Sense Desktop o Server
- Python 3.8 o Docker para ejecución en cualquier ambiente

## Conceptos:
La conexión entre QS y Python, se da con la librería gRPC en Python y el servicio Analytics Connection de Qlik Sense con el motor QIX.
- En el caso de la librería gRPC, Qlik tiene un repositorio donde ha construído la conexión el cuál podemos reutilizar: https://github.com/qlik-oss/server-side-extension
- En QS se tienen dos opciones, en Desktop se habilita la conexión mediante el archivo setting.ini dentro de la carpeta de QS y en Server se habilita creando un Analytics Connections en QMC; para ambos casos se detalla la ip del ambiente donde se levanto el la librería de Python y el puerto que se ha abierto.

## Instalación:
- Crear un ambiente de Python 3.8 e instalar las dependencias ```pip install -r requeriments.txt``` y ejecutar el archivo ```python ExtensionService_Models.py```
  -  En caso se tenga docker, solo ejecutar el archivo Makefile:
    -  ```make qlik-pysse-build``` Para construir la imagen
    -  ```make qlik-pysse-run```: Para correr la imagen en un contenedor y abrir el puerto a usar
- En Qlik Sense Desktop, copiar el archivo QVF a la carpeta apps de QS: ..Documents/Qlik/Sense/Apps/
- Dentro de la misma carpeta de Sense se encontrará el archivo settings.ini, agregar lo siguiente: **SSEPlugin=Model,localhost:50053**

    ![image](https://user-images.githubusercontent.com/11880722/124551423-b21f7a00-ddf7-11eb-86a1-70359337a2be.png)

  - SSEPlugin: Protocolo
  - Model: Nombre de la conexión que será usada en el app de QS
  - localhost: IP o nombre del servidor de Python
  - 50053: Puerto abierto del servidor Python

- En caso no se tenga respuesta de la llamada de QS desde Python, probar cerrando y abriendo QS. (El orden de ejecución es primero Python, luego QS)
- Imagen de confirmación de conexión establecida:

    ![image](https://user-images.githubusercontent.com/11880722/124553588-881b8700-ddfa-11eb-96c3-d2103b8105e6.png)

## Caso Práctico
- Se ha desarrollado usando un ejemplo práctico de kaggle para comparación de modelos analíticos como Random Forest y XGBoost: https://www.kaggle.com/nitinkhandagale/house-prediction-regression-model
- El cuál se ha implementado como funciones reutilizables dentro del poyecto sobre la librería gRPC que tiene Qlik para conectar con Python en su repositorio: https://github.com/qlik-oss/server-side-extension
- Esta implementación se construyó en base a las funciones que maneja esta librería para poder leer los datos desde Qlik Sense como input de la data para los modelos.
- Se demuestra dos formas de poder utilizar el potencial de la conexión:
  - Ejecución en batch mediante la corrida manual del app QS en la parte del Editor de Script, se llama a la función en Python que tiene el modelo:

    ![image](https://user-images.githubusercontent.com/11880722/124555316-94084880-ddfc-11eb-893a-9b458d6fd165.png)

  - Ejecución en tiempo real desde la hoja de gráfico (esto interacciona debido a cambios como filtros), llamando a la función en Python que tiene el modelo:

    ![image](https://user-images.githubusercontent.com/11880722/124555575-ddf12e80-ddfc-11eb-84fb-b1ac491a3189.png)

