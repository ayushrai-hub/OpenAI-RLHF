import os
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chains import LLMChain

# Loading environment variables from my .env file
load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")        # Set the API key for LangChain from the environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"                             # Enable LangChain tracing for monitoring and debugging
os.environ["LANGCHAIN_PROJECT"] = "Enhanced Q&A Chatbot With Ollama"    # Set the LangChain project name for organized tracing


def get_prompt_template():
    # Chat Prompt template with system and user messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are an information extractor assistant. Your task is to accurately extract and return specific types of information from a user's input. Specifically, you need to identify and extract:

                        1. **Color Names**: If the input text includes any color name, return it as a dictionary with the key "color" and the value being the identified color. If there is no color mentioned, return `None`.
                            - Example 1: Input - "The sky is blue." -> Return `{"color": "blue"}`
                            - Example 2: Input - "Color - red" -> Return `{"color": "red"}`
                            - Example 3: Input - "Hello Susovan" -> Return `None`

                        2. **Location Names**: If the input text includes a location name, return it as a dictionary with the key "location" and the value being the identified location. If there is no location mentioned, return `None`.
                            - Example 1: Input - "I live in New York." -> Return `{"location": "New York"}`
                            - Example 2: Input - "Location - USA" -> Return `{"location": "USA"}`
                            - Example 3: Input - "Watermelon is tasty." -> Return `None`

                        Ensure that you return only the relevant information based on the input text and nothing extra. Your output should be a dictionary with either or both keys ("color" and "location") or `None` for each case where the corresponding information is not found.
                                """),
            ("user", "{input}")
        ]
    )
    return prompt


# Response from LLM function
def generate_response(question, llm_model):
    """
    Generate a response from the LLM based on the user's question.

    Args:
        question (str): The user's question.
        llm_model (str): The name of the LLM model to use.

    Returns:
        str: The generated response from the LLM.
    """

    # Initialize the LLM with the specified model
    llm = OllamaLLM(model=llm_model)
    
    # Create the LLM chain
    chain = LLMChain(prompt=get_prompt_template(), llm=llm)
    
    # Invoke the chain with the user's question
    response = chain.run({'input': question})
    return response
