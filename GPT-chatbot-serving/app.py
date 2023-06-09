from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import tensorflow_hub as hub
import json
import os
from apikey import api_key

# Import langchain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

# Import OpenAI API KEY
os.environ['OPENAI_API_KEY'] = api_key

app = Flask(__name__)
CORS(app)  # Aktifkan CORS pada aplikasi Flask

# Langchain
answer_template = PromptTemplate(
    input_variables= ['question'],
    template= 'Jawab pertanyaan ini "{question}" dengan jelas.'
)

sources_template = PromptTemplate(
    input_variables= ['answer'],
    template= 'Berikan satu atau beberapa link yang berhubungan dengan ini: "{answer}".'
)

# Memory
answer_memory = ConversationBufferMemory(input_key='question', memory_key= 'chat_history')
sources_memory = ConversationBufferMemory(input_key='answer', memory_key= 'chat_history')

# LLMs
llm = OpenAI(temperature=0.9)
answer_chain = LLMChain(llm=llm, prompt=answer_template, verbose=True, output_key='answer', memory=answer_memory)
sources_chain = LLMChain(llm=llm, prompt=sources_template, verbose=True, output_key='sources', memory=sources_memory)

# Load the results from JSON
with open('results.json', 'r') as f:
    results = json.load(f)

# Load the Universal Sentence Encoder module
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
embed = hub.load(module_url)

@app.route('/')
def index():
    return "API is running."

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    question = data['question']

    # GPT Answers
    answer = answer_chain.run(question)
    sources = sources_chain.run(answer=answer)

    # Embed the input question
    embedded_question = embed([question])

    # Calculate cosine similarity scores
    cos_scores = []
    for module in results.keys():
        embedded_answer = embed([module])
        similarity_score = tf.reduce_sum(tf.multiply(
            embedded_question, embedded_answer), axis=1).numpy()[0]
        cos_scores.append(similarity_score)

    # Sort the scores in descending order
    sorted_indices = sorted(range(len(cos_scores)),
                            key=lambda k: cos_scores[k], reverse=True)

    # Get the top 3 modules, titles, and links
    top_modules = []
    top_titles = []
    link_diskusi = []

    for index in sorted_indices[:3]:
        module = list(results.keys())[index]
        title = results[module]['discussion_title']
        link = results[module]['link_diskusi']
        top_modules.append(module)
        top_titles.append(title)
        link_diskusi.append(link)

    # Combine the top modules, titles, and links into one paragraph with separators
    combined_paragraph = ""
    for i in range(len(top_modules)):
        combined_paragraph += f"<p>Module: {top_modules[i]}</p><p>Title: {top_titles[i]}</p><p><a href='{link_diskusi[i]}'>{link_diskusi[i]}</a><br></p>"
        if i < len(top_modules) - 1:
            combined_paragraph += "<br>"

    response = {
        'gpt_answer': answer,
        'gpt_sources': sources,
        'combined_paragraph': combined_paragraph
    }

    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000)
