import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from tkinter import StringVar
from tkinter import colorchooser
from tkinter import messagebox
from datetime import datetime
import serial
import threading
import csv
import time
from serial.tools import list_ports
import os
import json

# Constanten voor de kleuren
COLORS = []

# Functie om beschikbare COM-poorten op te halen
def get_available_com_ports():
    com_ports = [port.device for port in list_ports.comports()]
    return com_ports

# Functie om een COM-poort te selecteren
def select_com_port():
    com_ports = get_available_com_ports()
    if com_ports:
        port_selection.set(com_ports[0])  # Stel standaard de eerste beschikbare COM-poort in
        com_port_dropdown['values'] = com_ports

# Functie om de lijst met COM-poorten dynamisch bij te werken
def update_com_ports():
    com_ports = get_available_com_ports()
    
    if com_ports:
        # Ophalen van de huidige selectie
        current_selection = port_selection.get()
        
        # Huidige selectie is niet meer beschikbaar, selecteer een nieuwe COM-poort
        if current_selection not in com_ports:
            current_selection = com_ports[0] if com_ports else ""
        
        # Bijwerken van de dropdown-menu's
        for com_port_dropdown in dropdown_menus:
            com_port_dropdown['values'] = com_ports
            com_port_dropdown.set(current_selection)  # Stel de huidige selectie opnieuw in
        
        # Huidige selectie instellen
        port_selection.set(current_selection)
    else:
        # Geen beschikbare COM-poorten
        for com_port_dropdown in dropdown_menus:
            com_port_dropdown['values'] = []
            com_port_dropdown.set("")  # Wis de huidige selectie

        port_selection.set("")  # Wis de huidige selectie


# Functie om de COM-poort van een module op te halen
def get_com_port_for_module(module_number):
    # Haal de index op van de module in de module_frames-lijst
    index = module_number % len(module_frames)
    com_port_dropdown = module_frames[index][1]
    return com_port_dropdown.get()

grid_columns = 25
group_size = 250  # Grootte van elke groep vierkantjes
modules = 120
grid_size = group_size*modules
grid_rows=int(grid_size/grid_columns)
square_size = 15  # Grootte van elk vierkantje
width = 10
height = 10


def save_parameters_to_json():
    parameters = {
        "grid_columns": grid_columns,
        "group_size": group_size,
        "modules": modules,
        "square_size": square_size,
        "COLORS": COLORS,
        "width": width,
        "height": height
    }
    save_button.config(state=tk.DISABLED)
    try:
        with open("Project1\.vscode\settings.json", "w") as json_file:
            json.dump(parameters, json_file, indent=4)
        messagebox.showinfo("Settings are saved", "Settings are saved")
    except Exception as e:
        messagebox.showerror("Error while saving", f"An error occured when saving: {str(e)}")

def load_parameters_from_json():
    global grid_columns, group_size, modules, square_size, COLORS, width, height

    try:
        with open("Project1\.vscode\settings.json", "r") as json_file:
            parameters = json.load(json_file)
            grid_columns = parameters.get("grid_columns", grid_columns)
            group_size = parameters.get("group_size", group_size)
            modules = parameters.get("modules", modules)
            square_size = parameters.get("square_size", square_size)
            COLORS = parameters.get("COLORS", COLORS)
            width = parameters.get("width", width)
            height = parameters.get("height", height)
    except Exception as e:
        messagebox.showerror("Error while loading", f"An error occured while loading the settings: {str(e)}")

load_parameters_from_json()

# Bereken het aantal groepen
num_groups = grid_size // group_size

# Schakelstanden voor elk vierkantje
switch_states = [0] * (grid_size)


# Standaardkleur voor elk vierkant
default_color = 0  # Je kunt dit aanpassen aan je voorkeur

# Initialiseer de colourList met standaardkleuren voor alle vierkanten
colourList = []

# Lijst om bij te houden welke squares moeten worden geüpdatet en hun kleur
updateList = []

# Lijst om de huidige kleur van elk vierkant bij te houden
current_square_colors = [COLORS[0]] * grid_size

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

# Voeg een functie toe om een bestand te selecteren
def selectFile():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path and os.path.isfile(file_path) and file_path.lower().endswith(".csv"):
        file_label.config(text=f"Selected file: {os.path.basename(file_path)}")
        button.config(state=tk.NORMAL)  # Activeer de "Send" knop
    else:
        file_label.config(text="Selected file: Not yet selected")
        button.config(state=tk.DISABLED)  # Deactiveer de "Send" knop als er geen bestand is geselecteerd
        if file_path:
            messagebox.showerror("Error", "Select a valid CSV file")
            log_message("Error: Select a valid CSV file")

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

def convert_data(num1, num2):
    # Functie om de data achter elkaar te plakken in de juiste volgorde

    # Zet de getallen om naar binaire representaties
    binary_num1 = convert_to_binary(num1)
    binary_num2 = convert_to_binary2(num2)

    # Combineer de binaire getallen
    combined_binary = binary_num1 + swap_last_two_bits(binary_num2)  # Wissel de laatste twee bits van binary_num2

    myBytes = bytearray()

    if var.get()==1:
        log_message(f"Switch: {num1}, Signal: {num2}, Binary: {combined_binary}")
    
    for i in range(0, len(combined_binary), 8):
        chunk = combined_binary[i:i + 8]
        myBytes.append(int(chunk, 2))
    
    return myBytes

# Function to send and receive data in a separate thread
def send_and_receive_data():
    try:
        on_com_port_selection_change("<DummyEvent>")
        start_time = time.time()  # Start the timer
        with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
            global ser
            global serial_port
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
            label1.config(text=f"Time elapsed: {elapsed_time}")
        update_square_colors()
        updateList.clear()  # Wis de lijst met update-vierkanten
        colourList.clear()  # Wis de lijst met kleuren

    except FileNotFoundError:
        messagebox.showerror("Error", "The selected file doesn't exist.")
        log_message("Error: The selected file doesn't exist.")
    except Exception as e:
        messagebox.showerror("error", f"Error with file: {str(e)}")
        log_message(f"Error: Error with file: {str(e)}")

# Function to send manually entered data
def send_manual_data():
    try:
        on_com_port_selection_change("<DummyEvent>")
        start_time = time.time()  # Start the timer
        ser = serial.Serial(serial_port, baudrate=1843200)

        num1 = entry_num1.get()
        num2 = entry_num2.get()

        if num1 and num2:
            switch_num = int(num1)
            signal_num = int(num2)

            if 0 <= switch_num < (grid_size-1) and 0 <= signal_num < len(COLORS):
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
                label1.config(text=f"Time elapsed: {elapsed_time}")
            else:
                messagebox.showerror(text="Invalid input: Switch number or signal out of range")
                log_message("Invalid input: Switch number or signal out of range")
        else:
            messagebox.showerror(text="Invalid input: Both fields are required")
            log_message("Invalid input: Both fields are required")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        log_message(f"Error: {str(e)}")

def resize_window():
    global width
    global height
    # Haal de gewenste breedte en hoogte van main_frame op
    width = big_frame.winfo_reqwidth()+20
    height = big_frame.winfo_reqheight()+20
    
    # Pas de grootte van het venster aan
    root.geometry(f"{width}x{height}")

def switch_to_screen1():
    screen2.pack_forget()
    main_frame.pack()
    big_frame.pack()

def switch_to_screen2():
    main_frame.pack_forget()
    screen2.pack(side="left", anchor="nw", fill=BOTH, expand=1)

# Create the main window
root = tk.Tk()
root.title("BE Precision Technology - Probe Card Tester")
root.iconbitmap("Project1\.vscode\BEPTLogo.ico")
root.geometry(f"{width}x{height}")  # Set the initial window size to 1920x1080 pixels
root.configure(bg="white")

port_selection = StringVar(root)

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
big_frame = Frame(my_canvas, bg="white")
big_frame.grid()

# Voeg een zwarte balk toe aan de bovenkant van big_frame
black_frame = tk.Frame(big_frame, bg="grey20")
black_frame.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
custom_font = ("Microsoft JhengHei UI", 20, "bold")
custom_font2 = ("Microsoft JhengHei UI", 15, "bold")
text_label = tk.Label(black_frame, text="Probe Card Tester", fg="white", bg="grey20", font=custom_font)
text_label.pack(side="right", padx=10)
button1 = tk.Button(black_frame, text="Start", command=switch_to_screen1, bg="limegreen", font=custom_font2, fg="white")
button2 = tk.Button(black_frame, text="COM Port", command=switch_to_screen2, bg="deepskyblue", font=custom_font2, fg="white")
button1.pack(side="left")
button2.pack(side="left")

# Voeg een frame toe voor de linkerkant
left_frame = Frame(big_frame, bg="white")
left_frame.pack(side=LEFT, fill=BOTH, expand=1)

# Voeg een frame toe voor de rechterkant
right_frame = Frame(big_frame, bg="white")
right_frame.pack(side=RIGHT, fill=BOTH, expand=1)

# Voeg een blauwe balk toe aan de bovenkant van right_frame
top_right_frame = tk.Frame(right_frame, bg="RoyalBlue4")
top_right_frame.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg een blauwe balk toe aan de bovenkant van left_frame
top_left_frame = tk.Frame(left_frame, bg="RoyalBlue4")
top_left_frame.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
custom_font = ("Microsoft JhengHei UI", 20, "bold")
text_label = tk.Label(top_right_frame, text="Current Switch Signals", fg="white", bg="RoyalBlue4", font=custom_font)
text_label.pack(side="left", padx=10)

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
custom_font = ("Microsoft JhengHei UI", 20, "bold")
text_label = tk.Label(top_left_frame, text="Send Data", fg="white", bg="RoyalBlue4", font=custom_font)
text_label.pack(side="left", padx=10, pady=(5,5))

# Add that New Frame a Window In The Canvas
my_canvas.create_window((0, 0), window=big_frame, anchor="nw")

# Bereken de totale breedte en hoogte van het canvas
canvas_width = grid_columns * square_size
canvas_height = grid_rows * square_size

squares_frame = tk.Frame(right_frame, bg="white")
squares_frame.pack()

# Create a canvas for the grid of squares
canvas = tk.Canvas(squares_frame, width=canvas_width, height=square_size*(group_size/grid_columns), bg="white")

# Create square objects
square_ids = []
square_widgets = []  # Houd een lijst bij van de werkelijke widgetobjecten
for i in range(grid_rows):
    for j in range(grid_columns):
        x0 = j * square_size
        y0 = i * square_size
        x1 = x0 + square_size
        y1 = y0 + square_size
        square = canvas.create_rectangle(x0, y0, x1, y1, fill=COLORS[0], state="hidden")

        # Voeg de widget toe aan de lijst
        square_widgets.append(square)

        # Voeg tooltip toe met het nummer van het vakje als tekst
        square_tooltip_text = f"{i * grid_columns + j}"
        square_ids.append(square)  # Voeg het ID van het vierkant toe aan de lijst

        # Bind de tooltipfunctie aan het canvas om tooltips weer te geven wanneer de muiscursor zich boven de vierkanten bevindt
        canvas.tag_bind(square, "<Enter>", lambda e, square_id=square: show_square_tooltip_for_square(e, square_id))
        canvas.tag_bind(square, "<Leave>", hide_square_tooltip)
        canvas.tag_bind(square, "<Motion>", update_square_tooltips)

canvas.pack(side="left", pady=2, padx=2)

color_boxes = []
color_frame = tk.Frame(squares_frame, bg="white")
color_frame.pack(side="right")

color_labels = ["Signaal 1", "Signaal 2", "Signaal 3", "Signaal 4"]

for i, (color, label) in enumerate(zip(COLORS, color_labels)):
    signal_frame = tk.Frame(color_frame, bg="white")
    signal_frame.pack(side="top")  # Plaats de frame voor elk signaal boven elkaar

    color_box = tk.Canvas(signal_frame, width=30, height=30, bg=color)
    color_box.pack(side="left")  # Plaats het kleurvak links in het frame
    color_box.bind("<Button-1>", lambda event, signal=i: change_signal_color(signal))
    color_boxes.append(color_box)

    color_label = tk.Label(signal_frame, text=label, bg="white")
    color_label.pack(side="left", padx=(0,10))  # Plaats het label links in het frame

def update_all_square_colors():
    for i in range(len(square_widgets)):
        square_id = square_widgets[i]
        canvas.itemconfig(square_id, fill=COLORS[colourList[i]])

# Functie om de kleur van een signaal te wijzigen
def change_signal_color(signal):
    # Use the colorchooser module to pick a color
    color = colorchooser.askcolor()[1]

    # Check if a color was selected (user didn't cancel the dialog)
    if color:
        old_color = COLORS[signal]
        COLORS[signal] = color
        color_boxes[signal].configure(bg=color)  # Update the color of the box

        # Werk de kleur van de vierkanten bij voor alle vierkanten met de oude kleur
        for i in range(len(current_square_colors)):
            if current_square_colors[i] == old_color:
                canvas.itemconfig(square_widgets[i], fill=color)
                current_square_colors[i] = color

# Functie om periodiek de COM-poorten bij te werken
def update_com_ports_periodically():
    update_com_ports()
    root.after(1000, update_com_ports_periodically)  # Herhaal elke 5 seconden

file_frame = tk.Frame(left_frame, bg="white")
file_frame.pack(pady=(10,0))

# Create file selection button
button = tk.Button(file_frame, text="Select File", command=selectFile)
button.pack(side="left", padx=(10,0))

# Voeg een label toe om de bestandsnaam weer te geven
file_label = tk.Label(file_frame, text="Selected file: Not yet selected", bg="white")
file_label.pack(side="left")

# Create a button
button = tk.Button(left_frame, text="Send!", command=button_click)
if file_label.cget("text") == "Geselecteerd bestand: Nog niet geselecteerd":
    button.config(state=tk.DISABLED)  # Deactiveer de knop
button.pack()

# Create a label
label1 = tk.Label(left_frame, text="Time elapsed: 0", bg="white")
label1.pack(pady=20)

# Voeg een blauwe balk toe aan de bovenkant van left_frame
top_left_frame2 = tk.Frame(left_frame, bg="RoyalBlue4")
top_left_frame2.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
text_label = tk.Label(top_left_frame2, text="Manual Data", fg="white", bg="RoyalBlue4", font=custom_font)
text_label.pack(side="left", padx=10, pady=5)

# Create labels and entry fields for manual data entry
switch_frame = tk.Frame(left_frame, bg="white")
switch_frame.pack(pady=(10,5))
label_num1 = tk.Label(switch_frame, text=f"Enter switch number (0-{group_size*modules-1}):", bg="white", width=23)
label_num1.pack(side="left")
entry_num1 = tk.Entry(switch_frame)
entry_num1.pack(side="left")

signal_frame = tk.Frame(left_frame, bg="white")
signal_frame.pack(pady=5)
label_num2 = tk.Label(signal_frame, text="Enter signal (0-3):                       ", bg="white")
label_num2.pack(side="left")
entry_num2 = tk.Entry(signal_frame)
entry_num2.pack(side="left")

def reset_all():
    try:
        on_com_port_selection_change("<DummyEvent>")
        ser = serial.Serial(serial_port, baudrate=1843200)
        ser.write(convert_data(32767, 3))

        # Werk de kleur van de vierkanten bij voor alle vierkanten met de oude kleur
        for i in range(len(current_square_colors)):
            canvas.itemconfig(square_widgets[i], fill=COLORS[0])
            current_square_colors[i] = COLORS[0]
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        log_message(f"Error: {str(e)}")

button_frame = tk.Frame(left_frame, bg="white")
button_frame.pack(pady=(5,20))

# Create a button to send manual data
button_send_manual = tk.Button(button_frame, text="Send Manual Data", command=send_manual_data)
button_send_manual.pack(side="left")

# Create a button to send manual data
reset_all_button = tk.Button(button_frame, text="Reset All", command=reset_all)
reset_all_button.pack(side="left", padx=20)

# Voeg een blauwe balk toe aan de bovenkant van left_frame
top_left_frame3 = tk.Frame(left_frame, bg="RoyalBlue4")
top_left_frame3.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
text_label = tk.Label(top_left_frame3, text="Settings", fg="white", bg="RoyalBlue4", font=custom_font)
text_label.pack(side="left", padx=10, pady=5)

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

# Voeg een functie toe om de waarden in de uitklapbare lijst dynamisch te genereren
def generate_group_dropdown_values():
    values = [str(i) for i in range(num_groups)]
    group_selection.set(str(current_group))  # Stel de geselecteerde waarde in op de huidige groep
    group_dropdown['values'] = values  # Update de waarden in de uitklapbare lijst

# Creëer de uitklapbare lijst met module nummers
number_frame = tk.Frame(right_frame, bg="white")
number_frame.pack(pady=(0,20))
label7 = tk.Label(number_frame, text="Module number:", bg="white")
label7.pack(side="left", anchor="nw")
group_dropdown = ttk.Combobox(number_frame, textvariable=group_selection, state="readonly")
generate_group_dropdown_values()  # Genereer de waarden voor de uitklapbare lijst
group_dropdown.bind("<<ComboboxSelected>>", on_group_selection_change)  # Voer de functie uit wanneer een nieuwe groep is geselecteerd
group_dropdown.pack(side="left", anchor="nw")

# Standaard weergave van de huidige groep
show_current_group()

# Voeg nieuwe labels en entry widgets toe om de parameters in te stellen
columns_frame = tk.Frame(left_frame, bg="white")
columns_frame.pack(pady=(10,5))
label_grid_columns = tk.Label(columns_frame, text="Grid Columns:", bg="white")
label_grid_columns.pack(side="left")
entry_grid_columns = tk.Entry(columns_frame)
entry_grid_columns.insert(0, grid_columns)  # Stel de standaardwaarde in
entry_grid_columns.pack(side="left")

group_frame = tk.Frame(left_frame, bg="white")
group_frame.pack(pady=(5))
label_group_size = tk.Label(group_frame, text="Group Size:      ", bg="white")
label_group_size.pack(side="left")
entry_group_size = tk.Entry(group_frame)
entry_group_size.insert(0, group_size)  # Stel de standaardwaarde in
entry_group_size.pack(side="left")

modules_frame = tk.Frame(left_frame, bg="white")
modules_frame.pack(pady=(5))
label_modules = tk.Label(modules_frame, text="Modules:         ", bg="white")
label_modules.pack(side="left")
entry_modules = tk.Entry(modules_frame)
entry_modules.insert(0, modules)  # Stel de standaardwaarde in
entry_modules.pack(side="left")

size_frame = tk.Frame(left_frame, bg="white")
size_frame.pack(pady=(5))
label_square_size = tk.Label(size_frame, text="Square Size:    ", bg="white")
label_square_size.pack(side="left")
entry_square_size = tk.Entry(size_frame)
entry_square_size.insert(0, square_size)  # Stel de standaardwaarde in
entry_square_size.pack(side="left")

def rearrange_squares():
    # Herverdeel de vierkanten op het nieuwe raster
    for i in range(grid_rows):
        for j in range(grid_columns):
            x0 = j * square_size
            y0 = i * square_size
            x1 = x0 + square_size
            y1 = y0 + square_size
            canvas.coords(square_widgets[i * grid_columns + j], x0, y0, x1, y1)

# Voeg een functie toe om de parameters bij te werken met de ingevoerde waarden
def update_parameters():
    global grid_columns, group_size, modules, square_size
    
    # Haal de oude waarden op voor het geval dat validatie mislukt
    old_grid_columns = grid_columns
    old_group_size = group_size

    # Haal de ingevoerde waarden op uit de entry widgets
    grid_columns = int(entry_grid_columns.get())
    group_size = int(entry_group_size.get())

    if group_size % grid_columns != 0:
        messagebox.showerror("Ongeldige invoer", "group_size / grid_columns moet een geheel getal zijn.")
        # Herstel de vorige waarden
        entry_grid_columns.delete(0, END)
        entry_group_size.delete(0, END)
        entry_grid_columns.insert(0, old_grid_columns)
        entry_group_size.insert(0, old_group_size)
        grid_columns = old_grid_columns
        group_size = old_group_size
        return

    modules = int(entry_modules.get())
    square_size = int(entry_square_size.get())

    # Bereken het aantal groepen en de grid-rijen opnieuw
    global grid_size, num_groups, grid_rows
    grid_size = group_size * modules
    num_groups = grid_size // group_size
    grid_rows = grid_size // grid_columns
    
    label_num1.config(text=f"Enter switch number (0-{group_size*modules-1}):")
    
    # Pas de grootte van het canvas aan
    canvas_width = grid_columns * square_size
    canvas_height = grid_rows * square_size
    canvas.config(width=canvas_width, height=canvas_height)
    show_current_group()
    resize_canvas_to_group()
    rearrange_squares()

    save_button.config(state=tk.NORMAL)

    # Controleer of de geselecteerde module groter is dan het nieuwe aantal modules
    global current_group
    if current_group >= modules:
        current_group = 0  # Zet de geselecteerde module terug naar 0 als deze groter is dan het nieuwe aantal modules

    # Roep de functie aan om de waarden in de uitklapbare lijst bij te werken
    generate_group_dropdown_values()
    on_group_selection_change("<DummyEvent>")
    resize_window()

# Voeg een updateknop toe om de parameters bij te werken
buttons_frame = tk.Frame(left_frame, bg="white")
buttons_frame.pack(pady=(10,5))
update_button = tk.Button(buttons_frame, text="Update Settings", command=update_parameters)
update_button.pack(side="left", padx=(0,20))

save_button = tk.Button(buttons_frame, text="Save", command=save_parameters_to_json, state=tk.DISABLED)
save_button.pack(side="left")

# Voeg een blauwe balk toe aan de bovenkant van left_frame
top_right_frame2 = tk.Frame(right_frame, bg="RoyalBlue4")
top_right_frame2.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
text_label = tk.Label(top_right_frame2, text="Log", fg="white", bg="RoyalBlue4", font=custom_font)
text_label.pack(side="left", padx=10, pady=0)

# Voeg een Scrollbar toe voor de Log
log_scrollbar = ttk.Scrollbar(right_frame, orient=VERTICAL)
log_scrollbar.pack(side=RIGHT, fill=Y)

# Maak een Text-widget voor de log en koppel deze aan de scrollbar
log_text = tk.Text(right_frame, wrap=WORD, yscrollcommand=log_scrollbar.set, height=15, bg="lavender")
log_text.pack(expand=True, fill=X, padx=20)

# Functie om tekst aan de log toe te voegen
def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Genereer een timestamp
    log_text.insert(END, f"[{current_time}] {message}\n")  # Voeg timestamp toe aan het bericht
    log_text.see(END)  # Zorg ervoor dat de scrollbar automatisch naar de onderkant schuift om de nieuwste berichten te tonen

# Functie om de log op te slaan
def save_log():
    # Vraag de gebruiker om een bestandslocatie te selecteren en een bestandsnaam in te voeren
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])

    if file_path:
        # Schrijf de log naar het geselecteerde bestand
        with open(file_path, 'w') as file:
            file.write(log_text.get("1.0", "end"))

# Functie om de log te resetten
def reset_log():
    log_text.delete("1.0", "end")

var = tk.IntVar(value=0)
# Maak het selectievakje en koppel het aan de variabele var
log_data = tk.Checkbutton(right_frame, text="Log send data (very slow)", variable=var, bg="white")
log_data.pack(side="left", padx=20)

save_log_button = tk.Button(right_frame, text="Save Log", command=save_log)
save_log_button.pack(side="left")

# Knop om de log te resetten
reset_button = tk.Button(right_frame, text="Reset Log", command=reset_log)
reset_button.pack(side="left", padx=20)

# Verbind de scrollbar met de Text-widget
log_scrollbar.config(command=log_text.yview)

# Maak scherm 2
screen2 = tk.Frame(root)
screen2.grid_remove()

# Create Frame for X Scrollbar
sec2 = Frame(screen2)
sec2.pack(fill=X, side=BOTTOM)
# Create A Canvas
my_canvas2 = Canvas(screen2)
my_canvas2.pack(side=LEFT, fill=BOTH, expand=1)
# Add A Scrollbars to Canvas
x_scrollbar2 = ttk.Scrollbar(sec2, orient=HORIZONTAL, command=my_canvas2.xview)
x_scrollbar2.pack(side=BOTTOM, fill=X)
y_scrollbar2 = ttk.Scrollbar(screen2, orient=VERTICAL, command=my_canvas2.yview)
y_scrollbar2.pack(side=RIGHT, fill=Y)
# Configure the canvas
my_canvas2.configure(xscrollcommand=x_scrollbar.set)
my_canvas2.configure(yscrollcommand=y_scrollbar.set)
my_canvas2.bind("<Configure>", lambda e: my_canvas2.config(scrollregion=my_canvas2.bbox(ALL)))
# Create Another Frame INSIDE the Canvas
big_frame2 = Frame(my_canvas2, bg="white")
big_frame2.grid()

# Voeg een zwarte balk toe aan de bovenkant van big_frame
black_frame = tk.Frame(big_frame2, bg="grey20")
black_frame.pack(side="top", fill="x")  # Stel in dat het de hele breedte beslaat

# Voeg witte tekst toe aan de zwarte balk aan de rechterkant
text_label = tk.Label(black_frame, text="Probe Card Tester", fg="white", bg="grey20", font=custom_font)
text_label.pack(side="right", padx=10)
button1 = tk.Button(black_frame, text="Start", command=switch_to_screen1, bg="limegreen", font=custom_font2, fg="white")
button2 = tk.Button(black_frame, text="COM Port", command=switch_to_screen2, bg="deepskyblue", font=custom_font2, fg="white")
button1.pack(side="left")
button2.pack(side="left")

# Maak een frame voor de module dropdowns
modules_frame = tk.Frame(big_frame2)
modules_frame.pack()

# Voeg labels en dropdown-menu's toe voor modules

module_frames = []
dropdown_menus = []

for i in range(20):
    for j in range(6):
        frame_com = tk.Frame(modules_frame)
        frame_com.grid(row=i, column=j, padx=5, pady=5)  # Gebruik .grid om frames in het raster te plaatsen
        label_module = tk.Label(frame_com, text=f"Module {i*6 + j}")  # Berekent de juiste module-index
        label_module.pack(side="left")
        com_port_dropdown = ttk.Combobox(frame_com, values=get_available_com_ports(), state="readonly")
        com_port_dropdown.pack(side="left")
        module_frames.append((label_module, com_port_dropdown))
        dropdown_menus.append(com_port_dropdown)

update_com_ports_periodically()

# Start the main loop
root.mainloop()