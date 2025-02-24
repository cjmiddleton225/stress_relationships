import numpy as np
import pandas as pd
from datetime import datetime
from stress_tensor import StressTensor  

class TimeSeriesStressTensor:
    """
    A class to manage stress tensors over time.
    """
    def __init__(self):
        """Initialize empty time series."""
        self.data = pd.DataFrame(
            columns=['timestamp', 'xx', 'yy', 'zz', 'xy', 'yz', 'xz']
        )
        self.data.set_index('timestamp', inplace=True)

    def add_tensor(self, tensor: StressTensor, timestamp: datetime = None):
        """Add a stress tensor at a specific time."""
        if timestamp is None:
            timestamp = datetime.now()

        # Extract components and flatten to vector form
        comps = tensor.components
        vector = [
            comps[0,0], comps[1,1], comps[2,2],  # xx, yy, zz
            comps[0,1], comps[1,2], comps[0,2]   # xy, yz, xz
        ]
        
        self.data.loc[timestamp] = vector

    def get_tensor(self, timestamp: datetime) -> StressTensor:
        """Get the stress tensor at a specific time."""
        if timestamp not in self.data.index:
            raise KeyError("No data for specified timestamp")
        
        row = self.data.loc[timestamp]
        return StressTensor([row.xx, row.yy, row.zz, row.xy, row.yz, row.xz])

    def get_time_series(self, component: str) -> pd.Series:
        """Get time series for a specific component."""
        if component not in self.data.columns:
            raise ValueError(f"Invalid component: {component}")
        return self.data[component]

    def get_von_mises_history(self) -> pd.Series:
        """Calculate von Mises stress history."""
        von_mises = []
        for idx in self.data.index:
            tensor = self.get_tensor(idx)
            von_mises.append(tensor.von_mises)
        return pd.Series(von_mises, index=self.data.index)

    def get_principal_stress_history(self) -> pd.DataFrame:
        """Calculate principal stress history."""
        principal_stresses = []

        for idx in self.data.index:
            tensor = self.get_tensor(idx)
            principal_stress, principal_vector = tensor.principal_stresses
            principal_stresses.append(list(principal_stress) + list(principal_vector))
        return pd.DataFrame(principal_stresses, index=self.data.index, columns=['principal1', 'principal2', 'principal3', 'vector1', 'vector2', 'vector3'])
        

    def get_signed_von_mises_history(self) -> pd.Series:
        """Calculate signed von Mises stress history."""
        signed_vm = []
        for idx in self.data.index:
            tensor = self.get_tensor(idx)
            signed_vm.append(tensor.signed_von_mises)
        return pd.Series(signed_vm, index=self.data.index)

    def get_tresca_history(self) -> pd.Series:
        """Calculate Tresca stress history."""
        tresca = []
        for idx in self.data.index:
            tensor = self.get_tensor(idx)
            tresca.append(tensor.tresca)
        return pd.Series(tresca, index=self.data.index)

    def get_signed_tresca_history(self) -> pd.Series:
        """Calculate signed Tresca stress history."""
        signed_tresca = []
        for idx in self.data.index:
            tensor = self.get_tensor(idx)
            signed_tresca.append(tensor.signed_tresca)
        return pd.Series(signed_tresca, index=self.data.index)

if __name__ == "__main__":
    # Example usage
    ts = TimeSeriesStressTensor()

    # Add some stress tensors
    tensor1 = StressTensor([-100, -50, -30, -20, -10, -5])  # Compressive stress state
    tensor2 = StressTensor([150, 250, 350, 55, 65, 75])     # Tensile stress state
    ts.add_tensor(tensor1)
    ts.add_tensor(tensor2)

    # Get stress histories
    print("\nVon Mises History:")
    print(ts.get_von_mises_history())
    
    print("\nSigned Von Mises History:")
    print(ts.get_signed_von_mises_history())
    
    print("\nPrincipal Stress History:")
    print(ts.get_principal_stress_history())
    
    print("\nTresca History:")
    print(ts.get_tresca_history())
    
    print("\nSigned Tresca History:")
    print(ts.get_signed_tresca_history())