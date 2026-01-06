import smu_utils
import time
import pandas as pd
import matplotlib.pyplot as plt

def main():
    """
    Performs a basic IV sweep measurement using the Ossila SMU.
    """
    # Configuration
    # You might want to change this to your specific port
    PORT = "/dev/ttyACM0"  # Update this!
    
    # Sweep Parameters
    V_START = 0.0
    V_END = 5.0
    V_STEP = 0.5
    DELAY_US = 1000  # Default 1000us
    
    # 1. Connect
    device = smu_utils.get_session(PORT, 'usb')
    if not device:
        print("Exiting...")
        return

    try:
        # 2. Setup SMU1
        print("Setting up SMU1...")
        # Enable SMU
        # Docs: `device.smu1.set.enabled(True, response=0)`
        device.smu1.set.enabled(True, response=0)
        
        # Set Voltage Limit (Compliance)
        # Default is 10 V, let's set it explicitly just in case
        device.smu1.set.limitv(10.0, response=0)
        
        # Set Current Limit
        # Default is 0.225 A usually
        device.smu1.set.limiti(0.1, response=0) # 100mA limit
        
        # 3. Perform Sweep
        # Command: `smu1 sweep float(start) float(inc) float(end) integer(delay)`
        # Returns [voltage, current] matrix
        
        print(f"Starting sweep from {V_START}V to {V_END}V...")
        
        # Calculation of expected points for info
        # The library likely returns a list of lists or similar structure
        data_matrix = device.smu1.sweep(V_START, V_STEP, V_END, DELAY_US)
        
        print("Sweep complete. Processing data...")
        
        # Data is likely [[v1, i1], [v2, i2], ...]
        # We can convert to DataFrame
        # Check if data_matrix is empty or valid
        if not data_matrix:
            print("No data returned. Compliance limit might have been hit instantly or error occurred.")
        else:
            # Depending on how the library parses "Array" or "Matrix" [cite: 41, 48]
            # It might be a list of strings or a numpy array if they used numpy internally.
            # We assume it's a list/iterable of rows.
            
            # Create DataFrame
            df = pd.DataFrame(data_matrix, columns=['Voltage (V)', 'Current (A)'])
            print(df)
            
            # Save to CSV
            csv_name = "measurement_results.csv"
            df.to_csv(csv_name, index=False)
            print(f"Data saved to {csv_name}")
            
            # Plot
            # (Optional: Requires matplotlib)
            try:
                plt.figure()
                plt.plot(df['Voltage (V)'], df['Current (A)'], 'o-')
                plt.title("IV Curve")
                plt.xlabel("Voltage (V)")
                plt.ylabel("Current (A)")
                plt.grid(True)
                plt.savefig("iv_curve.png")
                print("Plot saved to iv_curve.png")
            except Exception as e:
                print(f"Could not plot: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # 4. Clean up
        # Turn off SMU output for safety
        if device:
            try:
                device.smu1.set.enabled(False, response=0)
                pass
            except:
                pass
            smu_utils.close_session(device)

if __name__ == "__main__":
    main()
