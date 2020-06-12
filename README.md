# vision_for_robots_2020

### Requisitos

- Se debe tener instalado python3 en el sistema
- Se recomienda utilizar [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) para aislar el ambiente de desarrollo de la instalación de python global
    ``` bash
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

    ```
- Si no se utiliza un virtual environment, se pueden instalar las dependencias de la siguiente manera:
    ``` bash
    pip3 install -r requirements.txt

    ```

### Funcionamiento

#### Calibración de colores:

``` bash
python color_calibration.py
# Usar python3 si no se está usando un virtual environment
```

- Mostrar el color que se desea guardar
- Hacer click en las regiones que contienen el color
- Repetir el paso anterior haste que se considere que se tiene una muestra representativa
- Presionar la letra n del teclado y volver al primer paso
- Al haber capturado 2 colores, mantener presionada la letra q hasta que el proceso termine


#### Simulación de estacionamiento:

``` bash
python parking_navigator.py
# Usar python3 si no se está usando un virtual environment
```

- Mostrar a la camara 2 de las imagenes válidas
- Rotar la imágen alargada hasta llegar a la dirección inicial deseada
- Presionar la letra "q"
- Hacer click en la imágen del estacionamiento hasta seleccionar el espacio vacío deseado
- Presionar la letra "q"
- Esperar a que la simulación de la trayectoria termine
- Presionar la letra "q" para terminar el proceso o "n" para repetirlo
