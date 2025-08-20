from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class Endian(Enum):
    LITTLE = "lt"
    BIG = "be"
    AUTO = "auto"


@dataclass
class ModbusSignal:
    """Class representing a standalone Modbus signal.

    Attributes:
        address (int): Address of the Modbus signal.
        name (str): Name of the Modbus signal.
        data_type (str): Data type of the Modbus signal.
        count (int): Number of data points for the Modbus signal. Defaults to 1.
        k (int): Scaling factor for the Modbus signal. Defaults to 1.
    """

    address: int
    name: str
    data_type: str
    count: int = 1
    k: int = 1

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusSignal":
        """Constructs a standalone ModbusSignal instance from JSON data."""

        address = json_data.get("address")
        name = json_data.get("name")
        data_type = json_data.get("type")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)

        # Validation
        if address is None:
            raise ValueError("'address' can't be undefined for a standalone signal.")

        if isinstance(address, str):
            if not address.startswith("0x"):
                raise ValueError(f"Invalid address format: {address}")
            try:
                address = int(address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {address}")

        if name is None:
            raise ValueError("'name' can't be undefined for a standalone signal.")

        if data_type is None:
            raise ValueError("'data_type' can't be undefined.")

        if count <= 0:
            raise ValueError("'count' must be positive.")

        if k == 0:
            raise ValueError("'k' can't be zero.")

        return cls(address, name, data_type, count, k)


@dataclass
class ModbusGroupSignal:
    """Class representing a Modbus signal within a group.

    Attributes:
        name (Optional[str]): Name of the signal.
        address (Optional[int]): Address within the group (optional).
        skip (Optional[int]): Bytes to skip in the group (optional).
        count (int): Number of data points. Defaults to 1.
        k (int): Scaling factor. Defaults to 1.
    """

    name: Optional[str] = None
    address: Optional[int] = None
    skip: Optional[int] = None
    count: int = 1
    k: int = 1

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        """Constructs a ModbusGroupSignal instance from JSON data."""

        address = json_data.get("address")
        name = json_data.get("name")
        skip = json_data.get("skip")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)

        # Validation
        if skip is None and name is None:
            raise ValueError("Either 'skip' or 'name' must be provided in a group signal.")

        if address is not None and isinstance(address, str):
            if not address.startswith("0x"):
                raise ValueError(f"Invalid address format: {address}")
            try:
                address = int(address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {address}")

        if count <= 0:
            raise ValueError("'count' must be positive.")

        if k == 0:
            raise ValueError("'k' can't be zero.")

        return cls(name, address, skip, count, k)


@dataclass
class ModbusGroup:
    name: str
    start_address: int
    signals: List[ModbusGroupSignal]
    data_type: Optional[str] = None
    nbytes: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroup":
        """Construct a ModbusGroup instance from JSON data."""

        name = json_data.get("name")
        start_address = json_data.get("startAddress")
        signals_data = json_data.get("signals")
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if not name:
            raise ValueError("'name' can't be undefined.")

        if isinstance(start_address, str):
            if not start_address.startswith("0x"):
                raise ValueError(f"Invalid address format: {start_address}")
            try:
                start_address = int(start_address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {start_address}")

        signals = [ModbusGroupSignal.from_json(sig) for sig in signals_data]

        return cls(name, start_address, signals, data_type, nbytes)


@dataclass
class ModbusDevice:
    slave_id: int
    name: str
    poll_period: int
    signals: List[ModbusSignal]
    groups: List[ModbusGroup]
    byte_order: Endian = Endian.LITTLE
    word_order: Endian = Endian.BIG

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusDevice":
        """Create a ModbusDevice from JSON input."""

        ORDER_MAPPING = {
            "lt": Endian.LITTLE,
            "be": Endian.BIG,
            "auto": Endian.AUTO,
        }

        slave_id = json_data.get("slaveId")
        name = json_data.get("name")
        poll_period = json_data.get("pollPeriod", 60)
        byte_order = ORDER_MAPPING.get(json_data.get("byteOrder", "lt"))
        word_order = ORDER_MAPPING.get(json_data.get("wordOrder", "be"))
        signals_data = json_data.get("signals", [])
        groups_data = json_data.get("groups", [])

        signals = [ModbusSignal.from_json(sig) for sig in signals_data]
        groups = [ModbusGroup.from_json(grp) for grp in groups_data]

        return cls(slave_id, name, poll_period, signals, groups, byte_order, word_order)
