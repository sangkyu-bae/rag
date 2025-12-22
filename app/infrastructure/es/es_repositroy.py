from app.infrastructure.es.es_clinet_factory import EsClientFactory
from elasticsearch.helpers import bulk


class EsRepository:
    def __init__(self):
        self.client = EsClientFactory.get_client()

    def upsert(self, index:str ,id:str,req:dict[str,any]):
        self.client.index(
            index=index,
            id=id,
            document=req
        )

    def bulk_upsert(
            self,
            index: str,
            docs: list[dict[str, any]],
            id_field: str = "chunk_id"
    ):
        """
        docs 예시:
        [
          {
            "chunk_id": "loan_policy_15_2",
            "text": "...",
            "doc_id": "loan_policy",
            ...
          }
        ]
        """

        actions = []

        for doc in docs:
            actions.append({
                "_op_type": "index",
                "_index": index,
                "_id": doc[id_field],
                "_source": doc
            })

        bulk(self.client, actions)