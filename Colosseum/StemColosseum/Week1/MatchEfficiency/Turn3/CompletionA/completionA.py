import copy
import time
import pandas as pd

# Ensure the DataFrame is filled properly
df = df.fillna('')

# Create a mapping of User ID to row data to reduce DataFrame accesses
user_data_cache = df.set_index('User ID').to_dict('index')

def measure_matching_efficiency(df, preference, groups):
    outputs = []
    aggregate_weightage = sum(abs(q[1]) for q in preference)
    query_weight = {q[0]: (abs(q[1]) / aggregate_weightage) * 100 for q in preference}

    for group in groups:
        group_outputs = []
        overall_group_efficiency = 0
        column_by_efficiency = {}

        for user_id in group:
            column_patient = []
            paired_tags_set = set()
            patient_row = user_data_cache.get(user_id, {})

            if not patient_row:
                continue

            patient_efficiency = 0

            for pref in preference:
                column_name, pref_style, column_style = pref
                alternate_user_ids = [other for other in group if other != user_id]
                alternate_user_data = [user_data_cache.get(uid, {}) for uid in alternate_user_ids]

                # Handle different column styles
                if column_style == 9:
                    # 'Ask' and 'Offer' columns
                    patient_ask = {tag.strip() for tag in patient_row.get('Ask', '').split(",") if tag.strip()}
                    patient_offer = {tag.strip() for tag in patient_row.get('Offer', '').split(",") if tag.strip()}

                    alt_patient_ask_tags = set()
                    alt_patient_offer_tags = set()
                    for member in alternate_user_data:
                        alt_patient_ask_tags.update({tag.strip() for tag in member.get('Ask', '').split(",") if tag.strip()})
                        alt_patient_offer_tags.update({tag.strip() for tag in member.get('Offer', '').split(",") if tag.strip()})

                    if pref_style > 0:
                        # Positive preference: match between patient 'Ask' and others' 'Offer' and vice versa
                        paired_ask = patient_ask & alt_patient_offer_tags
                        paired_offer = patient_offer & alt_patient_ask_tags

                        paired_tags_set.update(paired_ask)
                        paired_tags_set.update(paired_offer)

                        column_efficiency = query_weight[column_name] if paired_ask or paired_offer else 0
                    else:
                        # Negative preference: tags in 'Ask'/'Offer' not present in the group's 'Offer'/'Ask'
                        unmatched_ask = patient_ask - alt_patient_offer_tags
                        unmatched_offer = patient_offer - alt_patient_ask_tags

                        paired_tags_set.update(unmatched_ask)
                        paired_tags_set.update(unmatched_offer)

                        column_efficiency = query_weight[column_name] if unmatched_ask or unmatched_offer else 0

                    patient_efficiency += column_efficiency
                    column_patient.append(column_efficiency)

                elif column_style == 5:
                    # Column contains IDs
                    patient_tags = {int(tag.strip()) for tag in patient_row.get(column_name, '').split(",") if tag.strip().isdigit()}
                    alternate_members = set(group) - {user_id}

                    if pref_style > 0:
                        paired_tags = patient_tags & alternate_members
                        column_efficiency = query_weight[column_name] if paired_tags else 0
                    else:
                        unmatched_tags = patient_tags - alternate_members
                        column_efficiency = query_weight[column_name] if unmatched_tags else 0

                    patient_efficiency += column_efficiency
                    column_patient.append(column_efficiency)

                else:
                    # General case for other columns
                    patient_tags = {tag.strip() for tag in patient_row.get(column_name, '').split(",") if tag.strip()}
                    alt_patient_all_tags = set()
                    for member in alternate_user_data:
                        alt_patient_all_tags.update({tag.strip() for tag in member.get(column_name, '').split(",") if tag.strip()})

                    if pref_style > 0:
                        paired_tags = patient_tags & alt_patient_all_tags
                        paired_tags_set.update(paired_tags)
                        column_efficiency = query_weight[column_name] if paired_tags else 0
                    else:
                        unmatched_tags = patient_tags - alt_patient_all_tags
                        paired_tags_set.update(unmatched_tags)
                        column_efficiency = query_weight[column_name] if unmatched_tags else 0

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
            "Column Efficiency": sum(v[0] for v in column_by_efficiency.values() if v)
        })

    return outputs

def try_change_groups(df, preference, start_groups, begin_efficiency, top_efficiency, outputs):
    improved_groups = copy.deepcopy(start_groups)
    begin_efficiency_list = copy.deepcopy(begin_efficiency)
    num_groups = len(improved_groups)

    processed_pairs = set()
    restart_outer_loop = True

    while restart_outer_loop:
        restart_outer_loop = False

        for i in range(num_groups):
            first_group = list(begin_efficiency_list[i].keys())
            for j in range(i + 1, num_groups):
                second_group = list(begin_efficiency_list[j].keys())

                processed_group = tuple(sorted(first_group + second_group))
                if processed_group in processed_pairs:
                    continue

                start_first_group_efficiency = sum(begin_efficiency_list[i].values()) / len(begin_efficiency_list[i]) if begin_efficiency_list[i] else 0
                start_second_group_efficiency = sum(begin_efficiency_list[j].values()) / len(begin_efficiency_list[j]) if begin_efficiency_list[j] else 0

                if start_first_group_efficiency >= top_efficiency and start_second_group_efficiency >= top_efficiency:
                    processed_pairs.add(processed_group)
                    continue

                change_done = False
                for first_member in first_group:
                    for second_member in second_group:
                        new_first_group = first_group.copy()
                        new_second_group = second_group.copy()

                        if first_member in new_first_group and second_member in new_second_group:
                            # Swap members
                            new_first_group.remove(first_member)
                            new_first_group.append(second_member)
                            new_second_group.remove(second_member)
                            new_second_group.append(first_member)

                            each_group_result = measure_matching_efficiency(df, preference, [new_first_group, new_second_group])

                            new_first_group_efficiency = each_group_result[0]['Group Efficiency (%)']
                            new_second_group_efficiency = each_group_result[1]['Group Efficiency (%)']

                            first_group_efficiency = outputs[i]['Column Efficiency']
                            second_group_efficiency = outputs[j]['Column Efficiency']

                            new_first_group_col_efficiency = each_group_result[0]['Column Efficiency']
                            new_second_group_col_efficiency = each_group_result[1]['Column Efficiency']

                            if (new_first_group_efficiency > start_first_group_efficiency and
                                new_second_group_efficiency >= start_second_group_efficiency) and (
                                    new_first_group_col_efficiency >= first_group_efficiency and
                                    new_second_group_col_efficiency >= second_group_efficiency):

                                # Update groups and efficiencies
                                improved_groups[i] = new_first_group
                                improved_groups[j] = new_second_group

                                begin_efficiency_list[i] = {member['User ID']: member['Matching Efficiency (%)'] for member in each_group_result[0]['Members']}
                                begin_efficiency_list[j] = {member['User ID']: member['Matching Efficiency (%)'] for member in each_group_result[1]['Members']}

                                outputs[i]['Column Efficiency'] = new_first_group_col_efficiency
                                outputs[j]['Column Efficiency'] = new_second_group_col_efficiency

                                start_first_group_efficiency = new_first_group_efficiency
                                start_second_group_efficiency = new_second_group_efficiency

                                print('SWAPPED:', first_member, '↔', second_member)
                                change_done = True
                                restart_outer_loop = True
                                break

                    if change_done:
                        break

                processed_pairs.add(processed_group)

                if restart_outer_loop:
                    break

            if restart_outer_loop:
                break

    return improved_groups

# Usage example:

# Assume 'df' is your DataFrame and 'groups' and 'preference' are defined as per your requirements

start_time = time.time()

# Run initial efficiency measurement
outputs = measure_matching_efficiency(df, preference, groups)

# Prepare data for the group optimization function
efficiency_list = []
for result in outputs:
    group_efficiency = {}
    for member in result['Members']:
        group_efficiency[member['User ID']] = member['Matching Efficiency (%)']
    efficiency_list.append(group_efficiency)

# Calculate the top efficiency among all groups
average_efficiencies = [sum(eff.values()) / len(eff) for eff in efficiency_list]
top_efficiency = max(average_efficiencies)

# Optimize groups
improved_groups = try_change_groups(df, preference, groups, efficiency_list, top_efficiency, outputs)

end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
print("Improved Groups:")
for group in improved_groups:
    print(group)
