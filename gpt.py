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




def gpt_call(openai, gpt_model, deployment_id, data, results):
    # Define the prompt for GPT-4
    prompt = (f"""
    Some functionality along with their description is given below. Your task is to return the functionality or sequence of functionalities from the 4 given below which fullfils the user prompt. Return the response only as JSON.
              Functionality description : Functionality name

              1. {results[0]['content']}
              2. {results[1]['content']}
              3. {results[2]['content']}
              4. {results[3]['content']}
              """)
    
    function_prompt = "Your task is to use the user prompt which has instructions and unformatted data, and return the functionality or sequence of functionalities from the 5 given below, which can fullfill the users instructions." 
    
    functionality_sequencer = {
                "type": "function",
                "function": {
                    "name": "get_functionality_sequence",
                    "description": function_prompt,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "commands": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "The functionality name in sequence"
                                },
                            "description": "List of functionality names in sequence"
                            },
                        },
                        "required": ["commands"]
                    },
                }   
            }

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
        #tools=[functionality_sequencer],
        #tool_choice="auto"
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
        if word in keywords:
            found_keywords.append(word)

    return found_keywords





if __name__ == "__main__":
    align_input_steps({"instruction": "I want to check whether my text equals this text"})
