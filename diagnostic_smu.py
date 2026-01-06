import xtralien
import time
import sys
import numpy as np

def run_diagnostics():
    print("=== SMU DIAGNOSTICS ===")
    port = "/dev/ttyACM0"
    
    print(f"1. Connecting to {port}...")
    try:
        device = xtralien.Device(port)
        print("   Connected.")
        print(f"   Hello Check: {device.cloi.hello().strip()}")
    except Exception as e:
        print(f"   FATAL: Could not connect ({e})")
        return

    print("\n2. Resetting Device...")
    try:
        device.smu1.set.enabled(False, response=0)
        device.vsense1.set.enabled(False, response=0)
        device.smu1.set.voltage(0, response=0)
        time.sleep(1)
        print("   Reset complete.")
    except Exception as e:
        print(f"   Reset failed ({e})")

    print("\n3. Testing SMU1 (Outer Probes) Source/Measure...")
    try:
        print("   Enabling SMU1...")
        device.smu1.set.enabled(True, response=0)
        
        target_v = 0.5
        print(f"   Setting Source Voltage to {target_v} V...")
        device.smu1.set.voltage(target_v, response=0)
        time.sleep(0.5)
        
        print("   Measuring SMU1...")
        data = device.smu1.measure()
        print(f"   Raw Data: {data}")
        
        v_out, i_out = 0.0, 0.0
        if data is not None:
             arr = np.array(data).flatten()
             if len(arr) >= 2:
                 v_out, i_out = float(arr[0]), float(arr[1])
        
        print(f"   Measured: V={v_out:.4f} V, I={i_out*1000:.4f} mA")
        
        if abs(i_out) < 1e-6:
             print("   WARNING: Current is near zero. Open Circuit/Probe Issue.")
        else:
             print("   SUCCESS: Current flowing.")

    except Exception as e:
        print(f"   SMU1 Test Failed ({e})")

    print("\n4. Testing Vsense1 (Inner Probes) Measure...")
    try:
        print("   Enabling Vsense1...")
        device.vsense1.set.enabled(True, response=0)
        time.sleep(0.5)
        
        print("   Measuring Vsense1...")
        v_data = device.vsense1.measure()
        print(f"   Raw Data: {v_data}")
        
        v_in = 0.0
        if v_data is not None:
             arr = np.array(v_data).flatten()
             if len(arr) > 0:
                 v_in = float(arr[0])
                 
        print(f"   Measured Inner V={v_in:.4f} V")
        print("   Vsense Test Complete.")
        
    except Exception as e:
        print(f"   Vsense1 Test Failed ({e})")

    print("\n5. Cleanup...")
    try:
        device.smu1.set.voltage(0, response=0)
        device.smu1.set.enabled(False, response=0)
        device.vsense1.set.enabled(False, response=0)
        device.close()
        print("   Device closed.")
    except:
        pass
        
    print("\n=== DIAGNOSTICS COMPLETE ===")

if __name__ == "__main__":
    run_diagnostics()
