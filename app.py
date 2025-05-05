import pdfplumber
from flask import Flask, request
from openai import OpenAI
from pptx import Presentation

prompt_templates = {
    'Summary': "Please summarize the following text in 100 words:\n\n",
    'Flashcard': "Please create flashcards from the following text:\n\n",
    'Mindmap': "Please create a mindmap from the following text:\n\n"
}
app = Flask(__name__)
with open('./apikey.txt', 'r') as file:
    api_key = file.read().strip()

client = OpenAI(
    api_key=api_key
)
@app.route('/')
def home():
    return "Welcome to GPT-Bridge!"


@app.post('/chat')
def chat():  
    prompt = request.json.get("prompt")
    if not prompt:
        return {"error": "Prompt is required"}, 400
    try:

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        print(completion)
        print(completion.choices[0].message.content)
        return {"response": completion.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}, 500


def extract_text_from_ppt(ppt_file):
    prs = Presentation(ppt_file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text


# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text





# Function to summarize text using OpenAI's GPT model
def summarize_text(text, prompt='Summary'):
    # openai.api_key = api_key

    # OpenAI API call for summarization
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt_templates[prompt] + text}
        ],
    )

    return response.choices[0].message.content.strip()


# Main function to process the file and summarize
def process_file(file_path, file_type='pdf', prompt='Summary'):
    text = ""

    if file_type in ('pptx', 'ppt'):
        text = extract_text_from_ppt(file_path)
    elif file_type == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif file_type == 'txt':
        with open(file_path, 'r') as file:
            text = file.read()

    if not text:
        return "No text extracted from the file."

    summary = summarize_text(text, prompt)
    return summary


# Example usage

@app.post('/chat-with-attachment')
def chat_with_attachment():
    prompt = request.form.get("prompt")
    # prompt = "Summarize the file content"
    file = request.files.get("file")
    if not prompt:
        return {"error": "Prompt is required"}, 400
    if not file:
        return {"error": "File is required"}, 400

    try:
        # Save the uploaded file temporarily
        file_path = file.filename
        file.save(file_path)  # Replace with your PPT or PDF file path
        file_type = file_path[file_path.rfind('.') + 1:]
        summary = process_file(file_path, file_type, prompt)
        # Upload the file to OpenAI

        return {"response": summary}
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500


if __name__ == '__main__':
    # app.run()
    app.run(debug=True, port=9000)
