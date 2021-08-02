import threading

from tqdm import tqdm


class ConcurrentUserConfigList:
    """
    Helper class for managing list that supports asynchronously getting next user config.
    """

    def __init__(self, user_id_list):
        self.__user_id_list = user_id_list
        self.__lock = threading.Lock()
        self.__iterator = iter(user_id_list)
        self.__progress_bar = tqdm(desc="用户数", unit="人", total=len(self))
        self.__progress_bar.display()

    def __next__(self):
        with self.__lock:
            out = next(self.__iterator)
            self.__progress_bar.update()
            return out

    def __iter__(self):
        """Each iterator will only point to self. This ensures each thread is iterating on the same iterator. """
        return self

    def __len__(self):
        return len(self.__user_id_list)
