from openai import OpenAI
import os
import platform

def main(code):
    try:
        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        )

        completion = client.chat.completions.create(
        model="meta-llama/llama-3.1-70b-instruct:free",
        messages=[
            { "role": "system", 
                "content": "You are a software engineer , your only and the only task is to create the Requierements.txt file , that's it , you will get a python code then your task is to return the requirements.txt only with no anything else, don't explain or anything" 
            },
            {
            "role": "user",
            "content": code
            }
        ]
        )
        response = completion.choices[0].message.content

        pkgs_cleaned = response.replace("```", "").replace("requirements.txt", "")

        def install_pkgs(pkgs):
            with open("requirements.txt",'w+') as f:
                f.writelines(pkgs)
            print("done")

            if platform.system() == "Windows":
                os.system("pip install -r requirements.txt")
            else:
                os.system("python -m venv venv")
                os.system("source venv/bin/activate")
                os.system("pip install -r requirements.txt")

        install_pkgs(pkgs_cleaned)

    except Exception as e:
        print(e)

