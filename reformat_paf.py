from name_generator import NameGenerator
#from gpt import generate_pass_message, generate_fail_message


def reformat_paf_activity(event_queue):
    PAF_SCRIPT = ""
    VALIDATION_SCRIPT = "\n"
    name_engine = NameGenerator()

    for event in event_queue:
        if event["event"] == "WaitForPageLoad":
            PAF_SCRIPT += "\t<WaitForPageLoad/>\n"
        elif event["event"] == "click":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<script xpath="{xpath}" clickElement="true"></script>\n'
        elif event["event"] == "input":
            xpath = event["xpath"]
            value = event["value"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<input xpath="{xpath}" value="{value}"></input>\n'
        elif event["event"] == "dblClick":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<dblClick xpath="{xpath}"></dblClick>\n'
        elif event["event"] == "scroll":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<scroll xpath="{xpath}"></scroll>\n'
        elif event["event"] == "getText":
            #getText_variable = name_engine.get_variable_name()
            xpath = event["xpath"]
            variable = event["variable"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}"></getText>\n'
        elif event["event"] == "variable-value":
            variable_name = event["name"]
            variable_value = event["value"]
            PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}"></variable>\n'
        elif event["event"] == "validation-exists" or event["event"] == "validation-not-exists":
            validation_name = event["validation_name"]
            xpath = event["xpath"]
            #instruction = event["instruction"]
            #passMsg = generate_pass_message(instruction)
            passMsg = event["pass_msg"]
            #failMsg = generate_fail_message(instruction)
            failMsg = event["fail_msg"]
            #PAF_SCRIPT += '\t<wait time="5000"></wait>\n'
            PAF_SCRIPT += f'\t<validation valGroupIds="{validation_name}"></validation>\n'
            VALIDATION_SCRIPT += f'\n<valGroup groupId="{validation_name}">\n'
            if event["event"] == "validation-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="true" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            elif event["event"] == "validation-not-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="false" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            VALIDATION_SCRIPT += f'</valGroup>\n'
    

    activity_name = name_engine.get_activity_name()
    
    PAF_SCRIPT = f'<activity id="{activity_name}">\n' + PAF_SCRIPT + '</activity>' + VALIDATION_SCRIPT
    return {"PAF_SCRIPT" : PAF_SCRIPT, "activity_id" : activity_name}




def reformat_paf_flow(activity_id):

    name_engine = NameGenerator()
    flow_name = name_engine.get_flow_name()

    PAF_FLOW = f'<flow id="{flow_name}">\n'
    PAF_FLOW += f'\t<call activity="{activity_id}" xml="./sample_xml/activity.xml"></call>'
    PAF_FLOW += '</flow>'

    return {"PAF_FLOW": PAF_FLOW, "flow_id": flow_name}
              
    


        
            
