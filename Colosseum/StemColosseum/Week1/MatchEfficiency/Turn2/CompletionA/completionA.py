import copy
import time
import pandas as pd

# Fill missing data in the DataFrame
df = df.fillna('')

# Precompute and store necessary data to reduce repeated DataFrame lookups
user_data_cache = df.set_index('User ID').to_dict('index')

def measure_matching_efficiency(df, preference, groups):
    outputs = []
    aggregate_weightage = sum(abs(q[1]) for q in preference)
    query_weight = {q[0]: (abs(q[1]) / aggregate_weightage) * 100 for q in preference}

    for group in groups:
        group_outputs = []
        overall_group_efficiency = 0
        column_by_efficiency = {}

        # Precompute alternate user data for each group member to avoid repeated DataFrame operations
        group_user_data = {user_id: user_data_cache.get(user_id, {}) for user_id in group}
        all_ask_tags = {uid: set(x.strip() for x in data.get('Ask', '').split(',') if x.strip()) for uid, data in group_user_data.items()}
        all_offer_tags = {uid: set(x.strip() for x in data.get('Offer', '').split(',') if x.strip()) for uid, data in group_user_data.items()}

        for user_id in group:
            column_patient = []
            paired_tags_set = set()
            patient_data = group_user_data[user_id]

            if not patient_data:
                continue

            patient_efficiency = 0

            for pref in preference:
                column_name, pref_style, column_style = pref
                alternate_user_ids = [other for other in group if other != user_id]

                if not alternate_user_ids:
                    continue

                # Evaluate based on column style
                if column_style == 9:
                    # Special case handling for 'Ask' and 'Offer' columns
                    patient_ask = all_ask_tags[user_id]
                    patient_offer = all_offer_tags[user_id]
                    alt_patient_ask_tags = set().union(*(all_ask_tags[other] for other in alternate_user_ids))
                    alt_patient_offer_tags = set().union(*(all_offer_tags[other] for other in alternate_user_ids))

                    paired_ask = paired_offer = 0

                    if pref_style > 0:
                        # Positive preference: matched ask with offer and vice versa
                        matched_ask = patient_ask & alt_patient_offer_tags
                        matched_offer = patient_offer & alt_patient_ask_tags
                        paired_ask += len(matched_ask)
                        paired_offer += len(matched_offer)
                        paired_tags_set.update(matched_ask)
                        paired_tags_set.update(matched_offer)
                    else:
                        # Negative preference: unmatched tags (those not found in alternate group members)
                        unmatched_ask = patient_ask - alt_patient_offer_tags
                        unmatched_offer = patient_offer - alt_patient_ask_tags
                        paired_ask += len(unmatched_ask)
                        paired_offer += len(unmatched_offer)
                        paired_tags_set.update(unmatched_ask)
                        paired_tags_set.update(unmatched_offer)

                    column_efficiency = query_weight[column_name] if (paired_ask > 0 or paired_offer > 0) else 0
                    patient_efficiency += column_efficiency
                    column_patient.append(column_efficiency)

                elif column_style == 5:
                    # For column style 5: comparing user IDs
                    patient_tags_str = patient_data.get(column_name, '')
                    patient_tags = {int(tag.strip()) for tag in patient_tags_str.split(",") if tag.strip().isdigit()}
                    alternate_members = set(alternate_user_ids)

                    if pref_style > 0:
                        # Positive preference: matches between patient tags and alternate members
                        matched_tags = patient_tags & alternate_members
                        paired_tags = len(matched_tags)
                    else:
                        # Negative preference: tags that are not present in alternate members
                        unmatched_tags = patient_tags - alternate_members
                        paired_tags = len(unmatched_tags)

                    column_efficiency = query_weight[column_name] if paired_tags > 0 else 0
                    patient_efficiency += column_efficiency
                    column_patient.append(column_efficiency)

                else:
                    # For other column styles: generic tag matching
                    patient_tags_str = patient_data.get(column_name, '')
                    patient_tags = {tag.strip() for tag in patient_tags_str.split(",") if tag.strip()}
                    alt_patient_all_tags = {tag.strip() for alt_id in alternate_user_ids for tag in group_user_data[alt_id].get(column_name, '').split(',') if tag.strip()}

                    if pref_style > 0:
                        # Positive preference: match tags
                        matched_tags = patient_tags & alt_patient_all_tags
                        paired_tags = len(matched_tags)
                        paired_tags_set.update(matched_tags)
                        column_efficiency = query_weight[column_name] if paired_tags > 0 else 0
                    else:
                        # Negative preference: unmatched tags
                        matched_tags_count = len(patient_tags & alt_patient_all_tags)
                        unmatched_tags_count = len(patient_tags) - matched_tags_count
                        unmatched_tags = patient_tags - alt_patient_all_tags
                        paired_tags_set.update(unmatched_tags)
                        column_efficiency = (unmatched_tags_count / len(patient_tags) * query_weight[column_name]) if patient_tags else 0

                    patient_efficiency += column_efficiency
                    column_patient.append(column_efficiency)

            column_by_efficiency[user_id] = column_patient
            group_outputs.append({
                "User ID": user_id,
                "Matching Efficiency (%)": patient_efficiency,
                "Paired_Tags": paired_tags_set
            })
            overall_group_efficiency += patient_efficiency

        group_avg_efficiency = overall_group_efficiency / len(group) if group else 0

        outputs.append({
            "Group": group,
            "Group Efficiency (%)": group_avg_efficiency,
            "Members": group_outputs,
            "Column Efficiency": sum((v[0] if v else 0) for v in column_by_efficiency.values())
        })

    return outputs

start_time = time.time()

def try_change_groups(df, preference, start_groups, begin_efficiency, top_efficiency, outputs):
    improved_groups = copy.deepcopy(start_groups)
    begin_efficiency_list = copy.deepcopy(begin_efficiency)
    num_groups = len(improved_groups)

    processed_pairs = set()
    restart_outer_loop = True

    while restart_outer_loop:
        restart_outer_loop = False
        for i in range(num_groups):
            first_group_keys = list(begin_efficiency_list[i].keys())
            first_group = improved_groups[i]

            for j in range(i + 1, num_groups):
                second_group_keys = list(begin_efficiency_list[j].keys())
                second_group = improved_groups[j]

                combined_group_key = tuple(sorted(first_group_keys + second_group_keys))
                if combined_group_key in processed_pairs:
                    continue

                start_first_group_efficiency = sum(begin_efficiency_list[i].values()) / len(begin_efficiency_list[i].values()) if begin_efficiency_list[i].values() else 0
                start_second_group_efficiency = sum(begin_efficiency_list[j].values()) / len(begin_efficiency_list[j].values()) if begin_efficiency_list[j].values() else 0

                if start_first_group_efficiency >= top_efficiency and start_second_group_efficiency >= top_efficiency:
                    processed_pairs.add(combined_group_key)
                    continue

                change_done = False
                for first_member in first_group_keys:
                    for second_member in second_group_keys:
                        if first_member in first_group and second_member in second_group:
                            new_first_group = [member for member in first_group if member != first_member] + [second_member]
                            new_second_group = [member for member in second_group if member != second_member] + [first_member]

                            each_group_result = measure_matching_efficiency(df, preference, [new_first_group, new_second_group])
                            new_first_group_efficiency = each_group_result[0]['Group Efficiency (%)']
                            new_second_group_efficiency = each_group_result[1]['Group Efficiency (%)']

                            first_group_column_efficiency = outputs[i]['Column Efficiency']
                            second_group_column_efficiency = outputs[j]['Column Efficiency']

                            new_first_group_column_efficiency = each_group_result[0]['Column Efficiency']
                            new_second_group_column_efficiency = each_group_result[1]['Column Efficiency']

                            if (new_first_group_efficiency > start_first_group_efficiency and
                                new_second_group_efficiency >= start_second_group_efficiency and
                                new_first_group_column_efficiency >= first_group_column_efficiency and
                                new_second_group_column_efficiency >= second_group_column_efficiency):

                                updated_begin_efficiency_i = {member['User ID']: member['Matching Efficiency (%)'] for member in each_group_result[0]['Members']}
                                updated_begin_efficiency_j = {member['User ID']: member['Matching Efficiency (%)'] for member in each_group_result[1]['Members']}

                                improved_groups[i] = new_first_group
                                improved_groups[j] = new_second_group
                                begin_efficiency_list[i] = updated_begin_efficiency_i
                                begin_efficiency_list[j] = updated_begin_efficiency_j

                                outputs[i]['Column Efficiency'] = new_first_group_column_efficiency
                                outputs[j]['Column Efficiency'] = new_second_group_column_efficiency

                                # Update the new group keys
                                first_group_keys = list(updated_begin_efficiency_i.keys())
                                second_group_keys = list(updated_begin_efficiency_j.keys())

                                start_first_group_efficiency = new_first_group_efficiency
                                start_second_group_efficiency = new_second_group_efficiency

                                change_done = True
                                restart_outer_loop = True
                                break
                    if change_done:
                        break

                processed_pairs.add(combined_group_key)

                if restart_outer_loop:
                    break
            if restart_outer_loop:
                break
    return improved_groups

# Example usage with the provided data and parameters
groups = [
    [1, 117], [2, 118], [3, 119], [4, 120], [5, 121], [6, 122], [7, 123], [8, 124],
    [9, 125], [10, 126], [11, 127], [12, 128], [13, 129], [14, 130], [15, 131], [16, 132],
    [17, 133], [18, 134], [19, 135], [20, 136], [21, 137], [22, 138], [23, 139], [24, 140],
    [25, 141], [26, 142], [27, 143], [28, 144], [29, 145], [30, 146], [31, 147], [32, 148],
    [33, 149], [34, 150], [35, 151], [36, 152], [37, 153], [38, 154], [39, 155], [40, 156],
    [41, 157], [42, 158], [43, 159], [44, 160], [45, 161], [46, 162], [47, 163], [48, 164],
    [49, 165], [50, 166], [51, 167], [52, 168], [53, 169], [54, 170], [55, 171], [56, 172],
    [57, 173], [58, 174], [59, 175], [60, 176], [61, 177], [62, 178], [63, 179], [64, 180],
    [65, 181], [66, 182], [67, 183], [68, 184], [69, 185], [70, 186], [71, 187], [72, 188],
    [73, 189], [74, 190], [75, 191], [76, 192], [77, 193], [78, 194], [79, 195], [80, 196],
    [81, 197], [82, 198], [83, 199], [84, 200], [85, 201], [86, 202], [87, 203], [88, 204],
    [89, 205], [90, 206], [91, 207], [92, 208], [93, 209], [94, 210], [95, 211], [96, 212],
    [97, 213], [98, 214], [99, 215], [100, 216], [101, 217], [102, 218], [103, 219], [104, 220],
    [105, 221], [106, 222], [107, 223], [108, 224], [109, 225], [110, 226], [111, 113], [112, 114],
    [115, 116]
]

preference = [
    ['27806', -5, 6],
    ['27805', -4, 6],
    ['Ask', 3, 9],
    ['27802', 2, 6]
]

# Measure initial group matching efficiency
outputs = measure_matching_efficiency(df, preference, groups)

group_results_list = []
for idx, result in enumerate(outputs):
    group = result["Group"]
    group_performance = result["Group Efficiency (%)"]
    group_efficiency_data = {m["User ID"]: m["Matching Efficiency (%)"] for m in result["Members"]}

    for member in result["Members"]:
        each_member_tags = ",".join(mem_tag for mem_tag in member["Paired_Tags"] if mem_tag)
        group_results_list.append({
            "Group": group,
            "User ID": member["User ID"],
            "Efficiency": member["Matching Efficiency (%)"],
            "Group Efficiency (%)": group_performance,
            "Tags": each_member_tags
        })

result_df = pd.DataFrame(group_results_list)
result_df = result_df.fillna('')
result_df['Tags'] = result_df['Tags'].apply(lambda x: set(map(str.strip, x.split(','))) if x else set())

efficiency_list = []
for i, group in enumerate(groups):
    group_efficiency = {member["User ID"]: member["Matching Efficiency (%)"] for member in outputs[i]["Members"]}
    efficiency_list.append(group_efficiency)

average_efficiencies = [sum(eff.values()) / len(eff) if eff else 0 for eff in efficiency_list]
top_efficiency = max(average_efficiencies) if average_efficiencies else 0

improved_groups = try_change_groups(df, preference, groups, efficiency_list, top_efficiency, outputs)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
print("Improved Groups:", improved_groups)
