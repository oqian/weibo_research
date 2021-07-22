#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import random
import sys
import traceback
import requests
from time import sleep
from lxml import etree
from tqdm import tqdm
from typing import Dict, Set, Tuple, List

# Type alias for readability
UserId = str
CrawlDepth = int


def random_sleep():
    if random.random() < 0.4:
        sleep(random.randint(3, 5))
    else:
        sleep(random.randint(1, 2))


def write_to_txt(follow_list):
    with open('user_id_list.txt', 'ab') as f:
        for user in follow_list:
            f.write((user['uri'] + ' ' + user['nickname'] + '\n').encode(
                sys.stdout.encoding))


class WeiboUserCrawler:
    def __init__(self, cookie: str, crawl_queue: List[Tuple[UserId, CrawlDepth]], max_depth: CrawlDepth = 0,
                 visited_user_id_set: Set[UserId] = None):
        self.cookie = cookie
        self.crawl_queue = crawl_queue
        self.visited_user_id_set = visited_user_id_set if visited_user_id_set else set()
        self.max_depth = max_depth

    @classmethod
    def init_from_config(cls, config: Dict, max_depth=0):
        user_id_depth_queue = [(user_id, 0) for user_id in config["user_id_list"]]
        return WeiboUserCrawler(cookie=config["cookie"], crawl_queue=user_id_depth_queue,
                                max_depth=max_depth)

    def query_webpage(self, url):
        """处理html"""
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
            headers = {'User_Agent': user_agent, 'Cookie': self.cookie}
            html = requests.get(url, headers=headers).content
            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def crawl_page_count(self, user_id: UserId):
        """获取关注列表页数"""
        url = "https://weibo.cn/%s/fans" % user_id
        selector = self.query_webpage(url)
        if selector.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(
                selector.xpath("//input[@name='mp']")[0].attrib['value'])
        return page_num

    def crawl_users_from_follower_page(self, user_id: UserId, page: int):
        """获取第page页的user_id"""
        url = 'https://weibo.cn/%s/fans?page=%d' % (user_id, page)
        selector = self.query_webpage(url)
        table_list = selector.xpath('//table')
        if page == 1 and len(table_list) == 0:
            print(u'cookie无效或提供的user_id无效')
        else:
            for t in table_list:
                im = t.xpath('.//a/@href')[-1]
                uri = im.split('uid=')[-1].split('&')[0].split('/')[-1]
                nickname = t.xpath('.//a/text()')[0]
                yield {'uri': uri, 'nickname': nickname}

    def get_page_list_for_user(self, user_id):
        """获取关注用户主页地址"""
        page_count = self.crawl_page_count(user_id)
        return [page for page in range(1, page_count + 1)]

    def get_expected_user_count_left(self, max_depth):
        """Returns expected number of users left to crawl, assuming that an average user has 200 follower. """
        return sum(map(lambda x: round((1 - 200 ** (max_depth - x[1] + 1)) / (1 - 200)), self.crawl_queue))

    def start(self):
        """运行爬虫"""
        print(u"预计获取user_id个数: %d" % self.get_expected_user_count_left(self.max_depth + 1))
        expected_user_count_to_crawl = self.get_expected_user_count_left(self.max_depth)
        time_bar = tqdm(total=expected_user_count_to_crawl, desc=u"（预计）用户爬取数", unit=u"人")
        while len(self.crawl_queue) > 0:
            user_id, depth = self.crawl_queue.pop()
            user_list_to_write = []
            for page in tqdm(self.get_page_list_for_user(user_id), desc="页数"):
                random_sleep()
                for follower_info in self.crawl_users_from_follower_page(user_id, page):
                    follower_user_id = follower_info["uri"]
                    if follower_user_id not in self.visited_user_id_set:
                        if depth < self.max_depth:
                            self.crawl_queue.insert(0, (follower_user_id, depth + 1))
                        user_list_to_write.append(follower_info)
                        self.visited_user_id_set.add(follower_user_id)
            time_bar.update(expected_user_count_to_crawl - self.get_expected_user_count_left(self.max_depth))
            write_to_txt(user_list_to_write)
        print(u'信息抓取完毕')


class ConfigFileReader:

    def __init__(self, config_path=None):
        self.config_path = config_path if config_path else os.path.split(
            os.path.realpath(__file__))[0] + os.sep + 'config.json'

    def read(self) -> Dict:
        if not os.path.isfile(self.config_path):
            sys.exit(u'当前路径：%s 不存在配置文件config.json' %
                     (os.path.split(os.path.realpath(__file__))[0] + os.sep))
        """打开文件"""
        with open(self.config_path) as f:
            try:
                config = json.loads(f.read())
            except ValueError:
                sys.exit(u'config.json 格式不正确，请参考 '
                         u'https://github.com/dataabc/weiboSpider#3程序设置')
        """验证配置是否正确"""
        user_id_list = config['user_id_list']
        if (not isinstance(user_id_list,
                           list)) and (not user_id_list.endswith('.txt')):
            sys.exit(u'user_id_list值应为list类型或txt文件路径')
        if not isinstance(user_id_list, list):
            if not os.path.isabs(user_id_list):
                user_id_list = os.path.split(
                    os.path.realpath(__file__))[0] + os.sep + user_id_list
            if not os.path.isfile(user_id_list):
                sys.exit(u'不存在%s文件' % user_id_list)
        """If user_id_list is file path, read that file"""
        if not isinstance(user_id_list, list):
            if not os.path.isabs(user_id_list):
                user_id_list = os.path.split(
                    os.path.realpath(__file__))[0] + os.sep + user_id_list
            config['user_id_list'] = self.get_user_list(user_id_list)

        return config

    def get_user_list(self, file_name):
        """获取文件中的微博id信息"""
        with open(file_name, 'rb') as f:
            try:
                lines = f.read().splitlines()
                lines = [line.decode('utf-8-sig') for line in lines]
            except UnicodeDecodeError:
                sys.exit(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序' % file_name)
            user_id_list = []
            for line in lines:
                info = line.split(' ')
                if len(info) > 0 and info[0].isdigit():
                    user_id = info[0]
                    if user_id not in user_id_list:
                        user_id_list.append(user_id)
        return user_id_list


def main():
    config = ConfigFileReader().read()
    wb = WeiboUserCrawler.init_from_config(config, max_depth=1)
    wb.start()  # 爬取微博信息


if __name__ == '__main__':
    main()
