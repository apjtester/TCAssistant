from datetime import datetime
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
    'llama3.2:1b','gemma:2b','falcon3:1b','gemma:7b','gemma3:12b','gemma3:1b','gemma3:4b'
]

class RAGBot:    
    model_name=models[5]
    ragLogPath="ragLogs.log"
    system_prompt = (
             "You are a test case creator for MobiControl. "
             "You should create test cases with detailed steps to cover all scenarios for the Acceptance Criteria provided by user."
             "You should also mention possible edge cases and error possibilities."
             "\n\n"
            # "MobiControl is an enterprise device management solution. It supports Android, Apple, Windows, ChromeOS and Linux devices. You can manage devices using profiles, policies, advanced configurations and device actions. You can monitor devices using reports, device dashboard and app dashboard."
            "Test case should be created only using the information provided below. Mention 'Not enough content to answer' if required information is not provided or the question is not related to MobiControl."
            "\n\n"
            "Context: {context}"
            "Acceptance Criteria will be provided by the user and you should create test cases based on that. Only test cases should be returned."
        )
    # system_prompt=(
    #     "You are a highly experienced software test engineer specializing in mobile device management (MDM) solutions. Your task is to generate comprehensive test cases for SOTI MobiControl, a leading MDM platform."
    #     "You will be provided with a description of a specific software functionality and an acceptance criteria. Your primary objective is to produce a test case that thoroughly validate the happy-path of the functionality, and after that, mention various negative scenarios, edge cases, and boundary conditions."
    #     "Critically, you must ensure test cases directly address and validate the provided acceptance criteria. If the provided context is insufficient to confidently generate test cases (e.g., missing crucial information about system dependencies or integration points), you *must* explicitly state this in your output, outlining the missing information required."
    #     "Do not make assumptions or invent functionality; flag gaps in the provided context.\n\n"
    #     "Here's the format you *must* follow for the happy path test case:\n\n**Test Case Name:** [A concise and descriptive name for the test case]\n\n**Steps:** [A numbered list of detailed steps to execute the test. Each step must be clear, concise, and unambiguous. Include expected results after *each* step.  This is absolutely critical – the language model should envision itself guiding a less experienced tester through the process.]\n\n\n"
    #     "Now, when I provide you with the functionality description and acceptance criteria, generate test cases following this format, prioritizing thoroughness and adherence to the provided information. If information is missing or ambiguous, clearly state the required clarification. Do not invent test cases; identify and flag the gaps."
    #     "Your output should *only* be the text case and scenarios itself. Do *not* include any introductory or concluding remarks."
    #     "\n\nContext: {context}"  
    # )
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
                ("user", "Created Test cases for the following: \"{input}\""),
            ]
        )
        print("MODELL:",self.model_name)
        self.chain = create_stuff_documents_chain(llm, qa_prompt)

        # st.session_state.chain = create_retrieval_chain(history_aware_retriever, qa_chain)
    
    def timeText(self,text):
        return f"{datetime.now()}: {text}"
    def FetchShortDocs(self,docs):
        shortDocs=""
        for doc in docs:
            shortDocs+=doc[0:20]
        return shortDocs
    


    def answerQuestion(self,question):
        docs,sourceUrls=self.vstoreConnection.findRelatedDocs(question)
        with open('ragLogs.logs', 'a') as f:
            f.write(self.timeText("Fetched Docs. ")+'\n')
        for doc in docs:
            print(f"DOC FETCHED  :  {doc}\n\n") 
        # response=self.chain.stream({"context":docs,"input":question})
        return sourceUrls,self.chain.stream({"context":docs,"input":question})
            # print(chunk, end="|", flush=True)
        # return ""#response
    