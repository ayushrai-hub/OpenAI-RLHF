from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class Endian(Enum):
    LITTLE = "LITTLE"
    BIG = "BIG"
    AUTO = "AUTO"

@dataclass
class BaseModbusSignal:
    """Base class for Modbus signals with common attributes.

    Attributes:
        name (str): Name of the Modbus signal.
        count (int): Data count for the Modbus signal.
        k (int): Value of k for the Modbus signal.
    """
    name: str
    count: int = 1
    k: int = 1

    @staticmethod
    def _validate_common_fields(name: Optional[str], count: Optional[int], k: Optional[int]) -> None:
        """Validate common fields for all signal types."""
        if name is None:
            raise ValueError("'name' can't be undefined!")
        if count is None:
            raise ValueError("'count' can't be undefined!")
        if k is None:
            raise ValueError("'k' can't be undefined!")

@dataclass
class ModbusSignal(BaseModbusSignal):
    """Class representing a standalone Modbus signal.

    Attributes:
        address (int): Address of the Modbus signal.
        data_type (str): Data type of the Modbus signal.
    """
    address: int
    data_type: str

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusSignal":
        """Build ModbusSignal instance from JSON data.

        Args:
            json_data (Dict[str, Any]): JSON with signal details.

        Returns:
            ModbusSignal: A new instance.

        Raises:
            ValueError: If necessary fields are missing or wrong in the JSON.
        """
        address = json_data.get("address")
        name = json_data.get("name")
        data_type = json_data.get("type")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)

        cls._validate_common_fields(name, count, k)

        if address is None:
            raise ValueError("'address' can't be undefined!")
        if data_type is None:
            raise ValueError("'data_type' can't be undefined!")

        if isinstance(address, str):
            if not address.startswith("0x"):
                raise ValueError(f"Invalid address format: {address}")
            try:
                address = int(address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {address}")

        return cls(name=name, count=count, k=k, address=address, data_type=data_type)

@dataclass
class ModbusGroupSignal(BaseModbusSignal):
    """Class representing a Modbus signal within a group.

    Attributes:
        skip (Optional[int]): Number of bits to skip before this signal.
    """
    skip: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        """Build ModbusGroupSignal instance from JSON data.

        Args:
            json_data (Dict[str, Any]): JSON with signal details.

        Returns:
            ModbusGroupSignal: A new instance.

        Raises:
            ValueError: If necessary fields are missing or wrong in the JSON.
        """
        name = json_data.get("name")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)
        skip = json_data.get("skip")

        if skip is None and name is None:
            raise ValueError("Either 'name' or 'skip' must be defined for group signals!")

        # If it's a skip signal, we don't need to validate the name
        if skip is not None and name is None:
            name = f"skip_{skip}"

        cls._validate_common_fields(name, count, k)

        return cls(name=name, count=count, k=k, skip=skip)

@dataclass
class ModbusGroup:
    """Class representing a group of Modbus signals.

    Attributes:
        name (str): Name of the group.
        start_address (int): Starting address of the group.
        signals (List[ModbusGroupSignal]): List of signals in the group.
        data_type (Optional[str]): Data type for the group.
        nbytes (Optional[int]): Number of bytes for bit groups.
    """
    name: str
    start_address: int
    signals: List[ModbusGroupSignal]
    data_type: Optional[str] = None
    nbytes: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroup":
        """Construct ModbusGroup instance from JSON data."""
        name = json_data.get("name")
        start_address = json_data.get("startAddress")
        signals_data = json_data.get("signals")
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if name is None:
            raise ValueError("'name' can't be undefined!")
        if start_address is None:
            raise ValueError("'startAddress' can't be undefined!")
        if data_type is not None and data_type != "bit":
            raise ValueError("The only supported 'type' for the group is 'bit'")
        if data_type == "bit" and nbytes is None:
            raise ValueError("You must set the number of bytes to transform into bits")
        if not signals_data:
            raise ValueError(f"You have to add at least one signal to the group '{name}'")

        if isinstance(start_address, str):
            if not start_address.startswith("0x"):
                raise ValueError(f"Invalid address format: {start_address}")
            try:
                start_address = int(start_address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {start_address}")

        signals = [ModbusGroupSignal.from_json(signal) for signal in signals_data]

        return cls(name, start_address, signals, data_type, nbytes)
