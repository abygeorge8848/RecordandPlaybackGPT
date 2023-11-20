from openai_auth import get_token


def get_PAF_code(question):
    deployment_id, gpt_model, embedding_model, openai = get_token()
    formatted_response = gpt_call(openai, gpt_model, deployment_id, question)
    print(formatted_response.choices[0]["message"]["content"])


def gpt_call(openai, gpt_model, deployment_id, question):

    # Results comes from redis search, so needs to be unpacked
    prompt = (f"""
    The below content gives information about an XML framework named PAF. Use that information to create the PAF code for the user query  
    Some attributes for each tag will be given. If an attribute is not given then please fill the attribute value,  
    with an appropriate value according to the attribute description. In case direct PAF code is given, then you can
    directly use it along with the rest of the given input. Only return the PAF code in the correct syntax and format.
              
              PAF MANUAL 
              ----------

              Every set of set instructions must be enclosed in an activity tag :
              <activity id="activity_name">
               -
               -
               -
              </activity>
            
              The activity can be named anything. Simply replace the 'activity_name' in the id attribute 
              with an appropriate name which describes what the activity is doing.

              Now the content inside the activity tag would be the individual functionality. Each functionality
              be a simple tag like <click xpath=""></click>, <input xpath="" value=""></input> which form the
              building blocks of PAF. Now let us explore some PAF tags with their corresponding functionality.

              To do a click action :
              <click xpath="xpath_value"></click>
              Here the xpath attribute represents the xpath of the element you want to click on. 'Replace xpath_value'
              with the xpath of the respective element.

              To input some text into a textbox :
              <input xpath="xpath_value" value="value_to_be_entered">
              xpath attribute is the xpath of the textbox you want to enter your text in.
              The value attribute represents the text you want to enter in the textfield.

              To wait for a specified amount of time in ms :
              <wait time="time_in_ms"></wait>
              Where the time attribute is the time in ms.

              To wait till the page has loaded :
              <WaitForPageLoad/>

              To double click on an element :
              <dblClick xpath="xpath_value"></dblClick>
              The xpath attribute is the xpath of the element you need to double click on

              To scroll to a particular element :
              <scroll xpath="xpath_value"></scroll>
              Where xpath is the element to be scrolled to.

              To get the text of an element :
              <getText xpath="xpath_value" variable="variable_name"></getText>
              The xpath attribute represents the xpath of the element whose text is to be read.
              The variable attribute represents an appropriate name for the variable in which the text is to be 
              stored. If there are multiple variables in a single activity, each variable name must be unique.


              """)

    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )

    return response

if __name__ == "__main__":
    #get_PAF_code("""page loading, click xpath="//button[@id='continue']", input xpath="//input[@id='username'] with 
    #the username to be input as aby.george@iqvia.com" retrieve the text value xpath="//h1[@title="grantplan"]", 
    #now I want a text xpath="//strong[@id='header']" """)
    get_PAF_code("""<WaitForPageLoad/> <click xpath="//button[@id='continue']"> <input xpath="//input[@id='username']" value="aby.george@iqvia.com"></input>. Now I want to extract the text value of the element xpath="(//h3[@title="procedure"])[2]" """)