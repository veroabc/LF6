import openai
import gradio
import chat

openai.api_key = "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"

messages = [{"role": "system", "content": "You are a system administrator from help desk specialised on cloudcomputing, SaaS, PaaS, IaaS"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

demo = gradio.Interface(fn=CustomChatGPT, inputs = "text", outputs = "text", title = "Support")

demo.launch(share=True)