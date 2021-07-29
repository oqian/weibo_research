import random
import json


class ProxyConfigReader:
    """Helper class for reading config file for proxies. """
    __config = None

    def __init__(self, filename="proxy.json"):
        self.filename = filename

    def __read_proxies(self):
        with open(self.filename, "r") as file:
            config = json.loads(file.read())
            assert config['username']
            assert config['password']
            assert config['port']
            return config

    def get_proxies(self):
        if not ProxyConfigReader.__config:
            ProxyConfigReader.__config = self.__read_proxies()
        username = ProxyConfigReader.__config['username']
        password = ProxyConfigReader.__config['password']
        port = ProxyConfigReader.__config['port']
        session_id = random.random()
        super_proxy_url = ('http://%s-country-cn-session-%s:%s@zproxy.lum-superproxy.io:%d' %
                           (username, session_id, password, port))
        return {
            'http': super_proxy_url,
            'https': super_proxy_url,
        }
