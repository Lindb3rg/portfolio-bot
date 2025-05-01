
import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import numpy as np
from utils.logger import logger

"""
vector_db module                                                                                                        
                                                                                                                           
This module defines the VectorDB class for loading markdown documents                                                      
from specified folders, splitting them into chunks, creating a FAISS vector                                                
store using OpenAI embeddings, and extracting vectors and metadata.                                                        
                                                                                                                           
Usage:                                                                                                                     
    db = VectorDB()                                                                                                        
    db.folders = ['path/to/dir1', 'path/to/dir2']                                                                          
    db.prepare_documents()                                                                                                 
    db.create_vector_store()                                                                                               
    vectors = db.vectors                                                                                                   
                                                                                                                        
Dependencies:                                                                                                              
    - langchain                                                                                                            
    - langchain_openai                                                                                                     
    - langchain_core                                                                                                       
    - numpy
    - FAISS
"""



class VectorStore:
    def __init__(self, folders):
        self.folders = folders
        self.documents = []
        self.vectors = []
        self.vector_store = None
        self.text_loader_kwargs = {'encoding': 'utf-8'}
        self.chunks = []
        self.embeddings = OpenAIEmbeddings()
        self.color_map = {'portfolio':'blue', 'portfolio-projects':'green', 'technical-skills':'red'}
        self.doc_types = []
        self.colors = []
        

        
    def prepare_documents(self):
        
        if not self.folders:
            raise ValueError("No folders specified: please set VectorStore.folders to a list of directory paths")
                                  
        for folder in self.folders:                                                                                                       
            if not os.path.isdir(folder):                                                                                                 
                raise ValueError(f"Folder path '{folder}' does not exist or is not a directory")                                          
                                                                                                                                        
        documents_from_folders = []
        
        for folder in self.folders:
            doc_type = os.path.basename(folder)
            try:
                loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=self.text_loader_kwargs)
                folder_docs = loader.load()
            except Exception as e:
                raise RuntimeError(f"Error loading documents from '{folder}': {e}") from e
            
            for doc in folder_docs:
                doc.metadata["doc_type"] = doc_type
                documents_from_folders.append(doc)
                
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.chunks = text_splitter.split_documents(documents_from_folders)
    

    def create_vector_store(self):
        if not self.chunks:
            raise ValueError("No chunks available: please call prepare_documents() before create_vector_store()")
            
        self.documents = []
        self.vectors = []
        self.doc_types = []
        self.colors = []
        
        try:
            self.vector_store = FAISS.from_documents(self.chunks, embeddings=self.embeddings)
        
        except TypeError:
            self.vector_store = FAISS.from_documents(self.chunks, embedding=self.embeddings)
        
        except Exception as e:
            raise RuntimeError(f"Error creating FAISS vector store: {e}") from e
        
        total_vectors = self.vector_store.index.ntotal
        dimensions = self.vector_store.index.d

        logger.info(f"There are {total_vectors} vectors with {dimensions:,} dimensions in the vector store")
        
        for i in range(total_vectors):
            try:
                vec = self.vector_store.index.reconstruct(i)
            except Exception as e:
                raise RuntimeError(f"Error reconstructing vector at index {i}: {e}") from e
            self.vectors.append(vec)
            
            doc_id = self.vector_store.index_to_docstore_id[i]
            
            document = self.vector_store.docstore.search(doc_id)
            if document is None or not hasattr(document, 'page_content'):
                raise RuntimeError(f"Document not found in docstore for id {doc_id}")
            self.documents.append(document.page_content)
            
            doc_type = document.metadata.get('doc_type')
            if not doc_type:                                                    
                raise KeyError(f"Missing 'doc_type' metadata for document id {doc_id}")
            self.doc_types.append(doc_type)
            
            color = self.color_map.get(doc_type, 'black')
            if doc_type not in self.color_map:
                logger.warning(f"No color mapping for doc_type '{doc_type}', using default 'black'")
            self.colors.append(color)
            
        self.vectors = np.array(self.vectors)
        
