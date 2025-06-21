import openai

openai.api_key = "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"


def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following text."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message['content'].strip()


def extract_keywords(text):
    words = text.split()
    return list(set(words[:5]))