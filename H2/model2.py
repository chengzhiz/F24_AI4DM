from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import TextLoader #load the document
from langchain_text_splitters import RecursiveCharacterTextSplitter #for creating chunks from the loaded document
from langchain_openai import OpenAIEmbeddings #for converting chunks into embeddings
from langchain_chroma import Chroma #database for stroring the embeddings

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

from dotenv import load_dotenv
load_dotenv()

import os
dir = os.getcwd()
db_dir = os.path.join(dir,"chroma_db")
print(db_dir)

#Read the text content from the .txt file and load it as langchain document
loader = TextLoader('boolean_questions.txt')
document = loader.load()

#Split the document into chunks using text splitters 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(document)

#create embeddings using openAI embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
#store the embeddings and chunks into Chroma DB
Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_dir)

#setting up the DB for retrieval
embeddings_used = OpenAIEmbeddings(model="text-embedding-3-small")
vectorDB = Chroma(persist_directory=db_dir,embedding_function=embeddings_used)

#setting up Retriver
retriever = vectorDB.as_retriever(search_type="similarity", search_kwargs={"k": 3})

def getRetriever(dir):
    """
    dir is the directory of the vector DB
    """
    embeddings_used = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorDB = Chroma(persist_directory=dir,embedding_function=embeddings_used)
    retriever = vectorDB.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return retriever

headers = {"Authorization": "Bearer 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"}


from huggingface_hub import InferenceClient

def textGeneration_langChain_RAG(user_type, retrieverDir, api_key):
    """
    user_type: The type of user (e.g., children, adults, etc.).
    retrieverDir: Directory of the vector DB with relevant boolean questions.
    api_key: Your Hugging Face API key for authentication.
    """

    # Initialize the Inference Client
    client = InferenceClient(api_key=api_key)

    # Retrieve relevant boolean questions from Chroma DB using user_type
    retriever = getRetriever(retrieverDir)
    
    # Modify the query to include user_type in the context
    query = f"Get some boolean questions for a {user_type}."
    retrieved_docs = retriever.get_relevant_documents(query)
    
    # Extract content from retrieved documents
    context = "\n".join(doc.page_content for doc in retrieved_docs)

    # Create a clear and direct system prompt for generating a boolean question
    system_prompt = (
        "Based on the following context, generate one complete boolean question that a {user_type} would ask:\n"
        "{context}\n\n"
        "Make sure it's only one grammatically correct question and can be answered with yes/no."
    )

    # Prepare the final prompt to send to the Hugging Face API
    final_prompt = system_prompt.format(user_type=user_type, context=context)

    # Prepare the messages for the chat API
    messages = [
        {"role": "user", "content": final_prompt}
    ]

    # Stream the response from the Hugging Face Inference Client
    stream = client.chat.completions.create(
        model="HuggingFaceTB/SmolLM2-1.7B-Instruct", 
        messages=messages, 
        max_tokens=500,
        stream=True
    )

    # Collect and print the output from the stream
    full_response = ""
    for chunk in stream:
        full_response += chunk.choices[0].delta.content

    return full_response.strip()  # Return the final response witho
