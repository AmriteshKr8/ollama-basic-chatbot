from flask import Flask, render_template, request, session, jsonify
from ollama import chat

app = Flask(__name__)
app.secret_key = "supersecretkey"
MAX_MESSAGES = 20

@app.route("/")
def home():
    session.clear()
    session["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]
    return render_template("chat.html", messages=session["messages"])

@app.route("/send", methods=["POST"])
def send():
    prompt = request.json.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    messages = session.get("messages")
    messages.append({"role": "user", "content": prompt})

    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-MAX_MESSAGES:]

    try:
        response = chat(model="gemma3:4b", messages=messages, stream=True)
        bot_reply = ""
        for chunk in response:
            bot_reply += chunk["message"]["content"]
    except Exception as e:
        bot_reply = "Error: " + str(e)

    messages.append({"role": "assistant", "content": bot_reply})
    session["messages"] = messages

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
