user_id_list = []
with open("verification_locations_combined.csv", "r") as f:
    for line in f:
        user_id_list.append(line.split(',')[0])

with open("user_id_list.txt", "w") as f:
    f.writelines((user_id+'\n' for user_id in user_id_list))
