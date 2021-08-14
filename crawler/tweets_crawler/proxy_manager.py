import json
import random
import threading

import requests
from requests.adapters import HTTPAdapter


class ProxyManager:
    """Helper class for making network requests with proxies. """
    __config = None

    def __init__(self, filename="proxy.json", request_max_retry=3, switch_ip_every_n_req=100):
        self.filename = filename
        self.request_max_retry = request_max_retry
        self.switch_ip_every_n_req = switch_ip_every_n_req
        self.__lock = threading.Lock()
        self.__current_session = self.__get_new_session()
        self.__switch_ip_counter = 0

    def __read_proxies(self):
        with open(self.filename, "r") as file:
            config = json.loads(file.read())
            assert config['username']
            assert config['password']
            assert config['port']
            return config

    def __get_new_session(self):
        s = requests.Session()
        s.mount("https://m.weibo.cn", HTTPAdapter(max_retries=self.request_max_retry))
        # s.proxies = self.__get_new_proxies()
        return s

    def __get_new_proxies(self):
        if not ProxyManager.__config:
            ProxyManager.__config = self.__read_proxies()
        username = ProxyManager.__config['username']
        password = ProxyManager.__config['password']
        port = ProxyManager.__config['port']
        session_id = random.random()
        super_proxy_url = ('http://%s-country-cn-session-%s:%s@zproxy.lum-superproxy.io:%d' %
                           (username, session_id, password, port))
        return {
            'http': super_proxy_url,
            'https': super_proxy_url,
        }

    def __pick_session(self):
        with self.__lock:
            if self.__switch_ip_counter >= self.switch_ip_every_n_req:
                self.__switch_ip_counter = 0
                self.__current_session = self.__get_new_session()
            else:
                self.__switch_ip_counter += 1
        return self.__current_session

    def request(self, url, params=None, headers=None):
        session = self.__pick_session()
        return session.get(url, params=params, headers=headers)
