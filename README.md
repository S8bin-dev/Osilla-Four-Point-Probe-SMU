# Ossila SMU Python Control

This project sets up a Python environment to control the Ossila Source Measure Unit (SMU) using the `xtralien` library.

## Setup

1. **Install Dependencies**
   
   Ensure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect the Device**
   - Connect the SMU via USB.
   - If using Linux, it will likely be at `/dev/ttyUSB0` or `/dev/ttyACM0`.
   - If using Windows, check Device Manager for the COM port (e.g., `COM3`).

## Usage

### 1. Verify Connection

Run the verification script to confirm the device is recognized and communicating:

```bash
python verify_connection.py <PORT> <CONNECTION_TYPE>
```

Example (USB):
```bash
python verify_connection.py /dev/ttyUSB0 usb
```

Example (Ethernet):
```bash
python verify_connection.py 192.168.0.200 ethernet
```

### 2. Basic Measurement

The `basic_measurement.py` script demonstrates how to:
- Connect to the SMU.
- Enable the output.
- Set voltage/current limits.
- Perform a voltage sweep (IV Curve).
- Save the data to `measurement_results.csv`.
- Plot the results (saved as `iv_curve.png`).

**Note:** Open `basic_measurement.py` and update the `PORT` variable before running:

```python
PORT = "/dev/ttyUSB0"  # Update this to your port!
```

Then run:
```bash
python basic_measurement.py
```

## Files

- `smu_utils.py`: Helper functions for connection and basic control.
- `verify_connection.py`: Checks device info (Version, Serial).
- `basic_measurement.py`: Example IV sweep implementation.
- `test_mock_device.py`: Tests the logic without physical hardware.
