import cmath

def z_to_rl(magnitude, phase):
    # Convert polar coordinates to rectangular coordinates
    impedance = cmath.rect(magnitude, phase)
    
    # Extract real and imaginary parts
    real_part = impedance.real
    imag_part = impedance.imag
    
    # Resistance (R) is the real part of impedance
    resistance = real_part
    
    # Reactance (X) is the imaginary part of impedance
    reactance = imag_part
    
    # For inductive reactance (L), X = jωL, where ω is angular frequency
    # For capacitive reactance (C), X = -1/(jωC)
    angular_frequency = 200000*3.14159  # Set an arbitrary value for angular frequency
    
    if reactance > 0:
        inductance = reactance / angular_frequency
        capacitance = None
    elif reactance < 0:
        capacitance = -1 / (reactance * angular_frequency)
        inductance = None
    else:
        inductance = capacitance = 0
    
    return resistance, inductance, capacitance

# Example usage
magnitude_Z = 1.564327*pow(10,4)
phase_rad = -1.594129

resistance, inductance, capacitance = z_to_rl(magnitude_Z, phase_rad)

print(f"Resistance (R): {resistance} Ohms")
print(f"Inductance (L): {inductance} Henrys")
print(f"Capacitance (C): {capacitance} Farads")
