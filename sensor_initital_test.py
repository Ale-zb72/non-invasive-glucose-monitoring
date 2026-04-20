from machine import SoftI2C, Pin, I2C
from time import sleep
import time
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM

# Configuración del I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16))

def reset_sensor(reset_pin_number):
    # Configurar el pin de reinicio como salida
    reset_pin = Pin(reset_pin_number, Pin.OUT)
    
    # Establecer el pin en alto para activar el sensor
    reset_pin.value(1)
    print(f"Reset pin {reset_pin_number} set to HIGH. Waiting for 2 minutes...")
    
    # Establecer el pin en bajo para completar el reinicio
    reset_pin.value(0)
    print(f"Reset pin {reset_pin_number} set to LOW. Sensor reset complete.")

def read_channel(channel, reset_pin_number):

    i2c.writeto(0x70, channel)
    i2c.scan()
    reset_sensor(reset_pin_number)
    
    sensor = MAX30102(i2c=i2c)  # Se requiere una instancia de I2C

    if sensor.i2c_address not in i2c.scan():
        print(f"Sensor no encontrado en el canal {channel}.")
        return
    elif not (sensor.check_part_id()):
        print(f"ID de dispositivo I2C no corresponde a MAX30102 o MAX30105 en el canal {channel}.")
        return
    else:
        print(f"Sensor en el canal {channel} conectado y reconocido.")

    print(f"Configurando sensor en el canal {channel} con configuración predeterminada.", '\n')
    sensor.setup_sensor()

    sensor.set_sample_rate(400)
    sensor.set_fifo_average(8)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    sleep(1)
    
    print(f"Iniciando adquisición de datos del canal {channel} de los registros RED & IR...", '\n')
    sleep(1)

    start_time = time.time()
    while time.time() - start_time < 10:  # Leer datos durante 10 segundos
        sensor.check()

        if sensor.available():
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()

            print(f"Canal {channel} - red_reading: {red_reading}, ir_reading: {ir_reading}")
    
    # Apagar el sensor al finalizar la lectura
    sensor.shutdown()  # Método de apagado del sensor
    
def main():
    canales = [(b'\x01', 18), (b'\x02', 19), (b'\x04', 20), (b'\x08', 21)]  # Tupla de (canal, pin_reset)
    for canal, pin_reset in canales:
        read_channel(canal, pin_reset)

if _name_ == '_main_':
    main()