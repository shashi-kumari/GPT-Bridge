from flask import Flask,request
from openai import OpenAI

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

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
