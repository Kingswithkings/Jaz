import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_internet_activity(
    website_or_app: str,
    url: str | None = None,
    summary: str | None = None
):
    prompt = f"""
    You are a child-safety classifier for JAZ, a child learning and care app.

    Classify this internet activity for a child.

    Website/App: {website_or_app}
    URL: {url or "Not provided"}
    Summary: {summary or "Not provided"}

    Return only one of these labels:
    educational
    neutral
    unsafe

    Definitions:
    - educational: learning, school work, reading, maths, science, coding, creativity, Bible learning, language learning
    - neutral: harmless entertainment, general browsing, cartoons, music, sports, games without obvious danger
    - unsafe: adult content, violence, gambling, drugs, bullying, hate, self-harm, stranger chat, dangerous trends, sexual content, private data exposure
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You classify child internet activity strictly and safely."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    label = completion.choices[0].message.content.strip().lower()

    if label not in ["educational", "neutral", "unsafe"]:
        return "neutral"

    return label