class PlateMap:
    def __init__(self, plate_map_data):
        self._plate_map_data = plate_map_data

    def _compile_conditions(self) -> list[str]:
        return list({value["condition_2"] for value in self._plate_map_data.values()})
