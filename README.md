# 🧪 Ossila SMU Sheet Resistance Measurement System

<p align="center">
  <b>A comprehensive Python-based solution for four-point probe sheet resistance measurements using the Ossila Source Measure Unit (SMU)</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/PyQt6-GUI-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/Streamlit-Web-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 📖 Overview

This project provides a complete measurement solution for thin film characterization using the Ossila SMU with a four-point probe. It includes:

- **Desktop GUI Application** (PyQt6) — Professional-grade interface with real-time measurements
- **Web Interface** (Streamlit) — Browser-based control for remote or lightweight usage
- **Command-line Scripts** — For quick measurements and automation

### Key Features

- ⚡ **Real-time Sheet Resistance Measurement** — Live display of Ω/square values
- 📊 **Automatic Calculations** — Sheet resistance, resistivity, and conductivity
- 📐 **Geometric Correction Factors** — Support for rectangular and circular samples
- 💾 **Data Export** — Save measurements to CSV files
- 🔧 **Advanced Configuration** — Probe spacing, sample filtering, polarity, and limits
- 🖥️ **Dual Interface** — Desktop GUI or web browser

---

## 🛠️ Hardware Requirements

| Component | Description |
|-----------|-------------|
| **Ossila SMU** | Source Measure Unit with four-point probe capability |
| **Four-Point Probe** | Ossila or compatible collinear probe (1.27mm default spacing) |
| **USB Cable** | For connection to computer |
| **Sample** | Thin film on substrate (e.g., conductive polymer, FTO, ITO) |

---

## 💻 Software Requirements

- **Python 3.8+**
- **Operating System**: Linux (tested) or Windows

### Dependencies

```
xtralien        # Ossila hardware communication
pyserial        # Serial port handling
numpy           # Numerical computations
pandas          # Data handling & export
matplotlib      # Plotting (basic scripts)
PyQt6           # Desktop GUI
pyqtgraph       # Real-time plotting
streamlit       # Web interface
plotly          # Interactive charts (web)
```

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/S8bin-dev/Osilla-Slu.git
cd Osilla-Slu
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Connect Hardware

- Connect the Ossila SMU via USB
- **Linux**: Device typically appears at `/dev/ttyUSB0` or `/dev/ttyACM0`
- **Windows**: Check Device Manager for COM port (e.g., `COM3`)

> ⚠️ **Linux Users**: If you get a permission error, run:  
> `sudo chmod 666 /dev/ttyUSB0` or add your user to the `dialout` group.

---

## 🚀 Quick Start

### Verify Connection

First, confirm the SMU is communicating:

```bash
# USB Connection
python verify_connection.py /dev/ttyACM0 usb

# Ethernet Connection (if applicable)
python verify_connection.py 192.168.0.200 ethernet
```

### Run Desktop GUI

```bash
python gui_main.py
```

### Run Web Interface

```bash
streamlit run web_main.py
# or use the provided script:
./run_web.sh
```

Open your browser to `http://localhost:8501`

### Basic IV Sweep (Command Line)

Edit the port in `basic_measurement.py`, then:

```bash
python basic_measurement.py
```

Results saved to `measurement_results.csv` and `iv_curve.png`

---

## 📂 Project Structure

```
Osilla-SLU/
├── gui_main.py            # PyQt6 desktop GUI application
├── web_main.py            # Streamlit web interface
├── gui_logic.py           # Core measurement calculations
├── smu_utils.py           # SMU connection & helper functions
├── verify_connection.py   # Connection verification script
├── basic_measurement.py   # Simple IV sweep example
├── diagnostic_smu.py      # Hardware diagnostics tool
├── style.qss              # GUI stylesheet (Qt)
├── requirements.txt       # Python dependencies
├── QUICKSTART.md          # Day 1 operations guide
├── README.md              # This file
├── results/               # Saved measurement data (CSV)
└── sludocumentation.pdf   # Ossila SMU documentation
```

---

## 📋 Usage Guide

### Desktop GUI (gui_main.py)

1. **Select Port** — Choose your SMU's serial port from the dropdown
2. **Configure Geometry** — Select Rectangular or Circular, enter dimensions
3. **Set Thickness** — Enter film thickness in micrometers (μm)
4. **Start Measurement** — Click the power button (⏻)
5. **View Results** — Real-time display of sheet resistance, resistivity, conductivity
6. **Record Data** — Set number of readings, click save (💾)

### Advanced Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Probe Spacing | Distance between probe tips (mm) | 1.270 |
| Samples per Point | Averaging filter for noise reduction | 8192 |
| Current Range | Measurement range (Autorange recommended) | Auto |
| Polarity | Current direction | Positive |
| Voltage Limit | Compliance voltage (V) | 10.5 |
| Current Limit | Compliance current (mA) | 220 |

### Web Interface (web_main.py)

The web interface mirrors the desktop GUI with a browser-based experience. Ideal for:
- Remote measurements
- Lab computers without GUI support
- Quick demonstrations

---

## 📐 Measurement Theory

This system implements the standard four-point probe method for sheet resistance measurement:

### Basic Formula

$$R_s = \frac{\pi}{\ln(2)} \cdot \frac{V}{I} \cdot C$$

Where:
- **R_s** = Sheet resistance (Ω/square)
- **V** = Voltage between inner probes
- **I** = Current through outer probes
- **C** = Geometric correction factor

### Calculated Properties

| Property | Formula | Unit |
|----------|---------|------|
| Sheet Resistance | R_s = 4.532 × (V/I) × C | Ω/square |
| Resistivity | ρ = R_s × t | Ω·m |
| Conductivity | σ = 1/ρ | S/m |

### Geometric Corrections

The system automatically applies correction factors based on:
- **Rectangular samples**: Width/spacing ratio (Smits 1958)
- **Circular samples**: Diameter/spacing ratio

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission Denied" on Linux | `sudo chmod 666 /dev/ttyUSB0` or add to `dialout` group |
| Device not found | Check USB connection, try different port in dropdown |
| Current reads zero | Verify probe contact, check sample conductivity |
| Compliance limit reached | Increase voltage/current limits, check for shorts |
| No serial in list | Click "Refresh" (R) button to rescan ports |

### Run Diagnostics

For detailed hardware testing:

```bash
python diagnostic_smu.py
```

---

## 📄 Data Output

Measurements are saved to the `results/` directory as CSV files:

```csv
Current (A),Voltage (V),Sheet Resistance (Ohm/square)
7.5e-05,0.0012,72.456
7.5e-05,0.0013,78.234
...
```

---

## 📚 References

- [Ossila SMU Documentation](https://www.ossila.com/pages/source-measure-unit)
- [Four-Point Probe Method (Wikipedia)](https://en.wikipedia.org/wiki/Four-terminal_sensing)
- Smits, F.M. (1958). "Measurement of Sheet Resistivities with the Four-Point Probe"

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sabin Baral**

- GitHub: [@S8bin-dev](https://github.com/S8bin-dev)

---

<p align="center">
  Made with ⚡ for thin film characterization
</p>
