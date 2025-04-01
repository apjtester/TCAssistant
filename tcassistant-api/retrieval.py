import os
import uuid
import pdb
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup,Tag
import faiss
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import HTMLSectionSplitter,CharacterTextSplitter,HTMLSemanticPreservingSplitter,HTMLHeaderTextSplitter,SentenceTransformersTokenTextSplitter,TokenTextSplitter,RecursiveCharacterTextSplitter
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
from tokenizers import Tokenizer
from langchain.storage import InMemoryByteStore

from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_community.storage import SQLStore
from sql_connection import SQLConnection

models=[
    'llama3.2:1b','gemma:2b','falcon3:1b','gemma:7b'
]

class ChunkStorage:
    id_key = "doc_id"
    def __init__(self):
        self.sqlStore = SQLStore(namespace="TCAssistant", db_url="sqlite://:memory:")

    
    def get_text(self, doc_id):       
        texts=self.sqlStore.mget([(doc_id)])
        return texts

class RAGBot:
    persist_directory="faiss_index"
    
    model_name=models[1]
    system_prompt = (
             "You are a test case generator for MobiControl. "
             "You should create test cases to cover all scenarios, edge cases and error possibilities."
             "\n\n"
            "MobiControl is an enterprise device management solution. It supports Android, Apple, Windows, ChromeOS and Linux devices. You can manage devices using profiles, policies, advanced configurations and device actions. You can monitor devices using reports, device dashboard and app dashboard."
            "Test case should be created using the information provided below."
            "\n\n"
            "Context: {context}"
        )
    vectorstore=None
    # chunkStorage=None
    sqlConnection=None
    chain=None
    count=0
    doc_ids=[]

    def __init__(self):
        print("Init Rag functions")
        self.getVStore()
        self.create_chain()
        self.sqlConnection=SQLConnection()

    def filter_content(self,main_content):
        formatted_text = main_content
        # formatted_text= re.sub(r'202(.){3} Help', '', formatted_text)
        formatted_text= re.sub('\nSearch\n', ' ', formatted_text)
        formatted_text= re.sub(r'\n+', ' ', formatted_text)
        formatted_text= re.sub(r'\*+', ' ', formatted_text)
        formatted_text= re.sub(r'\t+', ' ', formatted_text)
        formatted_text= re.sub(r'  +', ' ', formatted_text)
        formatted_text= re.sub('!SPLIT!', '', formatted_text)
        formatted_text= re.sub('Jump to main content', '', formatted_text)
        formatted_text= re.sub('Welcome to SOTI MobiControl', '', formatted_text)
        return formatted_text
        
    # def improve_text(self,text):
    #     OllamaLLM(model=self.model_name).invoke()
    def create_vstore(self):        
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if(not self.vectorstore):            
            faiss_index = faiss.IndexFlatIP(len(embeddings.embed_documents('XXX')[0]))  # Inner product for cosine similarity
            self.vectorstore=FAISS(index=faiss_index, embedding_function=embeddings, docstore=InMemoryDocstore(),index_to_docstore_id={})
        self.vectorstore.save_local(self.persist_directory) 
        # The storage layer for the parent documents
        # self.chunkStorage = ChunkStorage()

        # id_key = "doc_id"
        # # The retriever
        # self.retriever = MultiVectorRetriever(
        #     vectorstore=self.vectorstore,
        #     byte_store=self.chunkStorage.sqlStore,
        #     id_key=id_key,
        # )

    def add_text(self,text,url):
        # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        # chunks = text_splitter.split_text(text)
        tl=self.count_tokens(text)
        # print(len(text),text)
        doc_id=self.sqlConnection.addText(text)
        # self.doc_ids.append(doc_id)
        summary=OllamaLLM(model=self.model_name).invoke("Summarize the following text in 2 or 3 lines and print only the sumarized text. Summarized text should mention all topics covered. \""+text+"\"")  
        # print("ORIGINAL SUMMARY",summary)
        summary= re.sub(r'^(Sure,([a-zA-Z]|[0-9]| |\')+:( |\n)*)+','', summary)
        # summary=summary.removeprefix("\n\n")
        print("URL: ",url,", Adding:",summary)
        self.vectorstore.add_texts(texts=[summary],metadatas=[{"source": f"URL_{url}", "doc_id": doc_id}])
    
    def count_tokens(self,text):
        tokenizer = Tokenizer.from_pretrained("tiiuae/Falcon3-1B-Base")
        return len(tokenizer.encode(text))
    def load_vstore(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text") 
        self.vectorstore = FAISS.load_local(
    self.persist_directory, embeddings, allow_dangerous_deserialization=True
)
        # self.chunkStorage = ChunkStorage()
        
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
        # Print the most similar documents

        k = 5  # Number of nearest neighbors to retrieve
        # distances, indices = self.faiss_index.search(np.array([query_vector], dtype=np.float32), k)
        # print(distances ,'\n',indices)
        # for i, index in enumerate(indices[0]):
        #     distance = distances[0][i]
        #     print(f"Nearest neighbor {i+1}: {self.docChunks[index]}, Distance {distance}")
        # return [self.docChunks[i] for i in indices[0]]
        similardocs=self.vectorstore.similarity_search_with_score(question,k=5,fetch_k=20)
        for doc in similardocs:
            print(doc[1]) 
        docs=[]
        for doc in similardocs:
            docs.append(Document(page_content=self.sqlConnection.getText(doc[0].metadata["doc_id"]),metadata=doc[0].metadata))
        return docs
        
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
        print("\n\nDocs Fetched\n")
        for doc in docs:
            print(f"DOC1:{doc}\n\n") 
        response=self.chain.invoke({"context":docs,"input":question})
        return response
    
    def fetch_all_links323(self, url, visited=None,initial=True):
        # print("Fetching",url)
        if visited is None:
            visited = set()
        url=url.split("#")[0]
        if url in visited:
            return []
        
        visited.add(url)
        response = requests.get(url)
        if response.status_code != 200:
            return []
        
        # links = []
        htmltext= response.text
        headers_to_split_on = [
            ("h1", "Header 1"),
            ("h2", "Header 2")
        ]
        # def code_handler(element: Tag) -> str:
        #     data_lang = element.get("data-lang")
        #     code_format = f"<code:{data_lang}>{element.get_text()}</code>"

        #     return code_format
        splitter=HTMLSectionSplitter(
        separators=[". "],
        headers_to_split_on=headers_to_split_on,
        max_chunk_size=5000,
        xslt_path="transform.xml"
        )
        # print(htmltext)

        htmltext=splitter.convert_possible_tags_to_header(htmltext)
        # documents = splitter.split_text(htmltext)
        # for doc in documents:
        #     print(doc.page_content)
        #     print(doc.metadata)
        #     self.add_text(doc.page_content,url)
        docs=splitter.split_html_by_headers(htmltext)

        headers_to_split_on = [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
            ("h3", "Header 3")
        ]

        # html_splitter = HTMLHeaderTextSplitter(headers_to_split_on)

        # # for local file use html_splitter.split_text_from_file(<path_to_file>)
        # html_header_splits = html_splitter.split_text(htmltext)
        # for doc in html_header_splits:
        #     # print(doc.page_content)
        #     print(doc.metadata)
        #     text=self.filter_content(doc.page_content)
        #     self.add_text(text,url)
        # chunk_size = 384
        # chunk_overlap = 30

        # text_splitter2=RecursiveCharacterTextSplitter(separators=["</tr>"],keep_separator=True,chunk_size=5000,chunk_overlap=0)

        # # Split
        # splits = text_splitter2.split_text(htmltext)
        
        for doc in docs:
            # print(doc.page_content)
            # soup = BeautifulSoup(doc, 'html.parser')
            text=self.filter_content(doc["content"])
            print(text)
            self.add_text(doc["content"],url)




        # for a_tag in soup.find_all('a', href=True):
        #     link = a_tag['href']
        #     if not link.startswith('http'):
        #         links.append(link)
        #         # links.extend(self.fetch_all_links("https://www.soti.net/mc/help/v2025.0/en/"+link, visited,False))
        # for header in soup.find_all(["header", "nav", "script", "style"]):
        #     header.decompose()
        
        # main_content = soup.text
        # # text=self.filter_content(main_content)
        # # print(main_content)
        # # self.add_text(text,url)
        # # if(initial):
        # #     self.vectorstore.save_local(self.persist_directory) 
        # return links
    def fetch_all_links(self, url, visited=None,initial=True):
        if visited is None:
            visited = set()
        url=url.split("#")[0]
        if url in visited or self.count>10:
            return []
        self.count+=1
        
        visited.add(url)
        response = requests.get(url)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        htmltext= response.text
        
        htmltext = re.sub(r'<header.*?>.*?</header>', ' ', htmltext, count=2, flags=re.DOTALL)
        htmltext = re.sub(r'<nav.*?>.*?</nav>', ' ', htmltext, flags=re.DOTALL)
        htmltext = re.sub(r'</section>', '!SPLIT!</section>', htmltext)
        htmltext = re.sub(r'</ul>', '!SPLIT!</ul>', htmltext)
        htmltext = re.sub(r'</ol>', '!SPLIT!</ol>', htmltext)
        htmltext = re.sub(r'</article>', '!SPLIT!</article>', htmltext)
        htmltext = re.sub(r'</table>', '!SPLIT!</table>', htmltext)
        htmltext = re.sub(r'</tr>', '!SPLIT!</tr>', htmltext)
        soup=BeautifulSoup(htmltext, 'html.parser')
        firstParagraph=self.filter_content(soup.text.split("!SPLIT!")[0])
        for script in soup(["script", "style","header","nav"]):
            script.decompose()
        
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if not link.startswith('http'):
                links.append(link)
                links.extend(self.fetch_all_links("https://www.soti.net/mc/help/v2025.0/en/"+link, visited,False))
        splitter= RecursiveCharacterTextSplitter(
            separators=["!SPLIT!"],
            chunk_size=4000,
        )
        docs=splitter.split_text(soup.text)
        # print(htmltext)
        for i in range(len(docs)):
            # print(doc.page_content)
            
            text=self.filter_content(docs[i])
            if(i>0):
                text=firstParagraph+"\n"+text
            self.add_text(text,url)
        
        # if(initial):
        #     self.vectorstore.save_local(self.persist_directory) 
        return links
    # def fetch_all_links2(self, url, visited=None,initial=True):
    #     # print("Fetching",url)
    #     if visited is None:
    #         visited = set()
    #     url=url.split("#")[0]
    #     if url in visited or self.count>10:
    #         return []
    #     self.count+=1
    #     visited.add(url)
    #     response = requests.get(url)
    #     if response.status_code != 200:
    #         return []
        
    #     # links = []
    #     htmltext= response.text
        
    #     htmltext = re.sub(r'<header.*?>.*?</header>', ' ', htmltext, count=2, flags=re.DOTALL)
    #     htmltext = re.sub(r'<nav.*?>.*?</nav>', ' ', htmltext, flags=re.DOTALL)
    #     htmltext = re.sub(r'</section>', '!SPLIT!</section>', htmltext)
    #     htmltext = re.sub(r'</ul>', '!SPLIT!</ul>', htmltext)
    #     htmltext = re.sub(r'</ol>', '!SPLIT!</ol>', htmltext)
    #     htmltext = re.sub(r'</article>', '!SPLIT!</article>', htmltext)
    #     htmltext = re.sub(r'</table>', '!SPLIT!</table>', htmltext)
    #     htmltext = re.sub(r'</tr>', '!SPLIT!</tr>', htmltext)
    #     soup=BeautifulSoup(htmltext, 'html.parser')
    #     firstParagraph=self.filter_content(soup.text.split("!SPLIT!")[0])
    #     for script in soup(["script", "style","header","nav"]):
    #         script.decompose()
    #     splitter= RecursiveCharacterTextSplitter(
    #         separators=["!SPLIT!"],
    #         chunk_size=4000,
    #     )
    #     docs=splitter.split_text(soup.text)
    #     # print(htmltext)
    #     for i in range(len(docs)):
    #         # print(doc.page_content)
            
    #         text=self.filter_content(docs[i])
    #         if(i>0):
    #             text=firstParagraph+"\n"+text
    #         self.add_text(text,url)
r=RAGBot()
# r.fetch_all_links("https://www.soti.net/mc/help/v2025.0/en/scriptcmds/reference/androidplus_classic.html")
# r.fetch_all_links2("https://www.soti.net/mc/help/v2025.0/en/console/users/internal_usermanagement.html")
# r.fetch_all_links2("https://www.soti.net/mc/help/v2025.0/en/console/applications/viewing_installed_apps.html")
# r.fetch_all_links2("https://www.soti.net/mc/help/v2025.0/en/setup/installing/system_requirements.html")
r.fetch_all_links("https://www.soti.net/mc/help/v2025.0/en/start.html")
ans=r.answerQuestion("Create a test case for the following acceptance criteria: User should be able to do al troubleshoot methods for upgrade failure.")
print(ans)
# print("Max length",r.maxlength)
# print("Avg length",r.sum/r.count)
# print("Total count",r.count)