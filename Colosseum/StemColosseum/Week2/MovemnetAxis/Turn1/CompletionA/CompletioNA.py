# Override older left/right inputs with newer ones instead of cancelling out the directions
func _get_latest_movement_axis():
	var axis = Input.get_axis("left", "right")

	left_input_frame = (
		max(left_input_frame, right_input_frame) + 1
		if Input.is_action_just_pressed("left")
		else 0 if Input.is_action_just_released("left") else left_input_frame
	)
	right_input_frame = (
		max(left_input_frame, right_input_frame) + 1
		if Input.is_action_just_pressed("right")
		else 0 if Input.is_action_just_released("right") else right_input_frame
	)
