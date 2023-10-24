import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from tkinter import StringVar
from tkinter import colorchooser
from tkinter import messagebox
import serial
import threading
import csv
import time

# Constanten voor de kleuren
COLORS = ["blue", "red", "green", "purple"]

serial_port = 'COM15'
grid_columns = 50
group_size = 250  # Grootte van elke groep vierkantjes
modules = 120
grid_size = group_size*modules
grid_rows=int(grid_size/grid_columns)
square_size = 15  # Grootte van elk vierkantje
# Bereken het aantal groepen
num_groups = grid_size // group_size

# Schakelstanden voor elk vierkantje
switch_states = [0] * (grid_size)

# Lijst om bij te houden welke squares moeten worden geüpdatet en hun kleur
updateList = []
colourList = []

# Lijst om de huidige kleur van elk vierkant bij te houden
current_square_colors = ["blue"] * grid_size

def resize_canvas_to_group():
    canvas_height = square_size*(group_size/grid_columns)
    canvas.configure(scrollregion=canvas.bbox("all"), height=canvas_height)

# Functie om vierkantkleuren bij te werken
def update_square_colors():
    for i in range(grid_size):
        if i in updateList:
            canvas.itemconfig(square_widgets[i], fill=COLORS[colourList[updateList.index(i)]])
            current_square_colors[i] = COLORS[colourList[updateList.index(i)]]
        # Voeg anders de bestaande kleur toe
        else:
            canvas.itemconfig(square_widgets[i], fill=current_square_colors[i])

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
    square_tooltip_text = f"Switch {square-1}"

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
    # Functie om de data achter elkaar te plakken in de juiste volgorde

    # Zet de getallen om naar binaire representaties
    binary_num1 = convert_to_binary(num1)
    binary_num2 = convert_to_binary2(num2)

    # Combineer de binaire getallen
    combined_binary = binary_num1 + swap_last_two_bits(binary_num2)  # Wissel de laatste twee bits van binary_num2

    #display_data_on_labels(num1, num2, combined_binary)

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
                    num1 = int(row[0])
                    num2 = int(row[1])
                    if 0 <= num1 < grid_size and 0 <= num2 < len(COLORS):
                        updateList.append(num1)
                        colourList.append(num2)
                        ser.write(convert_data(num1, num2))
                    else:
                        messagebox.showerror("Fout", f"Ongeldige invoer in CSV-bestand op regel {csv_reader.line_num}")
                        ser.close()
                        return

            ser.close()
            end_time = time.time()  # Stop the timer
            elapsed_time = end_time - start_time
            label1.config(text=elapsed_time)
        update_square_colors()
        updateList.clear()  # Wis de lijst met update-vierkanten
        colourList.clear()  # Wis de lijst met kleuren

    except serial.SerialException as e:
         label.config(text=f"Error {str(e)}")

# Function to send manually entered data
def send_manual_data():
    try:
        start_time = time.time()  # Start the timer
        ser = serial.Serial(serial_port, baudrate=1843200)

        num1 = entry_num1.get()
        num2 = entry_num2.get()

        if num1 and num2:
            switch_num = int(num1)
            signal_num = int(num2)

            if 0 <= switch_num < grid_size and 0 <= signal_num < len(COLORS):
                updateList.append(switch_num)
                colourList.append(signal_num)
                # Stuur de gecombineerde binaire gegevens naar de seriële poort
                ser.write(convert_data(switch_num, signal_num))

                update_square_colors()
                updateList.clear()  # Wis de lijst met update-vierkanten
                colourList.clear()  # Wis de lijst met kleuren
                ser.close()
                end_time = time.time()  # Stop the timer
                elapsed_time = end_time - start_time
                label1.config(text=elapsed_time)
            else:
                label2.config(text="Invalid input: Switch number or signal out of range")
        else:
            label2.config(text="Invalid input: Both fields are required")
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
canvas = tk.Canvas(big_frame, width=canvas_width, height=square_size*(group_size/grid_columns), bg="white")
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
        square = canvas.create_rectangle(x0, y0, x1, y1, fill="blue", state="hidden")

        # Voeg de widget toe aan de lijst
        square_widgets.append(square)

        # Voeg tooltip toe met het nummer van het vakje als tekst
        square_tooltip_text = f"{i * grid_columns + j}"
        square_ids.append(square)  # Voeg het ID van het vierkant toe aan de lijst

        # Bind de tooltipfunctie aan het canvas om tooltips weer te geven wanneer de muiscursor zich boven de vierkanten bevindt
        canvas.tag_bind(square, "<Enter>", lambda e, square_id=square: show_square_tooltip_for_square(e, square_id))
        canvas.tag_bind(square, "<Leave>", hide_square_tooltip)
        canvas.tag_bind(square, "<Motion>", update_square_tooltips)

# Voeg gekleurde vakjes toe om de signalen weer te geven
color_boxes = []
colors = ["blue", "red", "green", "purple"]
for i, color in enumerate(colors):
    color_box = tk.Canvas(big_frame, width=30, height=30, bg=color)
    color_box.pack(side="left")  # Use pack to place color boxes side by side
    color_box.bind("<Button-1>", lambda event, signal=i: change_signal_color(signal))
    color_boxes.append(color_box)

# Functie om de kleur van een signaal te wijzigen
def change_signal_color(signal):
    # Use the colorchooser module to pick a color
    color = colorchooser.askcolor()[1]

    # Check if a color was selected (user didn't cancel the dialog)
    if color:
        colors[signal] = color
        COLORS[signal] = color
        color_boxes[signal].configure(bg=color)  # Update the color of the box

        # Update the color for all squares that use this signal
        for i in range(len(colourList)):
            if colourList[i] == signal:
                canvas.itemconfig(updateList[i], fill=color)
                current_square_colors[updateList[i]] = color
                
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
    resize_canvas_to_group()

# Functie om naar de vorige groep te schakelen
def previous_group():
    global current_group
    current_group = (current_group - 1) % num_groups
    show_current_group()
    resize_canvas_to_group()

# Voeg een functie toe om de huidige groep te wijzigen wanneer een nieuwe groep is geselecteerd in het dropdown-menu
def on_group_selection_change(event):
    global current_group
    current_group = group_selection.get()
    current_group = int(current_group)  # Zet de geselecteerde waarde om in een integer
    show_current_group()  # Toon de bijgewerkte groep
    resize_canvas_to_group()

# Maak een StringVar voor de dropdown selectie
group_selection = StringVar(root)
group_selection.set(str(current_group))  # Stel de standaard selectie in op de huidige groep

# Voeg een dropdown-menu toe
label7 = tk.Label(big_frame, text="Module number:")
label7.pack()
group_dropdown = ttk.Combobox(big_frame, textvariable=group_selection, values=[str(i) for i in range(num_groups)])
group_dropdown.bind("<<ComboboxSelected>>", on_group_selection_change)  # Voer de functie uit wanneer een nieuwe groep is geselecteerd
group_dropdown.pack()

# Standaard weergave van de huidige groep
show_current_group()

# Voeg nieuwe labels en entry widgets toe om de parameters in te stellen
label_grid_columns = tk.Label(big_frame, text="Grid Columns:")
label_grid_columns.pack()
entry_grid_columns = tk.Entry(big_frame)
entry_grid_columns.insert(0, grid_columns)  # Stel de standaardwaarde in
entry_grid_columns.pack()

label_group_size = tk.Label(big_frame, text="Group Size:")
label_group_size.pack()
entry_group_size = tk.Entry(big_frame)
entry_group_size.insert(0, group_size)  # Stel de standaardwaarde in
entry_group_size.pack()

label_modules = tk.Label(big_frame, text="Modules:")
label_modules.pack()
entry_modules = tk.Entry(big_frame)
entry_modules.insert(0, modules)  # Stel de standaardwaarde in
entry_modules.pack()

label_square_size = tk.Label(big_frame, text="Square Size:")
label_square_size.pack()
entry_square_size = tk.Entry(big_frame)
entry_square_size.insert(0, square_size)  # Stel de standaardwaarde in
entry_square_size.pack()

# Voeg een functie toe om de parameters bij te werken met de ingevoerde waarden
def update_parameters():
    global grid_columns, group_size, modules, square_size

    # Haal de ingevoerde waarden op uit de entry widgets
    grid_columns = int(entry_grid_columns.get())
    group_size = int(entry_group_size.get())
    modules = int(entry_modules.get())
    square_size = int(entry_square_size.get())

    # Bereken het aantal groepen en de grid-rijen opnieuw
    global grid_size, num_groups, grid_rows
    grid_size = group_size * modules
    num_groups = grid_size // group_size
    grid_rows = grid_size // grid_columns

    # Pas de grootte van het canvas aan
    canvas_width = grid_columns * square_size
    canvas_height = grid_rows * square_size
    canvas.config(width=canvas_width, height=canvas_height)
    show_current_group()
    resize_canvas_to_group()

# Voeg een updateknop toe om de parameters bij te werken
update_button = tk.Button(big_frame, text="Update Parameters", command=update_parameters)
update_button.pack()

# Start the main loop
root.mainloop()