import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
import serial
import threading
import csv
import time

# Constanten voor de kleuren
COLORS = ["blue", "red", "green", "purple"]

serial_port = 'COM24'
grid_rows = 10
grid_columns = 100
group_size = 1000  # Grootte van elke groep vierkantjes
grid_size = grid_rows * grid_columns
square_size = 15  # Grootte van elk vierkantje
# Bereken het aantal groepen
num_groups = grid_size // group_size

# Schakelstanden voor elk vierkantje
switch_states = [0] * (grid_rows * grid_columns)

#Lijst om te updaten squares bij te houden
updateList = []
colourList = []

# Functie om vierkantkleuren bij te werken
def update_square_colors(updateList, colourList):
    for i in updateList:
        canvas.itemconfig(updateList[i], fill=COLORS[int(colourList[i])])

# Voeg tooltips toe aan het canvas
tooltips = []  # Lijst om tooltips bij te houden

# Functie om tooltips te vernietigen wanneer de muiscursor het canvas verlaat
def hide_square_tooltip(event):
    for tooltip in tooltips:
        tooltip.destroy()
    tooltips.clear()

# Functie om een tooltip voor een specifiek vierkant weer te geven
def show_square_tooltip_for_square(event, square):
    x, y = event.x_root, event.y_root  # Gebruik x_root en y_root voor absolute schermcoördinaten
    square_tooltip_text = f"Square {square}"

    # Controleer eerst of er al een tooltip voor dit vierkant bestaat
    for tooltip in tooltips:
        if tooltip.square == square:
            return  # Tooltip bestaat al voor dit vierkant

    # Pas de positie aan om dichter bij de muis te zijn
    offset_x = 10
    offset_y = 10
    x += offset_x
    y += offset_y

    # Toon de tooltip in een Toplevel-venster
    tw = Toplevel(root)
    tw.wm_overrideredirect(1)
    tw.wm_geometry(f"+{x}+{y}")
    label = Label(tw, text=square_tooltip_text, justify=LEFT,
                  background="#ffffe0", relief=SOLID, borderwidth=1,
                  font=("tahoma", "8", "normal"))
    label.pack(ipadx=1)

    # Voeg de tooltip toe aan de lijst
    tooltips.append(tw)
    tw.square = square  # Voeg een attribuut 'square' toe aan het Toplevel-venster

# Functie om de tooltips voor het huidige vierkant te tonen en te verbergen voor anderen
def update_square_tooltips(event):
    x, y = event.x, event.y
    item = canvas.find_closest(x, y)
    current_square = item[0]

    # Toon de tooltip voor het huidige vierkant
    show_square_tooltip_for_square(event, current_square)

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

def convert_to_binary2(number):
    # Functie om een getal naar een binaire representatie om te zetten
    binary_str = format(int(number), '02b')  # Zorg voor een binaire reeks van 2 bits
    return binary_str

def swap_last_two_bits(binary_str):
    # Functie om de laatste twee bits van een binaire string om te wisselen
    if len(binary_str) >= 2:
        return binary_str[:-2] + binary_str[-1] + binary_str[-2]
    return binary_str

def display_data_on_labels(switch_num, signal_num, binary_data):
    label4.config(text=f"Switch number: {switch_num}")
    label5.config(text=f"Signal number: {signal_num}")
    label6.config(text=f"Binary data: {binary_data}")

def convert_data(num1, num2):
    # Functie om de data achterelkaar te plakken in de juiste volgorde

    # Zet de getallen om naar binaire representaties
    binary_num1 = convert_to_binary(num1)
    binary_num2 = convert_to_binary2(num2)

    # Combineer de binaire getallen
    combined_binary = binary_num1 + swap_last_two_bits(binary_num2)  # Wissel de laatste twee bits van binary_num2

    display_data_on_labels(num1, num2, combined_binary)

    myBytes = bytearray()
    
    
    for i in range(0, len(combined_binary), 8):
        chunk = combined_binary[i:i + 8]
        myBytes.append(int(chunk, 2))
    
    return myBytes



# Function to send and receive data in a separate thread
def send_and_receive_data():
    try:
        start_time = time.time()  # Start the timer
        with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
            global ser
            ser = serial.Serial(serial_port, baudrate=1843200)
            csv_reader = csv.reader(csv_file, delimiter=';')

            for row in csv_reader:
                if len(row) >= 2:  # Controleer of er minstens 2 kolommen in de rij zijn
                    num1 = row[0]
                    num2 = row[1]
                    updateList.append(int(row[0]))
                    colourList.append(int(row[1]))
                    # Stuur de gecombineerde binaire gegevens naar de seriële poort
                    ser.write(convert_data(num1, num2))
                    switch_states[int(num1)] = num2  # Werk de schakelstand bij

                    #time.sleep(2)
            
            ser.close()
            end_time = time.time()  # Stop the timer
            elapsed_time = end_time - start_time
            label1.config(text=elapsed_time)
            update_square_colors(updateList, colourList)
            updateList.clear()
            colourList.clear()

    except serial.SerialException as e:
         label.config(text=f"Error {str(e)}")

# Function to send manually entered data
def send_manual_data():
    try:
        start_time = time.time()  # Start the timer
        ser = serial.Serial(serial_port, baudrate=1843200)

        num1 = entry_num1.get()
        num2 = entry_num2.get()

        # Stuur de gecombineerde binaire gegevens naar de seriële poort
        ser.write(convert_data(num1, num2))
        
        switch_states[int(num1)] = num2  # Werk de schakelstand bij
        update_square_colors()
        ser.close()
        end_time = time.time()  # Stop the timer
        elapsed_time = end_time - start_time
        label1.config(text=elapsed_time)
    except serial.SerialException as e:
        label.config(text=f"Error {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Python test")
root.geometry("1200x800")  # Set the initial window size to 1920x1080 pixels

# Create A Main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)
# Create Frame for X Scrollbar
sec = Frame(main_frame)
sec.pack(fill=X, side=BOTTOM)
# Create A Canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
# Add A Scrollbars to Canvas
x_scrollbar = ttk.Scrollbar(sec, orient=HORIZONTAL, command=my_canvas.xview)
x_scrollbar.pack(side=BOTTOM, fill=X)
y_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
y_scrollbar.pack(side=RIGHT, fill=Y)
# Configure the canvas
my_canvas.configure(xscrollcommand=x_scrollbar.set)
my_canvas.configure(yscrollcommand=y_scrollbar.set)
my_canvas.bind("<Configure>", lambda e: my_canvas.config(scrollregion=my_canvas.bbox(ALL)))
# Create Another Frame INSIDE the Canvas
big_frame = Frame(my_canvas)
# Add that New Frame a Window In The Canvas
my_canvas.create_window((0, 0), window=big_frame, anchor="nw")
# Create a label
label = tk.Label(big_frame, text="FPGA TEST GUI")
label.pack(pady=20)

# Bereken de totale breedte en hoogte van het canvas
canvas_width = grid_columns * square_size
canvas_height = grid_rows * square_size

# Create a canvas for the grid of squares
canvas = tk.Canvas(big_frame, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Create square objects
square_ids = []
square_widgets = []  # Houd een lijst bij van de werkelijke widgetobjecten
for i in range(grid_rows):
    for j in range(grid_columns):
        x0 = j * square_size
        y0 = i * square_size
        x1 = x0 + square_size
        y1 = y0 + square_size
        square = canvas.create_rectangle(x0, y0, x1, y1, fill="blue", state="normal")

        # Voeg de widget toe aan de lijst
        square_widgets.append(square)

        # Voeg tooltip toe met het nummer van het vakje als tekst
        square_tooltip_text = f"{i * grid_columns + j}"
        square_ids.append(square)  # Voeg het ID van het vierkant toe aan de lijst

        # Bind de tooltipfunctie aan het canvas om tooltips weer te geven wanneer de muiscursor zich boven de vierkanten bevindt
        canvas.tag_bind(square, "<Enter>", lambda e, square_id=square: show_square_tooltip_for_square(e, square_id))
        canvas.tag_bind(square, "<Leave>", hide_square_tooltip)
        canvas.tag_bind(square, "<Motion>", update_square_tooltips)

# Create a button
button = tk.Button(big_frame, text="Send!", command=button_click)
button.pack()

# Create file selection button
button = tk.Button(big_frame, text="Select File", command=selectFile)
button.pack()

# Create a label
label1 = tk.Label(big_frame, text="Time Elapsed")
label1.pack(pady=20)

label2 = tk.Label(big_frame, text="Serial message")
label2.pack(pady=20)

# Create labels and entry fields for manual data entry
label_num1 = tk.Label(big_frame, text="Enter switch number (0-30000):")
label_num1.pack()
entry_num1 = tk.Entry(big_frame)
entry_num1.pack()

label_num2 = tk.Label(big_frame, text="Enter signal (0-3):")
label_num2.pack()
entry_num2 = tk.Entry(big_frame)
entry_num2.pack()

# Create a button to send manual data
button_send_manual = tk.Button(big_frame, text="Send Manual Data", command=send_manual_data)
button_send_manual.pack()

# Create a label
label3 = tk.Label(big_frame, text="Last sent data")
label3.pack()

label4 = tk.Label(big_frame, text="Switch number: ")
label4.pack()

label5 = tk.Label(big_frame, text="Signal number: ")
label5.pack()

label6 = tk.Label(big_frame, text="Binary data: ")
label6.pack()

# Aantal groepen en groepsgrootte
current_group = 0

# Functie om de huidige groep weer te geven
def show_current_group():
    start = current_group * group_size
    end = (current_group + 1) * group_size

    for i, square_id in enumerate(square_ids):
        if start <= i < end:
            canvas.itemconfig(square_id, state="normal")
        else:
            canvas.itemconfig(square_id, state="hidden")

# Functie om naar de volgende groep te schakelen
def next_group():
    global current_group
    current_group = (current_group + 1) % num_groups
    show_current_group()

# Functie om naar de vorige groep te schakelen
def previous_group():
    global current_group
    current_group = (current_group - 1) % num_groups
    show_current_group()

# Voeg knoppen toe om tussen groepen te schakelen
next_group_button = tk.Button(big_frame, text="Next Group", command=next_group)
next_group_button.pack()
previous_group_button = tk.Button(big_frame, text="Previous Group", command=previous_group)
previous_group_button.pack()

# Standaard weergave van de huidige groep
show_current_group()

# Start the main loop
root.mainloop()
