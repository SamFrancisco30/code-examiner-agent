from collections import deque


class Conversation():

    def __init__(self):
        self.conversation_history = deque(maxlen=30)
        return


    def update(self, context, response):
        # Add the user's message and the assistant's reply in history
        self.conversation_history.append({"role": "user", "content": context})
        self.conversation_history.append({"role": "assistant", "content": response})


    def get(self, context):
        history = ""
        for turn in self.conversation_history:
            prefix = "User" if turn["role"] == "user" else "Assistant"
            history += f"{prefix}: {turn['content']}\n"

        context = f"Conversation history:/n{history.strip()} /n New question:/n{context.strip()}"
        return {"messages": context}