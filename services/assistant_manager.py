import openai
import time
import json
from config import Config
from services.news_service import NewsService  

class AssistantManager:
    """Handles OpenAI Assistant interactions, threading, and function calling."""
    assistant_id = Config.ASSISTANT_ID 
    thread_id = Config.THREAD_ID

    def __init__(self, model="gpt-3.5-turbo"):
        """Initialize OpenAI client and assistant settings."""
        Config.ensure_openai_key()  
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None
        self._load_existing()

    def _load_existing(self):
        """Retrieve existing assistant and thread if they are stored."""
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(AssistantManager.assistant_id)

        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(AssistantManager.thread_id)

    def create_assistant(self):
        """Creates an AI Assistant if not already stored."""
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name="News Assistant",
                instructions=(
                    "Summarize multiple news articles into a single, well-structured paragraph. "
                    "**Do NOT** use bullet points, numbered lists, or separate sections. "
                    "Ensure all key points are smoothly integrated into a single paragraph. "
                    "Use **in-text citations** in parentheses at the end of relevant sentences (e.g., '[BBC - Article Title]'). "
                    "At the **end of the summary**, provide a 'Sources:' section listing each article with its URL."
                ),
                model=self.model,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "get_news",
                        "description": "Fetches the latest news on a given topic",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string",
                                    "description": "The news topic to summarize"
                                }
                            },
                            "required": ["topic"]
                        }
                    }
                }]
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"✅ Assistant Created! ID: {assistant_obj.id}")

    def create_thread(self):
        """Creates a new conversation thread and stores both system instructions & user query."""
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj

            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=(
                    "INSTRUCTIONS: You MUST return the response strictly as a JSON object. "
                    "DO NOT include bullet points, markdown formatting, or extra text. "
                    "Return the data ONLY in this JSON format:\n\n"
                    "{\n"
                    '  "summary": "Brief news summary",\n'
                    '  "citations": [\n'
                    '    {\n'
                    '      "intextCitation": "BBC",\n'
                    '      "articleName": "Title of article",\n'
                    '      "link": "https://example.com/article"\n'
                    "    }\n"
                    "  ]\n"
                    "}\n\n"
                    "IMPORTANT: If the articles do not contain sufficient information, return:\n"
                    "{ \"summary\": \"No relevant news found.\", \"citations\": [] }\n"
                    "FAILURE TO RETURN VALID JSON WILL RESULT IN ERRORS."
                )
            )
            print(f"✅ Thread Created with System Instructions & User Request! ID: {thread_obj.id}")

    def add_message_to_thread(self, role, content):
        """Adds a user message to request a summary."""
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    def run_assistant(self):
        """Runs the assistant and processes messages."""
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )

    def wait_for_completed(self):
        """Waits for assistant to complete processing."""
        if self.thread and self.run:
            while True:
                time.sleep(3)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )
                print(f"🟡 Assistant Run Status: {run_status.status}")
                if run_status.status == "completed":
                    self.process_messages()
                    break
                elif run_status.status == "requires_action":
                    print("⚠️ Assistant is requesting function execution!")
                    self.call_required_functions(run_status.required_action.submit_tool_outputs.model_dump())

    def process_messages(self):
        """Retrieves messages and ensures JSON format."""
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            last_message = messages.data[0]  

            try:
                response_text = last_message.content[0].text.value.strip()
                self.summary = json.loads(response_text)
                print(f"✅ Parsed JSON Summary: {json.dumps(self.summary, indent=4)}")  
            except json.JSONDecodeError:
                print("❌ Assistant response is not valid JSON! Debugging output:")
                print(response_text)
                self.summary = {"error": "Invalid response format from assistant"}

    def call_required_functions(self, required_actions):
        """Executes function calls requested by the assistant."""
        tool_outputs = []
        print(f"⚙️ Assistant Requested Tools: {required_actions}")  

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_news":
                print(f"🔍 Running get_news() for topic: {arguments['topic']}")  
                output = NewsService.get_news(topic=arguments["topic"])
                print("\n📢 FINAL NEWS DATA SENT TO ASSISTANT:\n")
                print(output)

                tool_outputs.append({"tool_call_id": action["id"], "output": output})

        if tool_outputs:
            print("✅ Submitting tool outputs to OpenAI")
            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread.id,
                run_id=self.run.id,
                tool_outputs=tool_outputs
            )

    def get_summary(self):
        """Returns the processed summary."""
        return self.summary
