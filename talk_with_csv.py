from langchain_openai import OpenAI
# from langchain.agents import create_pandas_dataframe_agent
from langchain_experimental.agents import create_pandas_dataframe_agent
import language
import pandas as pd
from dotenv import load_dotenv
import json
import os
import streamlit as st
import sqlite3
#import altair as alt
#import seaborn as sns
from showallthedb import showallgraph
from streamlit_pandas_profiling import st_profile_report
from pydantic_settings import BaseSettings
from openai import OpenAI


# import sweetviz as sv
from ydata_profiling import ProfileReport

conn = sqlite3.connect('news_data.db')
cursor = conn.cursor()

st.set_page_config(page_title="👨‍💻 Talk with your CSV", layout='wide')
load_dotenv()

# Render the custom CSS styles
st.markdown("""
    <style>
    /* Add custom CSS styles here */
    body {
        margin: 0;
        padding: 0;
    }
    
    .full-width {
        width: 100%;
    }
    
    .stApp {
        padding-top: 0 !important;
    }
    
    .stTab {
        margin-top: 0 !important;
    }
    
    </style>
    """,
            unsafe_allow_html=True)

# D:\D2K\Talk2CSV\Mumbai.csv
def csv_tool(filename: str):
    FILE_PATH = os.path.join(os.getcwd(),filename)
    print("---", FILE_PATH, "---")
    df = pd.read_csv(FILE_PATH)
    # sweetviz(df)
    # pandas_profiling(df)
    return create_pandas_dataframe_agent(OpenAI(temperature=0),df,verbose=True)


def ask_agent(agent, query):
    """
    Query an agent and return the response as a string.

    Args:
        agent: The agent to query.
        query: The query to ask the agent.

    Returns:
        The response from the agent as a string.
    """
    # Prepare the prompt with query guidelines and formatting
    prompt = ("""
        Let's decode the way to respond to the queries. The responses depend on the type of information requested in the query. 

        1. If the query requires a table, format your answer like this:
           {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

        2. For a bar chart, respond like this:
           {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

        3. If a line chart is more appropriate, your reply should look like this:
           {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

        Note: We only accommodate two types of charts: "bar" and "line".

        4. For a plain question that doesn't need a chart or table, your response should be:
           {"answer": "Your answer goes here"}

        For example:
           {"answer": "The Product with the highest Orders is '15143Exfo'"}

        5. If the answer is not known or available, respond with:
           {"answer": "I do not know."}

        Return all output as a string. Remember to encase all strings in the "columns" list and data list in double quotes. 
        For example: {"columns": ["Products", "Orders"], "data": [["51993Masc", 191], ["49631Foun", 152]]}
        Note: for any graph, just consider first 50 rows
        Now, let's tackle the query step by step. Here's the query for you to work on: 
        """ + query)

    # Run the prompt through the agent and capture the response.
    response = agent.run(prompt)

    # Return the response converted to a string.
    return str(response)


def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    # print("+++>.>>",response)
    # response = response.replace('`', '"')
    # response = response.replace("'", '"')
    print(response)
    return json.loads(response)


def write_answer(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]
        try:
            df_data = {
                col:
                [x[i] if isinstance(x, list) else x for x in data['data']]
                for i, col in enumerate(data['columns'])
            }
            df = pd.DataFrame(df_data)
            print(df)
            #df.set_index("Products", inplace=True)
            # sns.set_palette("gray")
            st.bar_chart(df)
            #chart = alt.Chart(df).mark_bar(color='gray')
            #st.altair_chart(chart)

        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")


# Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        try:
            df_data = {
                col: [x[i] for x in data['data']]
                for i, col in enumerate(data['columns'])
            }
            df = pd.DataFrame(df_data)

            st.line_chart(df)
        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")

    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)


def save_to_database():
    query = st.session_state.get('query', '')
    answer = st.session_state.get('response', '')
    print(query)
    print(answer)
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS savedgraphs (query TEXT, answer TEXT)")
    cursor.execute("INSERT INTO savedgraphs (query, answer) VALUES (?, ?)",
                   (query, answer))
    conn.commit()


def fetch_historical_data():
    cursor.execute("SELECT query,answer FROM savedgraphs")
    return cursor.fetchall()

LANG = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu':'zulu',
    }

def welcome():
    lang = st.sidebar.selectbox(("Select Language"), ["en", "bn", "hi", "de", "ta", "te",'pa'])
    
    st.session_state.selected_language = lang
    talk=language.st_translate_text("Talk with your CSV",st.session_state.selected_language)
    app=language.st_translate_text("An application which lets you analyze your CSV",st.session_state.selected_language)
    how=language.st_translate_text("How it works",st.session_state.selected_language)
    upload=language.st_translate_text("Upload your CSV file and input a query for analysis.",st.session_state.selected_language)
    queryeg=language.st_translate_text("Query examples: draw a bar chart, show a line chart, provide a table, answer a question.",st.session_state.selected_language)
    ify=language.st_translate_text("If you want to store the result or add it to the dashboard, use the 'Add to Canvas' button.",st.session_state.selected_language)
    ok=language.st_translate_text("A dashboard is available to display the charts stored by the user.",st.session_state.selected_language)
    button_trans=language.st_translate_text("Take me to site",st.session_state.selected_language)
    st.title(talk)
    
    st.write(app)
    
    st.write(how)
    st.write(upload)
    
    st.write(queryeg)
    st.write(ify)
    
    st.write(ok)

    
    
    if st.button(button_trans):
        st.session_state['authentication_status'] = True

def interpret_data(df):
        client = OpenAI(api_key="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")


        prompt = (
            "Interpret the given data and provide me the 1. theme of the data , 2. purpose of the data 3. why is this data used and business insights on the data\n"
            f"{df.columns}\n{df.head()}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a powerful data interpreter. You can interpret the data and provide the description for the data. You have to provide me the theme of the data as in what the data means and what is thw purpose of the data along with data description I believe in you!"},
                    {"role": "user", "content": f"This is the data:\n{df.columns}\n{df.head()}"}
                    ]
        
            # prompt=prompt,
            # temperature=0.75,
            # max_tokens=4,
            # top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0.6,
            )
        
        response_message = response.choices[0].message.content
        print(response_message )
    
    # return all_choices_text.strip()
        return response_message

def login():
    
    lang = st.sidebar.selectbox(("Select Language"), ["en", "bn", "hi", "de", "ta", "te",'pa'])
    
    st.session_state.selected_language = lang
    talkto=language.st_translate_text("👨‍💻 Talk with your CSV",st.session_state.selected_language)
    dashboard=language.st_translate_text("🗃 Dashboard",st.session_state.selected_language)
    subheader=language.st_translate_text("👨‍💻 Talk with your CSV",st.session_state.selected_language)
    uploadcsv=language.st_translate_text("Please upload your CSV file below.",st.session_state.selected_language)
    uploadd=language.st_translate_text("Upload a CSV",st.session_state.selected_language)
    sendmessage=language.st_translate_text("Send a Message",st.session_state.selected_language)
    canva=language.st_translate_text("Add this to Canvas",st.session_state.selected_language)
    submitquery=language.st_translate_text("Submit Query",st.session_state.selected_language)

    # tab1, tab2 = st.tabs(["👨‍💻 Talk with CSV", "🗃 Dashboard"])

    # #st.title("👨‍💻 Talk with your CSV")
    # tab1.subheader("👨‍💻 Talk with your CSV")
    # #st.write("Please upload your CSV file below.")
    # tab1.write("Please upload your CSV file below")
    # uploaded_file = tab1.file_uploader("Upload a CSV",
    #                                    type="csv",
    #                                    accept_multiple_files=False,
    #                                    key="fileUploader")

    tab1, tab2 = st.tabs([talkto,dashboard])

    tab1.subheader(subheader)
    tab1.write(uploadcsv)
    data = tab1.file_uploader(uploadd,
                              type="csv",
                              accept_multiple_files=False,
                              key="fileUploader",
               )

    if data is not None:
        filename = data.name
        df = pd.read_csv(filename)
        if tab1.button("Generate stats data"):
            pandas_profiling(df)
        if st.button("Theme of the data"):        
            st.title("Data Interpretation and Purpose using Llama-2-70b-chat-hf Model")

            st.write("Data:")
            st.write(df.head())

            interpretation = interpret_data(df)
            st.write("Data Interpretation:")
            st.write(interpretation)
    

    query = tab1.text_area(sendmessage)

    if tab1.button(submitquery):
        # Create an agent from the CSV file.
        print("--> ", data.name)
        agent = csv_tool(data.name)

        # Query the agent.
        response = ask_agent(agent=agent, query=query)

        # Decode the response.
        decoded_response = decode_response(response)
        #decoded_response = {"bar": {"columns": ["Price"], "data": [20.04, 16.94, 15.77]}}

        # Write the response to the Streamlit app.
        write_answer((decoded_response))
        st.session_state['query'] = query
        st.session_state['response'] = str(decoded_response)
        if st.button("Exit",
                     args=(st.session_state.query, st.session_state.response)):
            print("Removed element")
            print("Removed element finally removed")

    if tab1.button("Add this to Canva"):
        save_to_database()

    with tab2:
        tab2.subheader("All the graphs")
        showallgraph()

# def sweetviz(df):
#     analyze_report = sv.analyze(df)
#     analyze_report.show_html('report.html', open_browser=True)

def pandas_profiling(df):
    # profile = ProfileReport(df, title="Statistical Report")
    # profile.to_file('statistical_report.html')
    st.title("Exploratory Data Analysis")
    profile_df = df.profile_report()
    st_profile_report(profile_df)

def main():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    if st.session_state['authentication_status']:
        login()
    else:
        welcome()


if __name__ == "__main__":
    main()
