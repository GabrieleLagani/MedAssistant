import os
import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, UnstructuredXMLLoader, CSVLoader
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_toolkits import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool, ToolException
import sqlite3

from .prompt import prompt_template
from config import *


def load_data(data_path):
    loader = DirectoryLoader(data_path, glob="*/*.xml", show_progress=True, loader_cls=UnstructuredXMLLoader)
    data = loader.load()
    return data

def text_split(data, chunk_size=500, chunk_overlap=20):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    text_chunks = splitter.split_documents(data)
    return text_chunks

def load_hf_embeddings():
    os.environ['HF_HOME'] = os.path.join(ASSETS_FOLDER, '.hf_cache')
    return HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

def parse_results(result):
    return result['messages'], result['messages'][-1].content

def initialize_llm(user_name, host, k=2, max_tokens=512, temp=0.1):
    # Load embeddings
    print("Loading embeddings...")
    embeddings = load_hf_embeddings()
    
    # Load index
    print("Loading index...")
    docsearch = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = docsearch.as_retriever(search_kwargs={"k": k})
    retriever_tool = create_retriever_tool(retriever, name="search_medical_information", description="Use to look up additional medical context and information to answer the question.")
    tools = [retriever_tool]
    
    # Load LLM
    print("Loading LLM...")
    llm = ChatOllama(model="llama3.1", temperature=temp, max_tokens=max_tokens)
    
    # Load DB
    db = SQLDatabase.from_uri("sqlite:///" + DB_PATH)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    #tools += toolkit.get_tools()
    
    # Create additional tools
    search_doctor_by_specialization_tool = StructuredTool.from_function(func=search_doctor_by_specialization, name="search_doctor_by_specialization", description="Use to look up a list of doctor with a desired specialization.", handle_tool_error=True)
    search_available_doctor_appointments_tool = StructuredTool.from_function(func=search_available_doctor_appointments, name="search_available_doctor_appointments", description="Use to look up a list of available time slots for appointments with a given doctor.", handle_tool_error=True)
    search_patient_appointments_tool = StructuredTool.from_function(func=search_patient_appointments, name="search_patient_appointments", description="Use to look up the list of appointments currently scheduled by the patient", handle_tool_error=True)
    register_emergency_tool = StructuredTool.from_function(func=register_emergency, name="register_emergency", description="Use to register a medical emergency manifested by a patient with a corresponding color-code.", handle_tool_error=True)
    tools += [retriever_tool, search_doctor_by_specialization_tool, search_available_doctor_appointments_tool, search_patient_appointments_tool, register_emergency_tool]
    
    # Create agent
    print("Loading agent...")
    prompt = SystemMessage(content=prompt_template.format(user_name=user_name, table_names=db.get_usable_table_names(), host=host))
    agent = create_react_agent(llm, tools, messages_modifier=prompt, debug=True)
    
    print("Done!")
    
    return agent

def search_doctor_by_specialization(specialization: str) -> list[str]:
    """
    Look up doctor with a given specialization field.
    
    :param specialization: The name of the specialization area, e.g. Cardiology.
    :return: A list of doctors with the given specialization area.
    """
    
    # Open connection to DB
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    
    # Prepare query to retrieve doctor information
    query = """
                SELECT name
                FROM doctors
                WHERE LOWER(specialization) LIKE LOWER(?)
            """
    
    # Execute query and fetch result
    result = cur.execute(query, ('%' + specialization + '%',))
    return list((r[0] for r in result.fetchall()))

def search_available_doctor_appointments(doctor: str) -> list[dict]:
    """
    Look up available time slots for appointments with a given doctor.

    :param doctor: The name of the doctor.
    :return: A list of time slots for appointments with the corresponding doctor and reservation link.
    """
    
    # Open connection to DB
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    
    # Prepare query to retrieve time slot information
    query = """
                SELECT id, time_slot, doctor
                FROM appointments
                WHERE patient is null and LOWER(doctor) LIKE LOWER(?)
            """
    
    # Execute query and fetch result
    result = cur.execute(query, ('%' + doctor + '%',))
    return list(({'time_slot': r[1], 'doctor': r[2], 'reservation_link': '<a href="res?id={}" target="_blank"> link </a>'.format(r[0])} for r in result.fetchall()))

def search_patient_appointments(patient: str, doctor: str = None) -> list[dict]:
    """
    Look up scheduled appointments of a patient with a given doctor.

    :param patient: The name of the patient.
    :param doctor: The name of the doctor. If null returns the patient appointments with all doctors.
    :return: A list of time slots of scheduled appointments with the corresponding doctor and reservation link.
    :raises ToolException: if the user is trying to access information of another patient.
    """
    
    # Check that user is authorized to access patient information
    if patient.lower() != USER_NAME.lower():
        raise ToolException("Current user is {}. This user is not allowed to access patient {}'s information. This information is confidential and cannot be disclosed. Answer the user's question by notifying this issue.".format(USER_NAME, patient))
    
    # Open connection to DB
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    
    if doctor is not None and doctor != '':
        # Prepare query to retrieve time slot information
        query = """
                    SELECT id, time_slot, doctor
                    FROM appointments
                    WHERE LOWER(patient) LIKE LOWER(?) and LOWER(doctor) LIKE LOWER(?)
                """
    
        # Execute query and fetch result
        result = cur.execute(query, ('%' + patient + '%', '%' + doctor + '%',))
    else:
        # Prepare query to retrieve time slot information
        query = """
                    SELECT id, time_slot, doctor
                    FROM appointments
                    WHERE LOWER(patient) LIKE LOWER(?)
                """
        # Execute query and fetch result
        result = cur.execute(query, ('%' + patient + '%',))
    
    return list(({'time_slot': r[1],'doctor': r[2],  'reservation_link': '<a href="res?id={}" target="_blank"> link </a>'.format(r[0])} for r in result.fetchall()))

def register_emergency(patient: str, question: str, code: str) -> str:
    """
        Register a medical emergency reported by the user.

        :param patient: The name of the patient.
        :param question: The question provided by the patient, describing the symptoms of the medical emergency.
        :param code: Color-code assigned to the emergency, which can be one of "RED", "YELLOW", or "GREEN", based on the level of emergency: color-code "RED" denotes the maximum level of emergency, to be used when the user's life is in immediate danger; color-code "YELLOW" denotes a moderate level of emergency, to be used when the user needs medical assistance, but is not facing an immediate risk of death; color-code "GREEN" denotes a low level of emergency, to be used when the user is not facing particular risks and can receive medical assistance without urgency
        :return: A success message of the operation.
    """
    
    # Get current datetime in string format
    t = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    # Open connection to DB
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    
    # Prepare and execute query to create emergency table if it does not exist already.
    query = """
                CREATE TABLE IF NOT EXISTS emergencies(user, patient, time, question, code)
            """
    cur.execute(query)
    
    # Prepare query to register emergency
    query = """
                INSERT INTO emergencies VALUES (?, ?, ?, ?, ?)
            """
    
    # Execute query and fetch result
    cur.execute(query, (USER_NAME, patient, t, question, code))
    db.commit()
    
    return "The emergency has been registered. Do not answer the user's question by returning the emergency color-code, because that information is reserved for doctors; instead, return general health tips related to the condition described by the user, reassure the user that the emergency can be handled by medical intervention, and advise consulting a healthcare professional."

