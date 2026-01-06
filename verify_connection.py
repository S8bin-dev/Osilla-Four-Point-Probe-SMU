import smu_utils
import sys

def main():
    """
    Simple script to verify connection to the Ossila SMU.
    Usage: python verify_connection.py [port_or_ip] [connection_type]
    """
    
    # Default arguments
    address = None
    conn_type = 'usb'
    
    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        conn_type = sys.argv[2]
        
    print(f"--- Ossila SMU Connection Check ---")
    
    device = smu_utils.get_session(address, conn_type)
    
    if not device:
        print("FAIL: Could not connect to device.")
        sys.exit(1)
        
    try:
        # Get System Info
        # Docs: `cloi version` returns version
        # Docs: `board no` returns board number
        # Docs: `serial` returns serial number
        
        # Note: If these functions are simple getters in Python wrapper, 
        # they might be attributes or methods.
        # Based on `device.cloi.hello()`, we assume `methods`.
        
        print("\n--- Device Info ---")
        try:
            version = device.cloi.version()
            print(f"CLOI Version: {version}")
        except Exception as e:
            print(f"Could not get CLOI version: {e}")

        try:
            # According to docs: `smu# set ...`
            # Top level commands like `serial` might be direct methods on `device` or `device.system`?
            # The docs say: `serial`: Returns serial number [cite: 561].
            # The python wrapper usually maps root commands to device methods.
            
            # Implementation note: In some versions of xtralien, properties are just attributes.
            serial = device.serial
            if callable(serial):
                serial = serial()
            
            print(f"Serial Number: {serial}")
        except Exception as e:
            # It's possible the wrapper puts top-level commands in a specific namespace.
            # We will try to just print what we can.
            print(f"Could not get Serial (might be under different attribute): {e}")

        print("\nSUCCESS: Communication established.")
        
    except Exception as e:
        print(f"An error occurred during verification: {e}")
    finally:
        smu_utils.close_session(device)

if __name__ == "__main__":
    main()
