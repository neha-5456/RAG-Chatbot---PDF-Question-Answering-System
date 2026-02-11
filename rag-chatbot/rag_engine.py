import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context from PDF documents.

Rules:
- Only answer based on the provided context
- If the answer is not in the context, say "I couldn't find this information in the uploaded documents."
- Be concise but thorough
- Mention which part of the document your answer comes from when possible

Context from documents:
{context}
"""

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


class RAGEngine:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.vectorstore = None
        self.retriever = None
        self.chat_history = []

    def load_pdfs(self, pdf_paths):
        all_documents = []
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            for doc in documents:
                doc.metadata["source_file"] = os.path.basename(pdf_path)
            all_documents.extend(documents)

        if not all_documents:
            return {"status": "error", "message": "No content found in PDFs"}

        chunks = self.text_splitter.split_documents(all_documents)

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="pdf_collection",
        )

        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )

        return {
            "status": "success",
            "total_pages": len(all_documents),
            "total_chunks": len(chunks),
        }

    def ask(self, question):
        if not self.retriever:
            return {"answer": "Pehle koi PDF upload karo!", "sources": []}

        retrieved_docs = self.retriever.invoke(question)
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

        messages = QA_PROMPT.invoke({
            "context": context,
            "chat_history": self.chat_history[-10:],
            "question": question,
        })

        response = self.llm.invoke(messages)
        answer = response.content

        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        sources = []
        for doc in retrieved_docs:
            sources.append({
                "content": doc.page_content[:200] + "...",
                "page": doc.metadata.get("page", "N/A"),
                "file": doc.metadata.get("source_file", "Unknown"),
            })

        return {"answer": answer, "sources": sources}

    def reset(self):
        self.chat_history = []
        if self.vectorstore:
            self.vectorstore.delete_collection()
        self.vectorstore = None
        self.retriever = None


if __name__ == "__main__":
    print("RAG Engine Test Starting...")
    engine = RAGEngine()
    test_pdf = "data/sample.pdf"
    if os.path.exists(test_pdf):
        result = engine.load_pdfs([test_pdf])
        print(f"PDF Loaded: {result}")
        answer = engine.ask("What is this document about?")
        print(f"Answer: {answer['answer']}")
        print(f"Sources: {len(answer['sources'])} chunks used")
    else:
        print(f"Test PDF not found at: {test_pdf}")
        print("Put a sample PDF in the data/ folder and try again.")