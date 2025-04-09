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

rootPathList="https://www.soti.net/mc/help/v2025.1/en".split("/")

class VectorStoreConnection:
    persist_directory="faiss_index"
    urlDirectoryPath="urlList.txt"
    vectorstore=None
    sqlConnection=None
    count=0
    doc_ids=[]
    finalUrlCount=1366

    def __init__(self):
        self.getVStore()
        self.sqlConnection=SQLConnection()

    def filter_content(self,main_content):
        formatted_text = main_content
        formatted_text= re.sub('\nSearch\n', ' ', formatted_text)
        formatted_text= re.sub(r'\n+', ' ', formatted_text)
        formatted_text= re.sub(r'\*+', ' ', formatted_text)
        formatted_text= re.sub(r'\t+', ' ', formatted_text)
        formatted_text= re.sub(r'  +', ' ', formatted_text)
        formatted_text= re.sub('!SPLIT!', '', formatted_text)
        formatted_text= re.sub('Jump to main content', '', formatted_text)
        formatted_text= re.sub('Welcome to SOTI MobiControl', '', formatted_text)
        return formatted_text
        
    def create_vstore(self):        
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if(not self.vectorstore):            
            faiss_index = faiss.IndexFlatIP(len(embeddings.embed_documents('XXX')[0]))  # Inner product for cosine similarity
            self.vectorstore=FAISS(index=faiss_index, embedding_function=embeddings, docstore=InMemoryDocstore(),index_to_docstore_id={})
        self.vectorstore.save_local(self.persist_directory) 
        
    def add_text(self,text,url):
        doc_id=self.sqlConnection.addText(text)
        summary=OllamaLLM(model="gemma:2b").invoke("Summarize the following text in 2 or 3 lines and print only the sumarized text. Summarized text should mention all topics covered. \""+text+"\"")  
        summary= re.sub(r'^(Sure,([a-zA-Z]|[0-9]| |\')+:( |\n)*)+','', summary)
        print("URL: ",url,", Adding:",summary)
        self.vectorstore.add_texts(texts=[summary],metadatas=[{"source": url, "doc_id": doc_id}])
    
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
        
    def findRelatedDocs(self,question):
        k = 5  # Number of nearest neighbors to retrieve
        # distances, indices = self.faiss_index.search(np.array([query_vector], dtype=np.float32), k)
        # print(distances ,'\n',indices)
        # for i, index in enumerate(indices[0]):
        #     distance = distances[0][i]
        #     print(f"Nearest neighbor {i+1}: {self.docChunks[index]}, Distance {distance}")
        # return [self.docChunks[i] for i in indices[0]]
        similardocs=self.vectorstore.similarity_search_with_score(question,k=k)
        sourceUrls=[]
        docs=[]
        for doc in similardocs:
            sourceUrls.append(doc[0].metadata["source"])
            docs.append(Document(page_content=self.sqlConnection.getText(doc[0].metadata["doc_id"]),metadata=doc[0].metadata))
        return docs, sourceUrls

    def fetch_all_links(self, url, visited=None,initial=True,path=rootPathList):
        if visited is None:
            visited = set()
        url=url.split("#")[0]
        if url in visited:
            return []
        if initial:
            file = open(self.urlDirectoryPath, "w") # For deleting existing contents
            file.close()
        with open(self.urlDirectoryPath, 'a') as f:
            f.write(url+'\n')
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
            if not link.startswith(('http','mailto:','#')):
                currentPathList=path
                while link.startswith('../'):
                    currentPathList=currentPathList[:-1]
                    link=link[3:]
                finalUrl="/".join(currentPathList)+'/'+ link
                currentPathList=finalUrl.split("/")[:-1]
                links.append(finalUrl)
                links.extend(self.fetch_all_links(finalUrl, visited,False,currentPathList))
        splitter= RecursiveCharacterTextSplitter(
            separators=["!SPLIT!"],
            chunk_size=4000,
        )
        docs=splitter.split_text(soup.text)
        for i in range(len(docs)):
            text=self.filter_content(docs[i])
            if(i>0):
                text=firstParagraph+"\n"+text
            self.add_text(text,url)
        
        self.count+=1
        print(f"\n{self.count}/{self.finalUrlCount} URLs processed\n")
        if(initial):
            self.count=0
            self.vectorstore.save_local(self.persist_directory) 
        return links