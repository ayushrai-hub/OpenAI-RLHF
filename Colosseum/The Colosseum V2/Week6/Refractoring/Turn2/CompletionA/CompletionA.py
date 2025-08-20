from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class BaseModbusSignal:
    """Base class defining common properties for Modbus signals."""
    address: Optional[int]
    name: Optional[str]
    data_type: Optional[str]
    count: int = 1
    k: int = 1

    @classmethod
    def validate_common_fields(cls, json_data: Dict[str, Any]):
        """Validates shared signal fields."""
        address = json_data.get("address")
        name = json_data.get("name")
        data_type = json_data.get("type")

        if name is None:
            raise ValueError("'name' can't be undefined!")

        if data_type is None:
            raise ValueError("'type' can't be undefined!")
            
        if isinstance(address, str) and not address.startswith("0x"):
            raise ValueError(f"Invalid address format: {address}")
        
        return address, name, data_type


@dataclass
class ModbusSignal(BaseModbusSignal):
    """Class representing a standalone Modbus signal."""
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusSignal":
        """Builds ModbusSignal instance from JSON data for standalone usage."""
        address, name, data_type = cls.validate_common_fields(json_data)
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)

        if address is None:
            raise ValueError("'address' can't be undefined!")

        if isinstance(address, str):
            try:
                address = int(address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {address}")

        return cls(address, name, data_type, count, k)


@dataclass
class ModbusGroupSignal(BaseModbusSignal):
    """Class representing a Modbus signal within a group."""
    skip: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        """Builds ModbusGroupSignal instance from JSON data for grouped usage."""
        address, name, data_type = cls.validate_common_fields(json_data)
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)
        skip = json_data.get("skip")

        if skip is None and name is None:
            raise ValueError("'name' can't be undefined in a group signal!")

        return cls(address, name, data_type, count, k, skip)


@dataclass
class ModbusGroup:
    """Class defining a Modbus group that holds multiple ModbusGroupSignals."""
    name: str
    start_address: int
    signals: List[ModbusGroupSignal]
    data_type: Optional[str] = None
    nbytes: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroup":
        """Constructs ModbusGroup instance from JSON data."""
        name = json_data.get("name")
        start_address = json_data.get("startAddress")
        signals_data: Optional[List[Dict[str, Any]]] = json_data.get("signals")
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if name is None:
            raise ValueError("'name' can't be undefined!")

        if start_address is None:
            raise ValueError("'startAddress' can't be undefined!")

        if not signals_data:
            raise ValueError(f"You must add at least one signal to the group '{name}'!")

        # Convert HEX string to integer if necessary
        if isinstance(start_address, str):
            if not start_address.startswith("0x"):
                raise ValueError(f"Invalid address format: {start_address}")
            try:
                start_address = int(start_address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {start_address}")

        signals = [ModbusGroupSignal.from_json(signal) for signal in signals_data]

        return cls(name, start_address, signals, data_type, nbytes)
