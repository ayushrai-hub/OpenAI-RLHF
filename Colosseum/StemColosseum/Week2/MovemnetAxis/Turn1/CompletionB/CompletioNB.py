func _get_latest_movement_axis():
    var axis = 0
    
    if Input.is_action_pressed("left"):
        axis -= 1
    if Input.is_action_pressed("right"):
        axis += 1
    
    return axis
