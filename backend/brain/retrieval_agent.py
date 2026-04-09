class RetrievalAgent:

    def retrieve(self, memory, question):

        results = memory.search(question)

        docs = results.get("documents", [])
        metas = results.get("metadatas", [])

        if not docs or len(docs[0]) == 0:
            return None, None

        contexts = docs[0]
        metadata = metas[0]

        combined_context = "\n\n".join(contexts)

        return combined_context, metadata