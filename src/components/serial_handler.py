import serial
import serial.tools.list_ports
import time
from typing import List, Optional

class SerialHandler:
    def __init__(self, baudrate: int = 9600):
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        
    def get_available_ports(self) -> List[str]:
        """List all available serial ports"""
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def connect(self, port: str) -> bool:
        """Connect to specified serial port"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.disconnect()
                
            self.serial_port = serial.Serial(port, self.baudrate)
            time.sleep(2)  # Wait for Arduino to reset
            return True
        except serial.SerialException as e:
            raise Exception(f"Failed to connect to {port}: {str(e)}")
    
    def disconnect(self) -> None:
        """Safely disconnect from serial port"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
        except serial.SerialException as e:
            raise Exception(f"Error disconnecting: {str(e)}")
    
    def read_data(self) -> Optional[float]:
        """Read one line of data from serial port"""
        if not self.serial_port or not self.serial_port.is_open:
            raise Exception("Serial port not connected")
        
        try:
            line = self.serial_port.readline().decode().strip()
            return float(line)
        except (ValueError, UnicodeDecodeError, serial.SerialException) as e:
            return None
