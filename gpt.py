from search_redis import search
from openai_auth import get_token
import string

def align_input_steps(instruction):

    results = search(instruction)

    deployment_id, gpt_model, embedding_model, openai = get_token()
    
    raw_response = gpt_call(openai, gpt_model, deployment_id, instruction, results)
    response = raw_response.choices[0]["message"]["content"]
    print(f"The response is : {response}\n")
    #response_content = raw_response.choices[0].message 
    # response = response_content.to_dict()['tool_calls']['arguments']
    # response = json.loads(response)
    # print(f"The response is : {response}")
    functional_sequence = extract_sequence(response)
    print(f"The functional sequence is : {functional_sequence}\n")
    return functional_sequence




def gpt_call(openai, gpt_model, deployment_id, data, results):
    # Define the prompt for GPT-4
    prompt = (f"""
    You are a helpful assistant incapable of doing anything but converting the user query to a set of Functions. Using only the below given functions, return the required function name/names in sequence to execute the user query. 
              
              Function description : Function name

              1. {results[0]['content']}
              2. {results[1]['content']}
              3. {results[2]['content']}
              4. {results[3]['content']}
              """)
    
    

    # Make the API call to GPT-4
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": data}
        ],
    )

    return response



def extract_sequence(text):
    keywords = [
        "getText", "loop", "validate-exists", "validate-not-exists", "if-condition",
        "variable-expression", "validation-equals", "validation-not-equals",
        "validation-num-equals", "validation-num-not-equals", "validation-num-le",
        "validation-num-ge", "validation-contains", "validation-starts-with",
        "validation-ends-with"
    ]
    found_keywords = []
    translator = str.maketrans('', '', string.punctuation.replace('-', ''))
    cleaned_text = text.translate(translator)
    words = cleaned_text.split()
    print(words)
    for word in words:
        if word in keywords and (word not in found_keywords):
            found_keywords.append(word)

    return found_keywords



def generate_pass_message(instruction):
    prompt = (f"""
    The user prompt will be an instruction. Return ONLY a message which indicates that the test has passed while executing the instruction. 
              """)

    deployment_id, gpt_model, embedding_model, openai = get_token()
    raw_response = gpt_call_message_generate(openai, gpt_model, deployment_id, instruction, prompt)
    response = raw_response.choices[0]["message"]["content"]
    print(f"The response is : {response}\n")
    return response


def generate_fail_message(instruction):
    prompt = (f"""
    The user prompt will be an instruction. Return ONLY a message which indicates that the test has failed while executing the instruction. 
              """)

    deployment_id, gpt_model, embedding_model, openai = get_token()
    raw_response = gpt_call_message_generate(openai, gpt_model, deployment_id, instruction, prompt)
    response = raw_response.choices[0]["message"]["content"]
    print(f"The response is : {response}\n")
    return response


def gpt_call_message_generate(openai, gpt_model, deployment_id, data, prompt):
    
    # Make the API call to GPT-4
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": data}
        ],
    )

    return response


if __name__ == "__main__":
    generate_pass_message("I want to check whether my text equals this text")
