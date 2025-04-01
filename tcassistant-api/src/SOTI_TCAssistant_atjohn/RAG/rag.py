import datetime
import os
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup
import faiss
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from  langchain_ollama import ChatOllama, OllamaLLM
# from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import re

from .sql_connection import SQLConnection
from .vector_store import VectorStoreConnection

models=[
    'llama3.2:1b','gemma:2b','falcon3:1b','gemma:7b'
]

class RAGBot:    
    model_name=models[1]
    ragLogPath="ragLogs.log"
    system_prompt = (
             "You are a test case generator for MobiControl. "
             "You should create test cases to cover all scenarios, edge cases and error possibilities."
             "\n\n"
            "MobiControl is an enterprise device management solution. It supports Android, Apple, Windows, ChromeOS and Linux devices. You can manage devices using profiles, policies, advanced configurations and device actions. You can monitor devices using reports, device dashboard and app dashboard."
            "Test case should be created only using the information provided below. Mention if required information is not provided."
            "\n\n"
            "Context: {context}"
        )
    vstoreConnection=None
    # chunkStorage=None
    sqlConnection=None
    chain=None

    def __init__(self):
        self.vstoreConnection=VectorStoreConnection()
        self.create_chain()
    def changeModel(self,model):
        if(model not in models):
            return False
        self.model_name=model
        self.chain=None
        self.create_chain()
        return True
       
    def create_chain(self):
        llm=ChatOllama(model=self.model_name)
        # condense_question_system_template = (
        #     "Given a chat history and the latest user question "
        #     "which might reference context in the chat history, "
        #     "formulate a standalone question which can be understood "
        #     "without the chat history. Do NOT answer the question, "
        #     "just reformulate it if needed and otherwise return it as is."
        # )

        # condense_question_prompt = ChatPromptTemplate.from_messages(
        #     [
        #          ("system", condense_question_system_template),
        #         ("placeholder", "{chat_history}"),
        #         ("human", "{input}"),
        #     ]
        # )
        # history_aware_retriever = create_history_aware_retriever(
        #     llm, docsearch.as_retriever(search_type="similarity"), condense_question_prompt
        # )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                 ("system", self.system_prompt),
                # ("placeholder", "{chat_history}"),
                ("user", "{input}"),
            ]
        )
        self.chain = create_stuff_documents_chain(llm, qa_prompt)

        # st.session_state.chain = create_retrieval_chain(history_aware_retriever, qa_chain)
    
    def timeText(self,text):
        return datetime.now() +': '+ text
    def FetchShortDocs(self,docs):
        shortDocs=""
        for doc in docs:
            shortDocs+=doc[0:20]
        return shortDocs

    def answerQuestion(self,question):
        docs=self.vstoreConnection.findRelatedDocs(question)
        
        with open('ragLogs.logs', 'a') as f:
            f.write(self.timeText("Fetched Docs. ")+'\n')
        # for doc in docs:
        #     print(f"DOC1:{doc}\n\n") 
        response=self.chain.invoke({"context":docs,"input":question})
        return response
    