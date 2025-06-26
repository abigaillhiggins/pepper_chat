from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Store received data in memory
received_emotions = []

@app.route('/emotion', methods=['POST'])
def emotion_endpoint():
    data = request.json
    print(f"Received: {data}")
    received_emotions.append(data)
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def index():
    # Simple HTML template to display the received emotions
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emotion Posts</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; }
            h1 { color: #333; }
            .emotion { margin-bottom: 1em; padding: 1em; border: 1px solid #ccc; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Received Emotion Posts</h1>
        {% for item in emotions %}
            <div class="emotion">
                <strong>Sentence:</strong> {{ item['sentence'] }}<br>
                <strong>Emotion:</strong> {{ item['emotion'] }}
            </div>
        {% else %}
            <p>No emotion posts received yet.</p>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, emotions=received_emotions)

if __name__ == "__main__":
    print("Starting emotion tag server on http://localhost:5000 ...")
    app.run(port=5000)