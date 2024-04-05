import openai
import os

# Set up your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_personalized_greeting(description):
    prompt = f"Write a personalized greeting for someone based on the following description: {description}"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    generated_greeting = response.choices[0].text.strip()
    return generated_greeting

if __name__ == "__main__":
    person_description = input("Enter a brief description of the person: ")
    personalized_greeting = generate_personalized_greeting(person_description)
    print(personalized_greeting)