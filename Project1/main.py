import tkinter as tk
import serial
import threading

serial_port = 'COM18'

# Function to be called when the button is clicked
def button_click():
    x1 = entry1.get()
    threading.Thread(target=send_and_receive_data, args=(x1,)).start()

# Function to send and receive data in a separate thread
def send_and_receive_data(x1):
    try:
        ser = serial.Serial(serial_port, baudrate=9600)
        message = x1
        ser.write(message.encode())
        x2 = ser.read(100)
        label.config(text=x2.decode())  # Decode received bytes to string
        ser.close()
    except serial.SerialException as e:
        label.config(text=f"Error: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Larger GUI")
root.geometry("1920x1080")  # Set the initial window size to 1920x1080 pixels

# Create a label
label = tk.Label(root, text="FPGA TEST GUI")
label.pack(pady=20)

# Create an input box
entry1 = tk.Entry(root)
entry1.pack()

# Create a button
button = tk.Button(root, text="Send!", command=button_click)
button.pack()

# Start the main loop
root.mainloop()
