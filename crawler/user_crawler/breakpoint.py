# Type alias for readability
import sqlite3
from typing import List, Tuple, Set

UserId = str
CrawlDepth = int


class BreakpointDatabaseOperator:
    """
    Helper class that manages breakpoint caching and recovery
    """

    __connection = None

    def __init__(self, path: str = "crawl_todo_list.db"):
        self.path = path

    def add_user_id_to_crawl(self, user_id: UserId, depth: CrawlDepth):
        con = self.__get_connection()
        try:
            con.execute('''
                INSERT INTO crawl_list (user_id, crawl_depth)
                VALUES (?, ?)
            ''', (user_id, depth))
        except sqlite3.IntegrityError:
            # Integrity error is caused by conflicting user_id, so ignore it.
            return
        con.commit()

    def add_visited_user_id(self, user_id):
        con = self.__get_connection()
        try:
            con.execute('''
                INSERT INTO visited_list (user_id)
                VALUES (?)
            ''', (user_id,))
        except sqlite3.IntegrityError:
            # Integrity error is caused by conflicting user_id, so ignore it.
            return
        con.commit()

    def remove_user_id_to_crawl(self, user_id:str):
        con = self.__get_connection()
        con.execute('''
            DELETE FROM crawl_list
            WHERE user_id=?
        ''', (user_id,))
        con.commit()
        pass

    def get_crawl_list(self) -> List[Tuple[UserId, CrawlDepth]]:
        con = self.__get_connection()
        return [(user_id, crawl_depth) for user_id, crawl_depth in con.execute('''
            SELECT user_id, crawl_depth
            FROM crawl_list
        ''')]

    def get_visited_list(self) -> Set[UserId]:
        con = self.__get_connection()
        return {user_id for user_id in con.execute('''
            SELECT user_id FROM visited_list
        ''')}

    def __get_connection(self):
        if not BreakpointDatabaseOperator.__connection:
            BreakpointDatabaseOperator.__connection = sqlite3.connect(self.path)
            BreakpointDatabaseOperator.__connection.execute('''
                CREATE TABLE IF NOT EXISTS crawl_list (
                  user_id VARCHAR PRIMARY KEY,
                  crawl_depth INT NOT NULL DEFAULT 0
                )
            ''')
            BreakpointDatabaseOperator.__connection.execute('''
                CREATE TABLE IF NOT EXISTS visited_list (
                    user_id VARCHAR PRIMARY KEY
                )
            ''')
        return BreakpointDatabaseOperator.__connection
