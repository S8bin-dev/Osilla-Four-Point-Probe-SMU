# Ossila SMU: Day 1 Operations Guide

## 1. Hardware Setup
1. **Power On**: Plug in the power adapter to the Ossila SMU and switch it on.
2. **USB Connection**: Connect the USB cable from the SMU to your computer.
3. **test Circuit**:
   - Connect your **Device Under Test (DUT)** (e.g., LED, resistor, solar cell) to the SMU output headers.
   - For a standard IV sweep, connect **SMU1+** (Signal) to the Anode/Positive and **SMU1-** (Ground) to the Cathode/Negative.

## 2. Software Verification
1. **Open Terminal**: Navigate to this folder: `/home/sabin/Documents/GitHub/Osilla SLU`.
2. **Activate Environment**:
   You must use the virtual environment we created. Run:
   ```bash
   source venv/bin/activate
   ```
   (You will see `(venv)` appear in your terminal prompt).

3. **Check Connection**:
   Run the verification script to find the device and confirm it talks to Python.
   ```bash
   python verify_connection.py
   ```
   *Success?* You should see "Communication established" and the Serial Number.
   *Failure?* If it fails, you may need to specify the port (e.g., `python verify_connection.py /dev/ttyUSB0 usb`).

## 3. Running Your First Experiment
1. **Edit Settings**: Open `basic_measurement.py`.
   - Update `PORT` if it was different during verification.
   - Adjust `V_START` (0V) and `V_END` (5V) if your device needs different ranges.
   - **Caution**: Ensure `device.smu1.set.limiti(0.1)` (100mA) is safe for your device!
2. **Run Measurement**:
   ```bash
   python basic_measurement.py
   ```
3. **View Results**:
   - **Data**: Check `measurement_results.csv` for the raw numbers.
   - **Plot**: Open `iv_curve.png` to see the graph immediately.

## Troubleshooting
- **Permission Error**: If Linux says "Access Denied" to the USB port, run: `sudo chmod 666 /dev/ttyUSB0`.
- **Compliance Limit**: If the output is all zeros or cuts off, increase the Current Limit (`limiti`) in `basic_measurement.py`.
