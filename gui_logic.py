import numpy as np

class MeasurementLogic:
    """
    Handles calculations for Sheet Resistance, Resistivity, and Conductivity.
    Implements geometric correction factors for finite sample sizes.
    """
    
    def __init__(self):
        pass
        
    def calculate_metrics(self, voltage, current, geometry, thickness_microns, 
                          length=0, width=0, diameter=0, spacing=1.27):
        """
        Calculates sheet resistance (R_sheet), Resistivity (rho), and Conductivity (sigma).
        
        Args:
            voltage (float): Measured voltage in Volts.
            current (float): Measured current in Amps.
            geometry (str): 'Rectangular' or 'Circular'.
            thickness_microns (float): Sample thickness in microns.
            length (float): Length in mm.
            width (float): Width in mm.
            diameter (float): Diameter in mm.
            spacing (float): Probe spacing in mm (default 1.27mm for standard Ossila/4-point).
            
        Returns:
            dict: {
                "sheet_resistance": float,
                "resistivity": float,
                "conductivity": float,
                "resistance": float,
                "correction_factor": float
            }
        """
        if current == 0:
            return {
                "sheet_resistance": 0.0,
                "resistivity": 0.0,
                "conductivity": 0.0,
                "resistance": 0.0,
                "correction_factor": 1.0
            }
            
        resistance = voltage / current
        
        # Calculate Correction Factor (C)
        # Standard 4-point probe formula: Rs = (pi / ln(2)) * (V/I) * C
        # Infinite sheet: C = 1.0
        # Basic multiplier K = pi / ln(2) ~= 4.5324
        
        K = np.pi / np.log(2) # 4.53236
        
        # Geometric Correction
        # Based on "A Survey of Four-Point Probe Sheet Resistance Measurements" or generic textbooks.
        # We will implement a simplified correction based on L/s or D/s ratios.
        
        C = 1.0
        s = spacing
        
        try:
            if geometry == "Rectangular":
                # Use the smaller dimension to determine "narrowness" correction
                # If sample is large (L, W >> s), C -> 1
                # If sample is narrow strip, C decreases.
                
                # Simplified Model for finite width d (Smits 1958)
                # d = min(length, width)
                # ratio = d / s
                
                d = min(length, width) if (length > 0 and width > 0) else 100.0
                ratio = d / s
                
                # Data table approximation for Rectangular correction (Finite Width)
                # d/s:  1.0     2.0     3.0     4.0     >= 5.0
                # C:    0.86    0.98    1.0     1.0     1.0
                # (Very rough approx for "Lite" replication)
                
                # A better formula for finite width w (where line of probes is parallel to length):
                # We'll use a widely used approximation for thin films:
                # If w/s > 4, correction is negligible (C~1).
                
                if ratio < 4.0:
                    # Generic decrease. 
                    # Let's use Ossila's style logic: infinite sheet assumption is surprisingly robust.
                    # But user wants "Calculations implemented".
                    # Let's use a standard lookup-interpolation or function.
                    # C(w/s) for infinite length:
                    # 2ln2 / (ln(sinh(t/s) ... ) complex stuff.
                    
                    # Implementation of Smits (1958) Table 1 for Recangular:
                    # w/s -> C
                    # 1.0 -> 0.865
                    # 2.0 -> 0.98
                    # 3.0 -> 0.997
                    # 4.0 -> 0.999
                    
                    # Let's do a simple interpolation for robustness
                    x = [1.0, 2.0, 3.0, 4.0, 5.0]
                    y = [0.865, 0.98, 0.997, 0.999, 1.0]
                    if ratio < 1.0: 
                         # Very narrow
                         C = 0.865 * ratio # Linear decay approximation
                    else:
                         C = np.interp(ratio, x, y)
                else:
                    C = 1.0
                
            elif geometry == "Circular":
                # Finite diameter D
                d = diameter if diameter > 0 else 100.0
                ratio = d / s
                
                # Smits 1958 Table 2 for Circular
                # d/s -> C
                # 3 -> 0.5
                # 4 -> 0.64
                # 10 -> 0.92
                # Infinite -> 1.0
                
                # Ideally:
                # C = 1 / (1 + (1 / (2*ln2)) * ln( ... ) )
                
                # Let's use interpolation again for stability
                x = [3.0, 4.0, 5.0, 10.0, 20.0, 100.0]
                y = [0.500, 0.646, 0.741, 0.926, 0.98, 1.0]
                
                if ratio < 3.0:
                    C = 0.5 * (ratio / 3.0) # Decay
                else:
                    C = np.interp(ratio, x, y)
                    
        except Exception:
            C = 1.0 # Fallback
            
        # Final Rs
        # Rs = K * R * C
        sheet_resistance = K * resistance * C
        
        # Resistivity (rho) = Rs * thickness (in meters)
        thickness_meters = thickness_microns * 1e-6
        resistivity = sheet_resistance * thickness_meters
        
        # Conductivity (sigma) = 1 / rho
        conductivity = 0.0
        if resistivity > 0:
            conductivity = 1.0 / resistivity
            
        return {
            "sheet_resistance": sheet_resistance,
            "resistivity": resistivity,
            "conductivity": conductivity,
            "resistance": resistance,
            "correction_factor": C
        }
