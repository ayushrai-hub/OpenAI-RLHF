def get_list_of_doctors_with_jobs():
    pk = "ListDoctorHasJobs"
    sk = "allDoctors"
    
    table = get_lookup_table()
    current_item = table.get_item(
        Key={
            'jobs': pk,
            'doctor_id': sk
        },
        AttributesToGet=['details']
    )
    return current_item.get("Item")
