import tkinter as tk
from tkinter import filedialog
import serial
import threading
import csv
import time

serial_port = 'COM24'

# Function to be called when the button is clicked
def button_click():
    threading.Thread(target=send_and_receive_data).start()

def selectFile():
   global file_path
   file_path = filedialog.askopenfilename()

def convert_to_binary(number):
    # Functie om een getal naar een binaire representatie om te zetten
    binary_str = bin(int(number))[2:]
    return binary_str

def swap_last_two_bits(binary_str):
    # Functie om de laatste twee bits van een binaire string om te wisselen
    if len(binary_str) >= 2:
        return binary_str[:-2] + binary_str[-1] + binary_str[-2]
    return binary_str

# Function to send and receive data in a separate thread
def send_and_receive_data():
    try:
        start_time = time.time()  # Start the timer
        with open(file_path) as csv_file:
            global ser
            ser = serial.Serial(serial_port, baudrate=921600)
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if len(row) >= 2:  # Controleer of er minstens 2 kolommen in de rij zijn
                    num1 = row[0]
                    num2 = row[1]

                    # Zet de getallen om naar binaire representaties
                    binary_num1 = convert_to_binary(num1)
                    binary_num2 = convert_to_binary(num2)

                    # Combineer de binaire getallen
                    combined_binary = binary_num1 + swap_last_two_bits(binary_num2)  # Wissel de laatste twee bits van binary_num2

                    # Stuur de gecombineerde binaire gegevens naar de seriële poort
                    ser.write(combined_binary.encode())
            ser.close()
            end_time = time.time()  # Stop the timer
            elapsed_time = end_time - start_time
            label1.config(text=elapsed_time)
    except serial.SerialException as e:
        label.config(text=f"Error {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Python test")
root.geometry("300x400")  # Set the initial window size to 1920x1080 pixels

# Create a label
label = tk.Label(root, text="FPGA TEST GUI")
label.pack(pady=20)

# Create a button
button = tk.Button(root, text="Send!", command=button_click)
button.pack()

# Create file selection button
button = tk.Button(root, text="Select File", command=selectFile)
button.pack()

# Create a label
label1 = tk.Label(root, text="Time Elapsed")
label1.pack(pady=20)

# Start the main loop
root.mainloop()
