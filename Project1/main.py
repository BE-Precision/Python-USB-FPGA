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

def serial_open():
    global ser
    ser = serial.Serial(serial_port, baudrate=9600)

def serial_close():
    ser.close()
    #test comment for commit

def selectFile():
   global file_path
   file_path = filedialog.askopenfilename()

# Function to send and receive data in a separate thread
def send_and_receive_data():
    try:
        start_time = time.time()  # Start the timer
        with open(file_path) as csv_file:
            global ser
            ser = serial.Serial(serial_port, baudrate=9600)
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                ser.write(row[0].encode())
                #response = ser.read(len(row[0].encode()))
                #response_decoded = response.decode('utf-8')
                #print(response)
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

# Create serial open button
button = tk.Button(root, text="Open Serial", command=serial_open)
button.pack()

# Create file selection button
button = tk.Button(root, text="Serial Close", command=serial_close)
button.pack()

# Create a label
label1 = tk.Label(root, text="Time Elapsed")
label1.pack(pady=20)

# Start the main loop
root.mainloop()
