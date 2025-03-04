from flask import request, jsonify, render_template
from . import api_blueprint 
from services.assistant_manager import AssistantManager  

assistant = AssistantManager()  

@api_blueprint.route('/', methods=['GET'])
def index():
    """Render an optional HTML frontend."""
    return render_template('index.html')

@api_blueprint.route('/get_news_summary', methods=['POST'])
def get_news_summary():
    """Handles requests to summarize news and returns HTML-formatted output."""
    data = request.json
    topic = data.get("topic", "technology")
    assistant.create_assistant()
    assistant.create_thread()
    assistant.add_message_to_thread(role="user", content=f"Summarize the latest news about {topic} in accordance with your instructions. Remember to provide the output in JSON format")
    assistant.run_assistant()
    assistant.wait_for_completed()
    summary = assistant.get_summary()

    return jsonify(summary)