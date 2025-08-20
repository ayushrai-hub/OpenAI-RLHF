# ideal_completion.py
#import _snowflake
import json
import streamlit as st
import time
#from snowflake.snowpark.context import get_active_session


DATABASE = "DATAANALYTICS"
SCHEMA = "PUBLIC"
STAGE = "DATA_REVIEWER"
FILE = "DataAnalysis_ReviewHOL.yaml"
import warnings
warnings.filterwarnings("ignore")
def transmit_prompt(query: str) -> dict:
    """Invokes the REST API and retrieves the output."""
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }
    resp = _snowflake.send_snow_api_request(
        "POST",
        f"/api/v2/data/reviewer/message",
        {},
        {},
        request_body,
        {},
        30000,
    )
    if resp["status"] < 400:
        return json.loads(resp["content"])
    else:
        raise Exception(
            f"Failed request with status {resp['status']}: {resp}"
        )

def handle_prompt(query: str) -> None:
    """Handles a prompt and appends the reply to the dialogue."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": query}]}
    )
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Compiling response..."):
            response = transmit_prompt(query=query)
            content = response["message"]["content"]
            show_content(content=content)
    st.session_state.messages.append({"role": "assistant", "content": content})

def show_content(content: list, message_index: int = None) -> None:
    """Demonstrates a content aspect for a dialogue."""
    message_index = message_index or len(st.session_state.messages)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Executing SQL..."):
                    session = get_active_session()
                    df = session.sql(item["statement"]).to_pandas()
                    if len(df.index) > 1:
                        data_tab, line_tab, bar_tab = st.tabs(
                            ["Data", "Line Chart", "Bar Chart"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                        with line_tab:
                            st.line_chart(df)
                        with bar_tab:
                            st.bar_chart(df)
                    else:
                        st.dataframe(df)

def reset_chat():
    """Resets the application to its initial state."""
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None
    st.rerun()  # Force rerun after resetting 

st.title("❄️ Snowflake Data Reviewer ❄️")
st.markdown(f"Semantic Model: `{FILE}`")

# Details about inquiry types and samples
st.markdown("""
### Pose Inquiries Regarding Your Dataset
You can make queries such as:
- Daily or monthly recaps
- Particular metrics for a specified period
- Data aggregated by classifications

**Sample Inquiries:**
1. What's the total income for the past month?
2. How many items were distributed last quarter?
3. What's the average score of products with over 10 feedbacks?

Your turn now. Pose your inquiry below!
""")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None

# Display previous messages
for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        show_content(content=message["content"], message_index=message_index)

# Input for user inquiry
if user_input := st.chat_input("What inquiry do you have?"):
    handle_prompt(query=user_input)

# Process active suggestion if available
if st.session_state.active_suggestion:
    handle_prompt(query=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None

# Reset chat button
if st.button("Reset Chat"):
     # Capture stdout and stderr
    captured_output = StringIO()

    # Redirect stdout and stderr to capture warnings and output
    with contextlib.redirect_stdout(captured_output):
        reset_chat()
