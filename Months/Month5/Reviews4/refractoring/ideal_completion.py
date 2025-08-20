# ideal_completion.py
class PlateMap:
    def __init__(self, plate_map_data):
        self._plate_map_data = plate_map_data

    def _compile_conditions(self) -> list[str]:
        treatment_list = []
        for value in self._plate_map_data.values():
            treatment = value["condition_2"]
            if treatment not in treatment_list:
                treatment_list.append(treatment)
        return treatment_list