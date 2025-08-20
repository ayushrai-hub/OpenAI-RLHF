from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class Endian(Enum):
    LITTLE = "little"
    BIG = "big"
    AUTO = "auto"

@dataclass
class ModbusConnection:
    port: str
    baud_rate: int
    data_bits: int = 8
    parity: str = "N"
    stop_bits: int = 1
    timeout: int = 10

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusConnection":
        port = json_data.get("port")
        baud_rate = json_data.get("baudRate")
        data_bits = json_data.get("byteSize", 8)

        parity_to_internal = {"none": "N", "even": "E", "odd": "O"}
        parity = parity_to_internal.get(json_data.get("parity", "none"), "N")

        stop_bits = json_data.get("stopBits", 1)
        timeout = json_data.get("timeout", 10)

        if not port or not isinstance(port, str):
            raise ValueError("Invalid or empty 'port' value")

        if not isinstance(baud_rate, int) or baud_rate <= 0:
            raise ValueError("Invalid or non-positive 'baudRate' value")

        if data_bits not in [7, 8]:
            raise ValueError("Invalid 'byteSize' value, must be 7 or 8")

        if parity not in parity_to_internal.values():
            raise ValueError("Invalid 'parity' value, must be 'none', 'even', or 'odd'")

        if stop_bits not in [1, 1.5, 2]:
            raise ValueError("Invalid 'stopBits' value, must be 1, 1.5, or 2")

        if timeout <= 0:
            raise ValueError("Invalid or non-positive 'timeout' value")

        return cls(port, baud_rate, data_bits, parity, stop_bits, timeout)

@dataclass
class ModbusSignal:
    address: int
    name: str
    data_type: str
    count: int = 1
    k: int = 1

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusSignal":
        address = json_data.get("address")
        name = json_data.get("name")
        data_type = json_data.get("type")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)

        if address is None:
            raise ValueError("'address' can't be undefined!")
        if name is None:
            raise ValueError("'name' can't be undefined!")
        if data_type is None:
            raise ValueError("'data_type' can't be undefined!")
        if count is None or count <= 0:
            raise ValueError("'count' must be positive!")
        if k is None or k <= 0:
            raise ValueError("'k' must be positive!")

        if isinstance(address, str):
            if not address.startswith("0x"):
                raise ValueError(f"Invalid address format: {address}")
            try:
                address = int(address, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal address: {address}")

        return cls(address, name, data_type, count, k)

@dataclass
class ModbusGroupSignal:
    name: Optional[str] = None
    skip: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        name = json_data.get("name")
        skip = json_data.get("skip")

        if name is None and skip is None:
            raise ValueError("Either 'name' or 'skip' must be defined for group signals.")

        if skip is not None:
            if not isinstance(skip, int) or skip <= 0:
                raise ValueError("'skip' must be a positive integer.")

        return cls(name, skip)

@dataclass
class ModbusGroup:
    name: str
    start_address: int
    signals: List[ModbusGroupSignal]
    data_type: Optional[str] = None
    nbytes: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroup":
        name = json_data.get("name")
        start_address = json_data.get("startAddress")
        signals_data: Optional[List[Dict[str, Any]]] = json_data.get("signals")
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if name is None:
            raise ValueError("'name' can't be undefined!")

        if start_address is None:
            raise ValueError("'startAddress' can't be undefined!")

        if data_type is not None and data_type != "bit":
            raise ValueError("The only supported 'type' for the group is 'bit'")

        if data_type == "bit" and nbytes is None:
            raise ValueError("You must set 'bytes' to define how many bytes to transform into bits")

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
        ORDER_MAPPING = {"lt": Endian.LITTLE, "be": Endian.BIG, "auto": Endian.AUTO}

        slave_id = json_data.get("slaveId")
        name = json_data.get("name")
        poll_period = json_data.get("pollPeriod", 60)
        byte_order = ORDER_MAPPING.get(json_data.get("byteOrder", "lt"))
        word_order = ORDER_MAPPING.get(json_data.get("wordOrder", "be"))
        signals_data: Optional[List[Dict[str, Any]]] = json_data.get("signals", [])
        groups_data: Optional[List[Dict[str, Any]]] = json_data.get("groups", [])

        if slave_id is None:
            raise ValueError("'slaveId' can't be undefined!")
        if name is None:
            raise ValueError("'name' can't be undefined!")
        if byte_order is None:
            raise ValueError("'byteOrder' is invalid, must be 'lt', 'be', or 'auto'!")
        if word_order is None:
            raise ValueError("'wordOrder' is invalid, must be 'lt', 'be', or 'auto'!")

        signals = [ModbusSignal.from_json(signal) for signal in signals_data]
        groups = [ModbusGroup.from_json(group) for group in groups_data]

        return cls(slave_id, name, poll_period, signals, groups, byte_order, word_order)
