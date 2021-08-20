import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm
from http.cookies import SimpleCookie
from requests.cookies import RequestsCookieJar

with open("cookie.txt", "r") as f:
    cookie_string = f.readline().strip('\n')

# Default to use break point id list
user_id_list_path = "remaining_user_id_list.txt"


def to_cookiejar(string):
    cookiejar = RequestsCookieJar()
    cookiejar.update(SimpleCookie(string))
    return cookiejar


def read_user_id_list(path):
    with open(path, 'r') as file:
        return [line.strip('\n') for line in file]


@sleep_and_retry
@limits(calls=3, period=6)
def get_profile_response(session: requests.Session, user_id):
    try:
        return session.get(url='https://weibo.cn/{}/info'.format(user_id))
    except:
        return None


def parse_location(response):
    """
    Parses response html into location of the user_id.
        Raises ConnectionError if the response is considered ill-formed.
    """
    if response is None or response.status_code != 200:
        raise ConnectionError
    soup = BeautifulSoup(response.content, 'lxml')
    if soup is None or soup.body is None or soup.body.text is None:
        raise ConnectionError
    if 'User does not exists!' in soup.body.text:
        return None
    try:
        contents = soup.body.find_all('div', class_='c')[3].contents
    except IndexError or AttributeError:
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


def create_https_session(cookie_jar):
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    }
    session.cookies = cookie_jar
    return session


def main():
    user_id_list = read_user_id_list(user_id_list_path)
    remaining_id_list = set(user_id_list)
    user_id_list_bar = tqdm(user_id_list, desc='Location crawled')
    cookie_jar = to_cookiejar(cookie_string)
    session = create_https_session(cookie_jar)
    for user_id in user_id_list_bar:
        response = get_profile_response(session, user_id)
        try:
            location = parse_location(response)
            if location is not None:
                user_id_list_bar.set_description("%10s - %-10s" % (user_id, location))
                write_location(user_id, location)
            remaining_id_list.remove(user_id)
            save_remaining_ids(remaining_id_list)
        except ConnectionError:
            user_id_list_bar.set_description("Connection error!")


if __name__ == '__main__':
    main()
