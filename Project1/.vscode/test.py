import serial
import threading

def monitor_com_port(ser):
    try:
        print(f"Monitoring COM-poort {ser.port}. Druk op Ctrl+C om te stoppen.")

        while True:
            data = ser.read(1)  # Lees één byte
            if data:
                print(f"Ontvangen: {data.decode('utf-8')}")
            else:
                continue

    except KeyboardInterrupt:
        print("Monitoring gestopt.")
    except Exception as e:
        print(f"Fout: {e}")
    finally:
        if ser.is_open:
            ser.close()

def send_data(ser):
    try:
        print(f"Data verzenden naar COM-poort {ser.port}. Druk op Ctrl+C om te stoppen.")

        while True:
            data_to_send = input("Voer gegevens in om te verzenden: ")
            ser.write(data_to_send.encode('utf-8'))

    except KeyboardInterrupt:
        print("Verzenden gestopt.")
    except Exception as e:
        print(f"Fout: {e}")
    #finally:
        #if ser.is_open:
            #ser.close()

# Vervang 'COM15' met de juiste COM-poort en pas eventueel de baudrate aan
ser = serial.Serial('COM15', 1843200)

# Start de monitoring in een aparte thread en geef de ser aan elke thread door
monitor_thread = threading.Thread(target=monitor_com_port, args=(ser,))
monitor_thread.start()

# Start het verzenden van gegevens in de hoofdthread en geef de ser aan elke thread door
send_data(ser)
