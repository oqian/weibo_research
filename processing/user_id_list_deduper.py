user_id_list_set = set()
with open("validation/user_id_list/out/user_id_list_combined.txt", "r") as file_in:
    for line in file_in:
        user_id_list_set.add(line)

with open("user_id_list_unique.txt", "w") as file_out:
    file_out.writelines(list(user_id_list_set))
