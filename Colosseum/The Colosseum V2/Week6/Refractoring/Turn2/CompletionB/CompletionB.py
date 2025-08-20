from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class Endian(Enum):
    LITTLE = 1
    BIG = 2
    AUTO = 3


@dataclass
class ModbusConnection:
    """Class defining properties for Modbus connection.

    Attributes:
        port (str): Modbus communication port.
        baud_rate (int): Communication baud rate.
        data_bits (int): Data bits count. Defaults to 8.
        parity (str): Parity setting ("N" for none, "E" for even, "O" for odd). Defaults to "N".
        stop_bits (int): Stop bits count. Defaults to 1.
        timeout (int): Communication timeout (in seconds). Defaults to 10.
    """

    port: str
    baud_rate: int
    data_bits: int = 8
    parity: str = "N"
    stop_bits: int = 1
    timeout: int = 10

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusConnection":
        """Construct ModbusConnection from JSON input.

        Args:
            json_data (Dict[str, Any]): JSON with connection details.

        Returns:
            ModbusConnection: An instance of ModbusConnection.

        Raises:
            ValueError: If fields are missing or invalid in the JSON input.
        """
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
    """Class representing a standalone Modbus signal.

    Attributes:
        address (int): Address of the Modbus signal.
        name (str): Name of the Modbus signal.
        data_type (str): Data type of the Modbus signal.
        count (int, optional): Data count for the Modbus signal.
        k (int, optional): Value of k for the Modbus signal.
    """

    address: int
    name: str
    data_type: str
    count: int = 1
    k: int = 1

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

        if address is None:
            raise ValueError("'address' can't be undefined for standalone signal!")

        if name is None:
            raise ValueError("'name' can't be undefined for standalone signal!")

        if data_type is None:
            raise ValueError("'type' can't be undefined for standalone signal!")

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
    """Class representing a Modbus signal within a group.

    Attributes:
        name (str): Name of the signal. Can be None if skip is provided.
        count (int): Data count for the signal.
        k (int): Value of k for the signal.
        skip (int, optional): Number of bits to skip.
    """

    name: Optional[str]
    count: int = 1
    k: int = 1
    skip: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroupSignal":
        """Build ModbusGroupSignal instance from JSON data.

        Args:
            json_data (Dict[str, Any]): JSON with group signal details.

        Returns:
            ModbusGroupSignal: A new instance.

        Raises:
            ValueError: If necessary fields are missing or wrong in the JSON.
        """
        name = json_data.get("name")
        count = json_data.get("count", 1)
        k = json_data.get("k", 1)
        skip = json_data.get("skip")

        if name is None and skip is None:
            raise ValueError("Either 'name' or 'skip' must be defined for group signal!")

        return cls(name, count, k, skip)


@dataclass
class ModbusGroup:
    """Class representing a group of Modbus signals.

    Attributes:
        name (str): Name of the group.
        start_address (int): Starting address of the group.
        signals (List[ModbusGroupSignal]): List of signals within the group.
        data_type (str, optional): Data type for the group.
        nbytes (int, optional): Number of bytes when data_type is 'bit'.
    """

    name: str
    start_address: int
    signals: List[ModbusGroupSignal]
    data_type: Optional[str] = None
    nbytes: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusGroup":
        """Construct ModbusGroup instance from JSON data.

        Args:
            json_data (Dict[str, Any]): JSON with group details.

        Returns:
            ModbusGroup: A new ModbusGroup instance.

        Raises:
            ValueError: If fields are missing or invalid in the JSON.
        """
        name = json_data.get("name")
        start_address = json_data.get("startAddress")
        signals_data: Optional[List[Dict[str, Any]]] = json_data.get("signals")
        data_type = json_data.get("type")
        nbytes = json_data.get("bytes")

        if name is None:
            raise ValueError("'name' can't be undefined for group!")

        if start_address is None:
            raise ValueError("'startAddress' can't be undefined for group!")

        if data_type is not None and data_type != "bit":
            raise ValueError("The only supported 'type' for the group is 'bit'")

        if data_type == "bit" and nbytes is None:
            raise ValueError("You must set the number of bytes to transform into bits for a bit group")

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
    """Class defining a Modbus device.

    Attributes:
        slave_id (int): Slave ID of the device.
        name (str): Name of the device.
        poll_period (int): Poll period in seconds.
        signals (List[ModbusSignal]): List of standalone signals for the device.
        groups (List[ModbusGroup]): List of signal groups for the device.
        byte_order (Endian): Byte order (LITTLE, BIG, or AUTO).
        word_order (Endian): Word order (LITTLE, BIG, or AUTO).
    """

    slave_id: int
    name: str
    poll_period: int
    signals: List[ModbusSignal]
    groups: List[ModbusGroup]
    byte_order: Endian = Endian.LITTLE
    word_order: Endian = Endian.BIG

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "ModbusDevice":
        """Create ModbusDevice from JSON input.

        Args:
            json_data (Dict[str, Any]): JSON containing device details.

        Returns:
            ModbusDevice: A new ModbusDevice instance.

        Raises:
            ValueError: If required data is missing or invalid in JSON.
        """
        ORDER_MAPPING = {"lt": Endian.LITTLE, "be": Endian.BIG, "auto": Endian.AUTO}

        slave_id = json_data.get("slaveId")
        name = json_data.get("name")
        poll_period = json_data.get("pollPeriod", 60)
        byte_order = ORDER_MAPPING.get(json_data.get("byteOrder", "lt"), Endian.LITTLE)
        word_order = ORDER_MAPPING.get(json_data.get("wordOrder", "be"), Endian.BIG)
        signals_data: Optional[List[Dict[str, Any]]] = json_data.get("signals", [])
        groups_data: Optional[List[Dict[str, Any]]] = json_data.get("groups", [])

        if slave_id is None:
            raise ValueError("'slaveId' can't be undefined for device!")

        if name is None:
            raise ValueError("'name' can't be undefined for device!")

        if poll_period is None:
            raise ValueError("'pollPeriod' can't be undefined for device!")

        if not isinstance(byte_order, Endian):
            raise ValueError("'byteOrder' is invalid, must be 'lt', 'be', or 'auto'")

        if not isinstance(word_order, Endian):
            raise ValueError("'wordOrder' is invalid, must be 'lt', 'be', or 'auto'")

        signals = [ModbusSignal.from_json(signal) for signal in signals_data]
        groups = [ModbusGroup.from_json(group) for group in groups_data]

        return cls(slave_id, name, poll_period, signals, groups, byte_order, word_order)
