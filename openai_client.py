import openai
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI, APIError, RateLimitError, Timeout
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type
from constants import *
from models import *
from models_sql import UserProfile
import json
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import SQLChatMessageHistory
from database import *


OPENAI_EMBEDDINGS_API_KEY = "sk-L7kqR1aerMHLYMrkKTgYNw"
OPENAI_API_KEY = "sk-e33XdbP5qVj57ONqvLnrpw"
OPENAI_BASE_URL = "https://aiportalapi.stu-platform.live/jpe"


import os
os.environ["PINECONE_API_KEY"] = "pcsk_2anjVo_RLgiFMaWs1NoqiueLPmqCoMBjVKNotYLBS6z9rh4oQJ7bZXDi1iFWYCYSXQ3Lz1"
pc = Pinecone()

index_name = "nutrition-index"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small",
                              base_url=OPENAI_BASE_URL,
                              api_key=OPENAI_EMBEDDINGS_API_KEY)

if index_name not in pc.list_indexes().names():
    print(f"Creating index '{index_name}' ...")
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    # Load documents and populate index ----
    loader = PyPDFLoader("data/meal_data.pdf")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(docs)

    vectorstore = PineconeVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        index_name=index_name
    )
    # Wait until index is ready
    while not pc.describe_index(index_name).status["ready"]:
        print("Waiting for index to be ready...")
        time.sleep(3)

vectorstore = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

loader = PyPDFLoader("data/meal_data.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)
print(split_docs)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(
    model="gpt-4o-mini",
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

def chat_with_open_ai(user_id: str, user_input: str):
    """
    Stateful chat with memory (SQL), retrieval context, and clean stored history.
    """

    # 1️⃣ Set up chat history and memory
    history = SQLChatMessageHistory(
        connection_string=DATABASE_URL,
        session_id=user_id
    )

    memory = ConversationBufferMemory(
        chat_memory=history,
        return_messages=True
    )

    # 3️⃣ (Optional) Retrieve external context — for example from Pinecone
    context = get_context(user_input)
    context_note = f"Relevant context:\n{context}\n\n" if context else ""

    # 4️⃣ Create the conversation chain (uses memory internally)
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    # 5️⃣ Generate response
    #    We prepend the context, but only the clean user_input will be saved in memory
    ai_response = conversation.predict(input=f"{context_note}{user_input}")

    return ai_response

# ---- Helper: optional context from vectorstore ----
def get_context(user_input: str):
    results = retriever.vectorstore.similarity_search_with_score(user_input, k=3)
    good_results = [doc for doc, score in results if score < 0.4]

    if not good_results:
        return ""

    context_text = "\n".join([doc.page_content for doc in good_results])
    return f"#thamkhao Một số thông tin tham khảo (không liên quan đến tình trạng/thông tin của user): \n{context_text}\n\n #thamkhao"

client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-e33XdbP5qVj57ONqvLnrpw"
)


def analyze_health(health_data: dict) -> dict:
    # response = client.chat.completions.parse(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": system_content_analyst},
    #         {"role": "user", "content": f"Đây là dữ liệu người dùng: {health_data}"},
    #     ],
    #     response_format=HealthAnalysis,
    #     temperature=0.2
    # )
    return health_data


def create_meal(user_profile: UserProfile, user_options: dict) -> dict:
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_MEAL_PLAN},
            {"role": "user",
             "content": f"Đây là dữ liệu người dùng: {user_profile.model_dump_json()}, options: {user_options}"},
        ],
        temperature=0.6,
        response_format=MealPlanData
    )
    return json.loads(response.choices[0].message.content)


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError, Timeout, ConnectionError)),
    wait=wait_random_exponential(multiplier=1, max=20),
    stop=stop_after_attempt(3),
    reraise=True
)
def summary_user_chat():
    """
    Tóm tắt các câu hỏi của user trong đoạn hội thoại, gom nhóm theo chủ đề.
    Trả về danh sách JSON gồm các phần tử: {"summary_sentence": ..., "source_index": ...}
    """

    # Lọc ra các câu hỏi của user
    user_questions = [
        {"index": i, "content": msg["content"]}
        for i, msg in enumerate(history)
        if msg["role"] == "user"
    ]

    # Tạo prompt yêu cầu tóm tắt
    prompt = (
        "Hãy tóm tắt ngắn gọn các câu hỏi của người dùng trong đoạn hội thoại.\n"
        "Nếu nhiều câu hỏi cùng chủ đề, hãy gộp thành 1-2 câu summary.\n"
        "Mỗi summary phải gắn source_index tới câu hỏi gốc gần nghĩa nhất.\n"
        "Mỗi summary phải giống như đang trả lời trực tiếp trong hội thoại, "
        "không dùng 'người dùng hỏi' hay 'trợ lý trả lời'.\n"
        "Chỉ tóm tắt câu hỏi của user, không tóm tắt câu trả lời của assistant.\n"
        "Trả lời dưới dạng JSON list với các trường: summary_sentence, source_index.\n\n"
        f"Các câu hỏi của user:\n{user_questions}\n"
        "Chỉ trả lời về JSON, không giải thích thêm."
    )

    # Gọi OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Trích xuất và chuyển đổi JSON
    content = response['choices'][0]['message']['content']
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ Lỗi định dạng JSON từ phản hồi.")
        return []
