import py_dss_interface
import numpy as np
import random
import time
import matplotlib.pyplot as plt

def add_ev_chargers(num_ev_stations):
    dss = py_dss_interface.DSS()
    dssFile = r"C:\Users\jilli\OneDrive - University of Pittsburgh\Desktop\ECE 1893\OpenDss_Basics\13Bus\IEEE13Nodeckt.dss"
    dss.text(f"compile [{dssFile}]")

    # Define ZIPV coefficients
    zipv_coeffs = "(0.1824, 0.9949, -0.1773, 8.917, -12.91, 4.993, 0.85)"

    # List of candidate buses for EV charging
    candidate_buses = ['671.1.2.3', '634.1', '634.2', '634.3','645.2', '646.2.3','692.3.1','675.1','675.2','675.3','611.3','652.1','670.1','670.2','670.3']

    # Randomly select buses to place EV chargers
    selected_buses = random.choices(candidate_buses, k=num_ev_stations)

    # File path for DistLoads file where load definitions are saved
    distloads_file = r"C:\Users\jilli\OneDrive - University of Pittsburgh\Desktop\ECE 1893\OpenDss_Basics\13Bus\DistLoads.dss"

    with open(distloads_file, "w") as file:
        for i, bus in enumerate(selected_buses, 1):
            ev_kw = random.uniform(3.3, 19.2)

            # Determine the kV for each bus from system configuration
            if bus in ['671.1.2.3', '646.2.3', '692.3.1']:
                bus_kv = 4.16
            elif bus in ['634.1', '634.2', '634.3']:
                bus_kv = 0.277
            elif bus in ['645.2']:
                bus_kv = 2.4
            else:
                bus_kv = 2.4

            # Generate the load name and write the load definition to the file
            name = f"DL_{i}"
            file.write(
                f"new load.{name} bus1={bus} phases=1 kV={bus_kv} kW={ev_kw:.2f} PF=.95 model=8 ZIPV={zipv_coeffs}\n")

    print(f"DistLoads file has been written to {distloads_file}")
    dss.text(f"compile [{distloads_file}]")

    dss.text("Solve")

    # Wait for 30 seconds before proceeding with the next run
    #time.sleep(30)  # Wait for 30 seconds

    dss.text("Show Voltage LN Nodes")

    file_path = r"C:\Users\jilli\OneDrive - University of Pittsburgh\Desktop\ECE 1893\OpenDss_Basics\13Bus\IEEE13Nodeckt_VLN_Node.Txt"

    bus_data = {}  # Dictionary to hold bus: [pu1, pu2, pu3]

    with open(file_path, 'r') as file:
        lines = file.readlines()[5:]  # Skip first 6 lines
        current_bus = None
        phase_index = 0
        for line in lines:
            parts = line.split()
            try:
                pu_value = float(parts[-1])
            except ValueError:
                continue
            # Detect a new bus (line does not start with a dash)
            if not line.lstrip().startswith('-'):
                current_bus = parts[0]
                bus_data[current_bus] = [None, None, None]
                phase_index = 0
            else:
                phase_index += 1
            if current_bus is not None and phase_index < 3:
                bus_data[current_bus][phase_index] = pu_value

                if pu_value > 3:
                    bus_data[current_bus][phase_index] = None

    # Display results
    for bus, pu_vals in bus_data.items():
        if bus == '645':
            pu_vals[1] = pu_vals[0]
            pu_vals[0] = None
        elif bus == '646':
            pu_vals[1] = pu_vals[0]
            pu_vals[0] = None
        elif bus == '684':
            pu_vals[2] = pu_vals[1]
            pu_vals[1] = None
        print(f"{bus}: Phase A={pu_vals[0]}, Phase B={pu_vals[1]}, Phase C={pu_vals[2]}")

    # Define HTML tags for colors
    GREEN = "<span style='color:green;'>"
    RED = "<span style='color:red;'>"
    RESET = "</span>"

    # Define the filename based on the number of chargers added
    output_file = f"C:\\Users\\jilli\\OneDrive - University of Pittsburgh\\Desktop\\ECE1893\\EV_Chargers_{num_ev_stations}_added.html"
    over_voltage = 0
    under_voltage = 0

    # Open the file for writing as HTML
    with open(output_file, "w", encoding="utf-8") as file:
        # Write HTML header and table structure with the number of chargers in the title
        file.write(
            f"<html><head><title>EV Charger Voltage Results - Chargers Added: {num_ev_stations}</title></head><body>")

        # Write the header with the number of chargers added
        file.write(f"<h1>EV Charger Voltage Results - Chargers Added: {num_ev_stations}</h1>")

        file.write("<table border='1'><tr><th>Bus</th><th>Phase A</th><th>Phase B</th><th>Phase C</th></tr>")

        # Write each bus with flagging logic
        for bus, pu_vals in bus_data.items():
            a_val = pu_vals[0]
            b_val = pu_vals[1]
            c_val = pu_vals[2]

            # Format Phase A
            if a_val is None:
                a_file_str = "   ---   "
            elif a_val > 1.05:
                a_file_str = f"{RED}{a_val:.5f} ⚠️ OVER{RESET}"
                over_voltage += 1
            elif a_val < 0.95:
                a_file_str = f"{RED}{a_val:.5f} ⚠️ UNDER{RESET}"
                under_voltage += 1
            else:
                a_file_str = f"{GREEN}{a_val:.5f}{RESET}"

            # Format Phase B
            if b_val is None:
                b_file_str = "   ---   "
            elif b_val > 1.05:
                b_file_str = f"{RED}{b_val:.5f} ⚠️ OVER{RESET}"
                over_voltage += 1
            elif b_val < 0.95:
                b_file_str = f"{RED}{b_val:.5f} ⚠️ UNDER{RESET}"
                under_voltage += 1
            else:
                b_file_str = f"{GREEN}{b_val:.5f}{RESET}"

            # Format Phase C
            if c_val is None:
                c_file_str = "   ---   "
            elif c_val > 1.05:
                c_file_str = f"{RED}{c_val:.5f} ⚠️ OVER{RESET}"
                over_voltage += 1
            elif c_val < 0.95:
                c_file_str = f"{RED}{c_val:.5f} ⚠️ UNDER{RESET}"
                under_voltage += 1
            else:
                c_file_str = f"{GREEN}{c_val:.5f}{RESET}"

            # Write the formatted line to the HTML file
            file.write(f"<tr><td>{bus}</td><td>{a_file_str}</td><td>{b_file_str}</td><td>{c_file_str}</td></tr>")

        # End HTML table and body
        file.write("</table></body></html>")

    # Print file output message
    print(f"Results have been written to {output_file}")
    return over_voltage, under_voltage


under_voltage:np.array = np.zeros(320)
over_voltage:np.array = np.zeros(320)

chargers_added = []
# Example call to the function
for i in range(0, 320, 1):
    over_v,under_v = add_ev_chargers(i)
    over_voltage[i] = over_v
    under_voltage[i] = under_v

    chargers_added.append(i)
    print(f"Over-voltage count for {i} chargers: {over_v}, Under-voltage count: {under_v}")


# Plot the over-voltage and under-voltage counts versus the number of chargers added
plt.figure(figsize=(10, 6))
plt.plot(chargers_added, over_voltage[:len(chargers_added)], label="Over-Voltage", marker='o', color='red')
plt.plot(chargers_added, under_voltage[:len(chargers_added)], label="Under-Voltage", marker='o', color='blue')

# Add labels and title
plt.xlabel("Number of Chargers Added")
plt.ylabel("Voltage Flag Count")
plt.title("Over and Under Voltage Counts vs. Number of Chargers Added")
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
# Wait for 30 seconds between runs
