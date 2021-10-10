from typing import Set
from tqdm import tqdm

file1_path = 'user_id_list_sqy.txt'
file2_path = 'user_id_list_qyc.txt'
output_file_path = 'user_id_list_out.txt'


def read_user_id_list(path: str) -> Set[int]:
    print("reading " + path)
    user_id_set = set()
    with open(path, 'r') as file:
        for line in file:
            tokens = line.split(' ')
            user_id = tokens[0]
            if user_id.isdigit():
                user_id_set.add(int(tokens[0]))
            else:
                print("user_id \"%s\" is not parsable to int" % user_id)
    return user_id_set


def main():
    with open(output_file_path, 'w') as file:
        user_id_set1 = read_user_id_list(file1_path)
        user_id_set2 = read_user_id_list(file2_path)
        for user_id in tqdm(user_id_set1.union(user_id_set2), desc='writing user id'):
            file.write(str(user_id) + '\n')


if __name__ == '__main__':
    main()
