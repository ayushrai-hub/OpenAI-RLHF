from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

@dataclass
class ModbusSignal:
    """Standalone Modbus signal."""

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
            raise ValueError("'address' can't be undefined for standalone signals!")
        if name is None:
            raise ValueError("'name' can't be undefined for standalone signals!")
        if data_type is None:
            raise ValueError("'data_type' can't be undefined for standalone signals!")

        address = cls.parse_address(address)

        return cls(address, name, data_type, count, k)

    @staticmethod
    def parse_address(address: Union[str, int]) -> int:
        if isinstance(address, str):
            if address.startswith("0x"):
                try:
                    return int(address, 16)
                except ValueError:
                    raise ValueError(f"Invalid hexadecimal address: {address}")
            else:
                raise ValueError(f"Invalid address format: {address}")
        return address
@dataclass
class ModbusGroupSignal:
    """Signal contained within a Modbus group."""

    name: Optional[str] = None
    skip: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        name = json_data.get("name")
        skip = json_data.get("skip")

        if name is None and skip is None:
            raise ValueError("Group signals must either define 'name' or 'skip'!")

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
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if name is None:
            raise ValueError("'name' can't be undefined for a group!")
        if start_address is None:
            raise ValueError("'startAddress' can't be undefined for a group!")

        if data_type is not None and data_type != "bit":
            raise ValueError("Currently, only 'bit' type is supported for groups!")
        if data_type == "bit" and nbytes is None:
            raise ValueError("Number of bytes ('bytes') must be set when 'type' is 'bit'!")

        start_address = ModbusSignal.parse_address(start_address)

        signals_data = json_data.get("signals")
        if not signals_data:
            raise ValueError(f"At least one signal must be defined within group '{name}'!")

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
        byte_order = ORDER_MAPPING.get(json_data.get("byteOrder", "lt"), Endian.LITTLE)
        word_order = ORDER_MAPPING.get(json_data.get("wordOrder", "be"), Endian.BIG)

        signals_data = json_data.get("signals", [])
        groups_data = json_data.get("groups", [])

        if slave_id is None:
            raise ValueError("'slaveId' must be defined!")
        if name is None:
            raise ValueError("'name' must be defined!")

        signals = [ModbusSignal.from_json(signal) for signal in signals_data]
        groups = [ModbusGroup.from_json(group) for group in groups_data]

        return cls(slave_id, name, poll_period, signals, groups, byte_order, word_order)
