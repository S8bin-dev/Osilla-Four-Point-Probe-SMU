import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QLineEdit, QComboBox, QSpinBox, 
                             QDoubleSpinBox, QPushButton, QGroupBox, QCheckBox, QTextEdit,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon

import smu_utils
from gui_logic import MeasurementLogic

class OssilaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GU Lab Sheet Resistance Lite v1.0.3 (Restored)")
        self.setGeometry(100, 100, 1060, 680)
        
        # Load Stylesheet
        try:
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("style.qss not found. Using default style.")

        # Logic & Device
        self.logic = MeasurementLogic()
        self.device = None
        self.is_measuring = False
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- LEFT SIDEBAR (Controls) ---
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280) 
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        
        # 1. System Address
        addr_row = QHBoxLayout()
        addr_row.addWidget(QLabel("System Address"))
        self.refresh_btn = QPushButton("R") 
        self.refresh_btn.setFixedSize(25, 25)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.port_combo = QComboBox()
        self.refresh_ports()
        addr_row.addWidget(self.refresh_btn)
        addr_row.addWidget(self.port_combo)
        sidebar_layout.addLayout(addr_row)
        
        # 2. Geometry
        sidebar_layout.addWidget(QLabel("Sample Geometry"))
        self.geom_combo = QComboBox()
        self.geom_combo.addItems(["Rectangular", "Circular"])
        self.geom_combo.currentIndexChanged.connect(self.update_geometry_fields)
        sidebar_layout.addWidget(self.geom_combo)
        
        # Geometry Fields
        self.geom_fields_layout = QGridLayout()
        
        self.long_spin = self.create_spinbox(60.00, "Long Side (mm)")
        self.lbl_long = QLabel("Long Side (mm)")
        self.geom_fields_layout.addWidget(self.lbl_long, 0, 0)
        self.geom_fields_layout.addWidget(self.long_spin, 0, 1)
        
        self.short_spin = self.create_spinbox(60.00, "Short Side (mm)")
        self.lbl_short = QLabel("Short Side (mm)")
        self.geom_fields_layout.addWidget(self.lbl_short, 1, 0)
        self.geom_fields_layout.addWidget(self.short_spin, 1, 1)
        
        self.diam_spin = self.create_spinbox(14.00, "Diameter (mm)")
        self.lbl_diam = QLabel("Diameter (mm)")
        self.geom_fields_layout.addWidget(self.lbl_diam, 2, 0)
        self.geom_fields_layout.addWidget(self.diam_spin, 2, 1)
        
        self.thick_spin = self.create_spinbox(0.000, "Thickness (μm)", decimals=3, max_val=10000.0)
        self.geom_fields_layout.addWidget(QLabel("Thickness (μm)"), 3, 0)
        self.geom_fields_layout.addWidget(self.thick_spin, 3, 1)
        
        sidebar_layout.addLayout(self.geom_fields_layout)
        self.update_geometry_fields() 
        
        sidebar_layout.addSpacing(10)
        
        # 3. Advanced Settings Toggle
        self.adv_chk = QCheckBox("Use Advanced Settings")
        self.adv_chk.toggled.connect(self.toggle_advanced)
        sidebar_layout.addWidget(self.adv_chk)
        
        # 4. Advanced Group
        self.adv_widget = QWidget()
        adv_layout = QGridLayout(self.adv_widget)
        adv_layout.setContentsMargins(0, 0, 0, 0)
        
        # Probe Spacing
        adv_layout.addWidget(QLabel("Probe Spacing (mm)"), 0, 0)
        self.spacing_spin = self.create_spinbox(1.270, "Spacing", decimals=3)
        adv_layout.addWidget(self.spacing_spin, 0, 1)
        
        # Samples per point
        adv_layout.addWidget(QLabel("Samples per Point"), 1, 0)
        self.samples_combo = QComboBox()
        self.samples_combo.addItems(["64", "256", "1024", "4096", "8192"])
        self.samples_combo.setCurrentText("8192")
        adv_layout.addWidget(self.samples_combo, 1, 1)
        
        # Current Range
        adv_layout.addWidget(QLabel("Current Range"), 2, 0)
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Autorange", "200 mA", "20 mA", "200 uA"])
        adv_layout.addWidget(self.range_combo, 2, 1)
        
        # Polarity
        adv_layout.addWidget(QLabel("Polarity"), 3, 0)
        self.polar_combo = QComboBox()
        self.polar_combo.addItems(["Positive", "Negative"])
        adv_layout.addWidget(self.polar_combo, 3, 1)
        
        # Limits
        adv_layout.addWidget(QLabel("Voltage Limit (V)"), 4, 0)
        self.vlim_spin = self.create_spinbox(10.50, "Voltage Limit", 20.0)
        adv_layout.addWidget(self.vlim_spin, 4, 1)
        
        adv_layout.addWidget(QLabel("Current Limit (mA)"), 5, 0)
        self.ilim_spin = self.create_spinbox(220.00, "Current Limit", 500.0)
        adv_layout.addWidget(self.ilim_spin, 5, 1)

        sidebar_layout.addWidget(self.adv_widget)
        self.toggle_advanced(False) 
        
        sidebar_layout.addStretch()
        
        # Reset Button (Keeping this as it's useful and harmless)
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setStyleSheet("background-color: #4a148c; color: white; padding: 8px; font-weight: bold;")
        reset_btn.clicked.connect(self.reset_defaults)
        sidebar_layout.addWidget(reset_btn)

        main_layout.addWidget(sidebar)
        
        # --- CENTER AREA (Display) ---
        center_widget = QWidget()
        center_widget.setObjectName("DisplayArea")
        center_layout = QVBoxLayout(center_widget)
        
        # Top Panel
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        
        self.power_btn = QPushButton("⏻")
        self.power_btn.setObjectName("PowerButton")
        self.power_btn.setFixedSize(90, 90)
        self.power_btn.setCheckable(True)
        self.power_btn.clicked.connect(self.toggle_power)
        top_layout.addWidget(self.power_btn, 0)
        
        self.sr_container = self.create_digital_display("Sheet Resistance", "00.000", "Ω/square", large=True)
        self.lbl_sheet_res = self.sr_container.val_label
        top_layout.addWidget(self.sr_container, 2)
        
        right_metrics = QVBoxLayout()
        self.res_widget = self.create_digital_display("Resistivity", "--.---", "Ω.m")
        self.lbl_resistivity = self.res_widget.val_label
        right_metrics.addWidget(self.res_widget)
        
        self.cond_widget = self.create_digital_display("Conductivity", "--.---", "S/m")
        self.lbl_conductivity = self.cond_widget.val_label
        right_metrics.addWidget(self.cond_widget)
        top_layout.addLayout(right_metrics, 1)
        
        center_layout.addWidget(top_panel, stretch=3)
        
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #333;")
        center_layout.addWidget(line)
        
        # Bottom Panel
        bot_panel = QWidget()
        bot_layout = QHBoxLayout(bot_panel)
        
        self.lbl_volt_out_widget = self.create_digital_display("Outer Probe Voltage", "000.00", "mV", large=True)
        self.lbl_volt_out = self.lbl_volt_out_widget.val_label
        
        self.lbl_curr_out_widget = self.create_digital_display("Outer Probe Current", "00.000", "mA", large=True)
        self.lbl_curr_out = self.lbl_curr_out_widget.val_label

        self.lbl_volt_in_widget = self.create_digital_display("Inner Probe Voltage", "00.000", "mV", large=True)
        self.lbl_volt_in = self.lbl_volt_in_widget.val_label
        
        bot_layout.addWidget(self.lbl_volt_out_widget)
        bot_layout.addWidget(self.lbl_curr_out_widget)
        bot_layout.addWidget(self.lbl_volt_in_widget)
        
        center_layout.addWidget(bot_panel, stretch=2)
        main_layout.addWidget(center_widget)
        
        # --- RIGHT SIDEBAR (Log) ---
        right_sidebar = QWidget()
        right_sidebar.setFixedWidth(250)
        right_layout = QVBoxLayout(right_sidebar)
        
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("Readings to Save"))
        self.save_spin = QSpinBox()
        self.save_spin.setValue(50)
        save_layout.addWidget(self.save_spin)
        save_btn = QPushButton("💾")
        save_btn.setFixedWidth(30)
        save_btn.clicked.connect(self.start_recording)
        save_layout.addWidget(save_btn)
        right_layout.addLayout(save_layout)
        
        self.log_area = QTextEdit()
        self.log_area.setObjectName("Log") 
        self.log_area.setReadOnly(True)
        self.log("System initialized.")
        right_layout.addWidget(self.log_area)
        
        # Branding
        logo_lbl = QLabel("GU Lab")
        logo_lbl.setObjectName("Logo")
        logo_lbl.setStyleSheet("color: #4a148c; font-size: 28px; font-weight: bold;")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(logo_lbl)
        
        main_layout.addWidget(right_sidebar)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.measurement_loop)
    
    # ... helpers ...
    def update_geometry_fields(self):
        geom = self.geom_combo.currentText()
        if geom == "Rectangular":
            self.long_spin.setVisible(True)
            self.lbl_long.setVisible(True)
            self.short_spin.setVisible(True)
            self.lbl_short.setVisible(True)
            self.diam_spin.setVisible(False)
            self.lbl_diam.setVisible(False)
        else:
            self.long_spin.setVisible(False)
            self.lbl_long.setVisible(False)
            self.short_spin.setVisible(False)
            self.lbl_short.setVisible(False)
            self.diam_spin.setVisible(True)
            self.lbl_diam.setVisible(True)
            
    def toggle_advanced(self, checked):
        self.adv_widget.setVisible(checked)
        
    def reset_defaults(self):
        self.log("Resetting to defaults...")
        self.geom_combo.setCurrentText("Rectangular")
        self.long_spin.setValue(60.00)
        self.short_spin.setValue(60.00)
        self.diam_spin.setValue(14.00)
        self.thick_spin.setValue(0.000)
        self.spacing_spin.setValue(1.270)
        self.samples_combo.setCurrentText("8192")
        self.range_combo.setCurrentText("Autorange")
        self.polar_combo.setCurrentText("Positive")
        self.vlim_spin.setValue(10.50)
        self.ilim_spin.setValue(220.00)
        self.save_spin.setValue(50)

    def create_spinbox(self, value, name, max_val=1000.0, decimals=2):
        sb = QDoubleSpinBox()
        sb.setRange(0.0, max_val)
        sb.setValue(value)
        sb.setDecimals(decimals)
        sb.setStyleSheet("background-color: white; color: black;")
        return sb
        
    def create_digital_display(self, title, placeholder, unit, large=False):
        container = QWidget()
        layout = QVBoxLayout(container)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("DigitalLabel")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_val = QLabel(placeholder)
        lbl_val.setObjectName("DigitalReadout")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not large:
             font = lbl_val.font()
             font.setPointSize(24)
             lbl_val.setFont(font)
        lbl_unit = QLabel(unit)
        lbl_unit.setObjectName("DigitalUnit")
        lbl_unit.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        layout.addWidget(lbl_unit)
        container.val_label = lbl_val
        return container

    def log(self, message):
        timestamp = time.strftime("%H:%M")
        self.log_area.append(f"{timestamp}: {message}")
        
    def refresh_ports(self):
        self.port_combo.clear()
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        port_list = [p.device for p in ports]
        if "/dev/ttyACM0" not in port_list: port_list.append("/dev/ttyACM0")
        if "/dev/ttyUSB0" not in port_list: port_list.append("/dev/ttyUSB0")
        self.port_combo.addItems(port_list)
        
    def toggle_power(self, checked):
        if checked:
            self.start_measurement()
        else:
            self.stop_measurement()
            
    def start_measurement(self):
        port = self.port_combo.currentText()
        user_v_limit = self.vlim_spin.value()
        user_i_limit = self.ilim_spin.value() * 1e-3
        
        self.log(f"Initialising device on {port}...")
        
        try:
             if self.device:
                 try: self.device.close()
                 except: pass
                 
             self.device = smu_utils.get_session(port, 'usb')
             if not self.device:
                 raise Exception("Connection failed")
             
             # Setup SMU
             self.device.smu1.set.enabled(True, response=0)
             self.device.smu1.set.limitv(user_v_limit, response=0)
             self.device.smu1.set.limiti(user_i_limit, response=0)
             
             # Advanced: Samples
             try:
                 samples = int(self.samples_combo.currentText())
                 self.device.smu1.set.filter(samples, response=0)
                 self.device.vsense1.set.filter(samples, response=0)
             except: pass
             
             # Polarity
             polarity_mult = 1.0
             if self.polar_combo.currentText() == "Negative":
                 polarity_mult = -1.0
             
             # Setup Vsense
             self.device.vsense1.set.enabled(True, response=0)
             
             # Source Voltage for Measurement
             # In the stable version, we sourced a standard measurement voltage like 0.5V
             # Or we relied on the system default. 
             # To match "Data Collected" which had 75uA, we likely had some voltage.
             # Setting 0.5V (Standard) here to ensure function.
             drive_v = 0.5 * polarity_mult
             self.device.smu1.set.voltage(drive_v, response=0)
             
             self.log(f"Measurement started (Source: {drive_v}V).")
             self.is_measuring = True
             self.timer.start(500) 
             
        except Exception as e:
            self.log(f"Error: {e}")
            self.power_btn.setChecked(False)
            
    def stop_measurement(self):
        if self.device:
            self.log("Stopping measurement...")
            try:
                self.device.smu1.set.voltage(0, response=0)
                self.device.smu1.set.enabled(False, response=0)
                self.device.vsense1.set.enabled(False, response=0)
                self.device.close()
            except: pass
            self.device = None
        self.is_measuring = False
        self.timer.stop()
        self.log("Measurement finished.")
        
    def measurement_loop(self):
        if not self.device or not self.is_measuring: return
        try:
            v_data = self.device.vsense1.measure()
            smu_data = self.device.smu1.measure()
            
            v_inner = 0.0
            i_outer = 0.0
            v_outer = 0.0
            import numpy as np
            
            if v_data is not None:
                v_arr = np.array(v_data).flatten()
                if len(v_arr) > 0:
                     try:
                         val = str(v_arr[0]).strip()
                         if val: v_inner = float(val)
                     except: pass
            
            if smu_data is not None:
                smu_arr = np.array(smu_data).flatten()
                if len(smu_arr) >= 2:
                    try:
                        val_v = str(smu_arr[0]).strip()
                        val_i = str(smu_arr[1]).strip()
                        if val_v: v_outer = float(val_v)
                        if val_i: i_outer = float(val_i)
                    except: pass
            
            thick_um = self.thick_spin.value()
            geom = self.geom_combo.currentText()
            metrics = self.logic.calculate_metrics(
                v_inner, i_outer, geom, thick_um, 
                length=self.long_spin.value(), width=self.short_spin.value(), 
                diameter=self.diam_spin.value(), spacing=self.spacing_spin.value()
            )
            
            # Recording
            if hasattr(self, 'is_recording') and self.is_recording:
                 self.data_buffer.append({
                     "Current (A)": i_outer,
                     "Voltage (V)": v_inner, # Matches old legacy format named "Voltage (V)"
                     "Sheet Resistance (Ohm/square)": metrics['sheet_resistance']
                 })
                 remaining = self.points_to_save - len(self.data_buffer)
                 if remaining <= 0:
                     self.save_buffer_to_file()
                 else:
                     self.log(f"Recording... {len(self.data_buffer)}")
                     
            self.lbl_sheet_res.setText(f"{metrics['sheet_resistance']:.3f}")
            self.lbl_resistivity.setText(f"{metrics['resistivity']*1e6:.2f}") 
            self.lbl_conductivity.setText(f"{metrics['conductivity']*1e-3:.4f}") 
            self.lbl_volt_out.setText(f"{v_outer*1000:.2f}") 
            self.lbl_curr_out.setText(f"{i_outer*1000:.4f}") 
            self.lbl_volt_in.setText(f"{v_inner*1000:.2f}") 
                
        except Exception as e:
            self.log(f"Read error: {e}")

    def start_recording(self):
        if not self.is_measuring:
            self.log("Error: Start measurement first.")
            return
        self.points_to_save = self.save_spin.value()
        self.data_buffer = []
        self.is_recording = True
        self.log(f"Started recording {self.points_to_save} points...")
        
    def save_buffer_to_file(self):
        self.is_recording = False
        self.log("Recording complete. Saving...")
        try:
            import pandas as pd
            if not os.path.exists("results"): os.makedirs("results")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"results/measurement_{timestamp}.csv"
            df = pd.DataFrame(self.data_buffer)
            # Ensure column order matches user's legacy file
            df = df[["Current (A)", "Voltage (V)", "Sheet Resistance (Ohm/square)"]]
            df.to_csv(filename, index=False)
            self.log(f"Saved: {filename}")
        except Exception as e:
            self.log(f"Save error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OssilaGUI()
    window.show()
    sys.exit(app.exec())
