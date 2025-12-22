from functools import lru_cache
from elasticsearch import Elasticsearch

class EsClientFactory:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_client():
        return Elasticsearch(
                "http://localhost:9200",
                basic_auth=("elastic", "password")
            )