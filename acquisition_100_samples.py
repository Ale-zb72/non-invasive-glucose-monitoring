from machine import SoftI2C, Pin
from time import sleep, time
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM

# Configuración del I2C
i2c = SoftI2C(sda=Pin(16), scl=Pin(17), freq=100000)  # Frecuencia de I2C comúnmente usada es 100kHz

def reset_sensor(reset_pin_number):
    reset_pin = Pin(reset_pin_number, Pin.OUT)
    reset_pin.value(1)
    sleep(0.001)  # Esperar un poco para que el reset sea efectivo (ajustado a 10ms)
    reset_pin.value(0)
    sleep(0.001)  # Reducir el retardo para agilizar el reinicio (ajustado a 10ms)

def read_channel(sensor, channel, datos_red, datos_ir):
    i2c.writeto(0x70, channel)
    sleep(0.001)  # Esperar un poco para asegurar que el canal esté configurado (ajustado a 10ms)
    
    sensor.check()
    
    if sensor.available():
        red_reading = sensor.pop_red_from_storage()
        ir_reading = sensor.pop_ir_from_storage()
        datos_red.append(red_reading)
        datos_ir.append(ir_reading)

def main():
    canales = [b'\x01', b'\x02', b'\x04', b'\x08']
    reset_pins = [18, 19, 20, 21]
    
    # Comprobación de dispositivos I2C
    dispositivos = i2c.scan()
    if 0x57 not in dispositivos:
        print("Sensor MAX30102 no encontrado en la dirección 0x57")
        return
    
    datos_red_canal1 = []
    datos_ir_canal1 = []
    datos_red_canal2 = []
    datos_ir_canal2 = []
    datos_red_canal3 = []
    datos_ir_canal3 = []
    datos_red_canal4 = []
    datos_ir_canal4 = []

    canal_datos = [
        (datos_red_canal1, datos_ir_canal1),
        (datos_red_canal2, datos_ir_canal2),
        (datos_red_canal3, datos_ir_canal3),
        (datos_red_canal4, datos_ir_canal4)
    ]

    muestras_por_sensor = 1000  # Número total de muestras
    muestras_totales = muestras_por_sensor * 4  # 4000 Muestras en total por los 4 sensores
    tiempo_total_segundos = 60  # Tiempo total en segundos (60 segundos)
    intervalo = tiempo_total_segundos / muestras_totales  # Intervalo calculado en segundos

    # Contador de tiempo
    tiempo_inicio = time()
    
    for muestra in range(muestras_totales):
        canal = canales[muestra % len(canales)]
        reset_pin = reset_pins[muestra % len(reset_pins)]
        
        # Reiniciar el sensor para cada canal
        reset_sensor(reset_pin)
        
        # Inicializar sensor
        sensor = MAX30102(i2c=i2c)
        sensor.setup_sensor()
        sensor.set_sample_rate(400)  # Ajustado a la tasa máxima soportada
        sensor.set_fifo_average(8)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
        
        read_channel(sensor, canal, canal_datos[muestra % len(canales)][0], canal_datos[muestra % len(canales)][1])
        #sleep(intervalo)  # Esperar el intervalo calculado antes de tomar la siguiente muestra

    # Contador de tiempo
    tiempo_fin = time()
    tiempo_total = tiempo_fin - tiempo_inicio
    print(f"Tiempo total de muestreo: {tiempo_total:.2f} segundos")
    
    # Guardar los datos en un solo archivo CSV
    with open("datos.csv", "w") as f:
        # Escribir encabezados
        f.write("Red Canal 1,IR Canal 1,Red Canal 2,IR Canal 2,Red Canal 3,IR Canal 3,Red Canal 4,IR Canal 4\n")
        
        # Obtener la longitud máxima de las listas de datos
        max_length = max(len(datos_red_canal1), len(datos_red_canal2), len(datos_red_canal3), len(datos_red_canal4))
        
        for i in range(max_length):
            row = [
                str(datos_red_canal1[i]) if i < len(datos_red_canal1) else '',
                str(datos_ir_canal1[i]) if i < len(datos_ir_canal1) else '',
                str(datos_red_canal2[i]) if i < len(datos_red_canal2) else '',
                str(datos_ir_canal2[i]) if i < len(datos_ir_canal2) else '',
                str(datos_red_canal3[i]) if i < len(datos_red_canal3) else '',
                str(datos_ir_canal3[i]) if i < len(datos_ir_canal3) else '',
                str(datos_red_canal4[i]) if i < len(datos_red_canal4) else '',
                str(datos_ir_canal4[i]) if i < len(datos_ir_canal4) else ''
            ]
            f.write(','.join(row) + '\n')

    # Imprimir datos
    print("Datos RED canal 1:", datos_red_canal1)
    print("Datos IR canal 1:", datos_ir_canal1)
    print("Datos RED canal 2:", datos_red_canal2)
    print("Datos IR canal 2:", datos_ir_canal2)
    print("Datos RED canal 3:", datos_red_canal3)
    print("Datos IR canal 3:", datos_ir_canal3)
    print("Datos RED canal 4:", datos_red_canal4)
    print("Datos IR canal 4:", datos_ir_canal4)

if __name__ == '__main__':
    main()