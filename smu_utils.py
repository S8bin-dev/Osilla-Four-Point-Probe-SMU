import xtralien
import time
import sys

def get_session(address=None, connection_type='usb'):
    """
    Connects to the Ossila SMU.
    
    Args:
        address (str): Port (e.g., '/dev/ttyUSB0', 'COM3') or IP address.
                       If None, tries to auto-detect (implementation limited).
        connection_type (str): 'usb' or 'ethernet'.
        
    Returns:
        xtralien.Device: The connected device object.
    """
    print(f"Attempting to connect via {connection_type}...")
    
    try:
        if connection_type.lower() == 'ethernet':
            if not address:
                raise ValueError("IP address is required for Ethernet connection.")
            # Default port is 8888 as per docs
            device = xtralien.Device(address, port=8888)
        else:
            # USB Connection
            if address:
                device = xtralien.Device(address)
            else:
                # If no address provided, we might want to hint the user or just fail
                # For now, let's try a common default or raise error
                print("No port specified. Please provide a COM port (e.g. /dev/ttyUSB0 or COM3)")
                return None

        # Verify connection with a simple command
        # Docs say `cloi hello` returns "Hello World\n"
        # We assume the library returns the string directly.
        response = device.cloi.hello()
        print(f"Device responded: {response.strip()}")
        return device

    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def check_compliance_error(device, unit='smu1'):
    """
    Checks if the SMU unit has hit a compliance limit.
    """
    try:
        # Access the error property. It returns a boolean.
        # device.smu1.get.error() based on docs hierarchy
        # The python wrapper usually maps properties to attributes or get/set methods
        # Docs say: `device.smu1.oneshot(set_voltage)` works.
        # Docs say: `cloi get precision`.
        # Python: `device.smu1.get.error()` is likely the syntax if `xtralien` follows the CLOI structure strictly
        # or just `device.smu1.error` if it maps properties directly.
        # The docs Show `device.smu1.set.enabled(True, response=0)`.
        # So `device.smu1.get.error()` is a safe bet.
        
        # Let's assume the library exposes `get` as a property or sub-object
        is_error = getattr(device, unit).get.error()
        if is_error:
            print(f"WARNING: {unit} Compliance Limit Reached!")
            return True
        return False
    except Exception as e:
        print(f"Error checking compliance: {e}")
        return False

def close_session(device):
    if device:
        device.close()
        print("Connection closed.")
