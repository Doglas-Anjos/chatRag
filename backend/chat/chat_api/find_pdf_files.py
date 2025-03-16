import pathlib
import fitz
from typing import *
import fitz
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


def find_pdf_file_by_folder(folder_pdfs: str) -> List[str]:
    folder_list = list([str(path_) for path_ in pathlib.Path(f'{folder_pdfs}').glob('*.pdf')])
    return folder_list


def convert_to_text_pdf_file(path_pdf_file: str) -> str:
    doc = fitz.open(path_pdf_file)
    result_text = "\n".join([page.get_text() for page in doc])
    return result_text


def generate_list_texts_pdfs_files(folder_pdfs) -> List[str]:
    list_folder_pdf = find_pdf_file_by_folder(folder_pdfs)
    text_list_files = list()
    for file_pdf in list_folder_pdf:
        text_list_files.append(convert_to_text_pdf_file(file_pdf))

    return text_list_files


def convert_text_to_vec_db(folder_pdf_files: str):
    list_of_text = generate_list_texts_pdfs_files(folder_pdf_files)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents(list_of_text)

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("./././faiss_index")
