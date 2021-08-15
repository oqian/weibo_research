from bs4 import BeautifulSoup
from requests import request
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

cookie = ""
# Default to use break point id list
user_id_list_path = "remaining_user_id_list.txt"


def read_user_id_list(path):
    with open(path, 'r') as file:
        return [line.strip('\n') for line in file]


@sleep_and_retry
@limits(calls=3, period=6)
def get_profile_response(user_id):
    return request(
        method='GET',
        url='https://weibo.cn/{}/info'.format(user_id),
        headers={
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Cookie": cookie,
        })


def parse_location(response):
    if response is None or response.status_code != 200:
        raise ConnectionError
    soup = BeautifulSoup(response.content, 'lxml')
    if 'User does not exists!' in soup.body.text:
        return None
    try:
        contents = soup.body.find_all('div', class_='c')[3].contents
    except IndexError:
        raise ConnectionError
    for content in contents:
        if '地区' in content:
            return content.strip('地区:')


def write_location(user_id, location):
    with open('locations.csv', 'a') as file:
        file.write("{},{}\n".format(user_id, location))


def save_remaining_ids(user_id_list):
    with open('remaining_user_id_list.txt', 'w') as file:
        file.writelines([uid + '\n' for uid in user_id_list])


def main():
    user_id_list = read_user_id_list(user_id_list_path)
    remaining_id_list = set(user_id_list)
    user_id_list_bar = tqdm(user_id_list, desc='Location crawled')
    for user_id in user_id_list_bar:
        response = get_profile_response(user_id)
        try:
            location = parse_location(response)
            if location is not None:
                user_id_list_bar.set_description("%10s - %-10s" % (user_id, location))
                write_location(user_id, location)
            remaining_id_list.remove(user_id)
            save_remaining_ids(remaining_id_list)
        except ConnectionError:
            user_id_list_bar.set_description("Connection error!")
            pass


if __name__ == '__main__':
    main()
