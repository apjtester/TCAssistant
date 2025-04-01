import os
import numpy as np
import requests
from bs4 import BeautifulSoup
import faiss
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from  langchain_ollama import ChatOllama, OllamaLLM
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import re

models=[
    'llama3.2:1b','gemma:2b','falcon3:1b','gemma:7b'
]

class RAGBot:
    persist_directory="faiss_index"
    
    model_name=models[1]
    system_prompt = (
             "You are a test case generator for MobiControl. "
             "You should create test cases to cover all scenarios, edge cases and error possibilities. All questions asked should be asked with respect to MobiControl."
             "\n\n"
            "MobiControl is an enterprise device management solution. It supports Android, Apple, Windows, ChromeOS and Linux devices. You can manage devices using profiles, policies, advanced configurations and device actions. You can monitor devices using reports, device dashboard and app dashboard."
            "Test case should be created for MobiControl and solely using the information provided. If sufficient information is not available, you can ask for more information."
            "\n\n"
            "Context: {context}"
        )
    vectorstore=None
    chain=None
    retriever=None
    doc_ids=[]

    # def checkURL(self,url):
    #     with shelve.open('db') as db:
    #         if not db.get("urls"):
    #             db["urls"]=[]
    #         if url in list(db['urls']):
    #             return True
    #         urls=db["urls"]
    #         urls.append(url)
    #         db["urls"]=urls
    #         db.sync()
    #         return False

    def __init__(self):
        print("Init Rag functions")
        self.getVStore()
        self.create_chain()
    
    def filter_content(self,main_content):
        formatted_text= re.sub(r'202(\d|.)+ Help', '', main_content)
        formatted_text= re.sub('\nSearch\n', ' ', formatted_text)
        formatted_text= re.sub(r'\n+', ' ', formatted_text)
        formatted_text= re.sub(r'\*+', ' ', formatted_text)
        formatted_text= re.sub(r'\t+', ' ', formatted_text)
        formatted_text= re.sub(r'  +', ' ', formatted_text)
        formatted_text= re.sub('!SPLIT!', '', formatted_text)
        formatted_text= re.sub('Jump to main content', '', formatted_text)
        formatted_text= re.sub('Welcome to SOTI MobiControl', '', formatted_text)
        return formatted_text
        
    def improve_text(self,text):
        OllamaLLM(model=self.model_name).invoke()
    def create_vstore(self):        
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if(not self.vectorstore):            
            faiss_index = faiss.IndexFlatIP(len(embeddings.embed_documents('XXX')[0]))  # Inner product for cosine similarity
            self.vectorstore=FAISS(index=faiss_index, embedding_function=embeddings, docstore=InMemoryDocstore(),index_to_docstore_id={})
        self.vectorstore.save_local(self.persist_directory) 

    def SplitText(self,text):
        htmltext = re.sub(r'<header.*?>.*?</header>', '', text, count=2, flags=re.DOTALL)
        htmltext = re.sub(r'<nav.*?>.*?</nav>', '', htmltext, flags=re.DOTALL)
        htmltext = re.sub(r'</section>', '!SPLIT!</section>', htmltext)
        htmltext = re.sub(r'</ul>', '!SPLIT!</ul>', htmltext)
        htmltext = re.sub(r'</ol>', '!SPLIT!</ol>', htmltext)
        htmltext = re.sub(r'</article>', '!SPLIT!</article>', htmltext)
        htmltext = re.sub(r'</table>', '!SPLIT!</table>', htmltext)
        htmltext = re.sub(r'</tr>', '!SPLIT!</tr>', htmltext)
        soup=BeautifulSoup(htmltext, 'html.parser')
        firstParagraph=self.filter_content(soup.text.split("!SPLIT!")[0])
        for script in soup(["script", "style"]):
            script.decompose()
        splitter= RecursiveCharacterTextSplitter(
            separators=["!SPLIT!"],
            chunk_size=4000,
        )
        docs=splitter.split_text(soup.text)
        for i in range(1,len(docs)):
            text=self.filter_content(docs[i])
            docs[i]=firstParagraph+"\n"+text
        return docs

    def add_text(self,htmlText,url):
        chunks = self.SplitText(htmlText)
        print(url)
        metadatas = [{"source": f"URL_{url} chunk_{i}"} for i in range(len(chunks))]
        self.vectorstore.add_texts(texts=chunks,metadatas=metadatas)
    
    def load_vstore(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text") 
        self.vectorstore = FAISS.load_local(
    self.persist_directory, embeddings, allow_dangerous_deserialization=True
)

    def getVStore(self):
        
        if os.path.isdir(self.persist_directory):
            self.load_vstore()
        else:
            self.create_vstore()
        
    def changeModel(self,model):
        if(model not in models):
            return False
        self.model_name=model
        self.chain=None
        self.create_chain()
        return True
        
    def findRelatedDocs(self,question):
        # query_vector = self.model.encode(question)
        # # Print the most similar documents

        # k = 5  # Number of nearest neighbors to retrieve
        # distances, indices = self.faiss_index.search(np.array([query_vector], dtype=np.float32), k)
        # print(distances ,'\n',indices)
        # for i, index in enumerate(indices[0]):
        #     distance = distances[0][i]
        #     print(f"Nearest neighbor {i+1}: {self.docChunks[index]}, Distance {distance}")
        # return [self.docChunks[i] for i in indices[0]]
        # question_paragraph=OllamaLLM(model=self.model_name).invoke("Create question)
        similardocs=self.vectorstore.similarity_search_with_score(question,k=5,fetch_k=20)
        docs=[]
        for doc in similardocs:
            docs.append(doc[0].page_content)
            print(doc,"\n\n")
        return [doc[0] for doc in similardocs]
        
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

    def answerQuestion(self,question):
        docs=self.findRelatedDocs(question)
        # print(docs)
        response=self.chain.invoke({"context":docs,"input":question})
        return response
    
    def fetch_all_links(self, url, visited=None,initial=True):
        if visited is None:
            visited = set()
        url=url.split("#")[0]
        if url in visited:
            return []
        
        visited.add(url)
        response = requests.get(url)
        if response.status_code != 200:
            return []
        self.add_text(response.text,url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if not link.startswith('http'):
                links.append(link)
                links.extend(self.fetch_all_links("https://www.soti.net/mc/help/v2025.0/en/"+link, visited,False))
        
        if(initial):
            self.vectorstore.save_local(self.persist_directory) 
        return links