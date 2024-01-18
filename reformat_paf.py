from name_generator import NameGenerator
#from gpt import generate_pass_message, generate_fail_message


def reformat_paf_activity(event_queue):
    PAF_SCRIPT = ""
    VALIDATION_SCRIPT = "\n"
    name_engine = NameGenerator()

    for event in event_queue:
        if event["event"] == "WaitForPageLoad":
            PAF_SCRIPT += "\t<WaitForPageLoad/>\n"
        elif event["event"] == "end-if":
            PAF_SCRIPT += "\t</if>\n"
        elif event["event"] == "end-if-then":
            PAF_SCRIPT += "\t\t</then>\n"
            PAF_SCRIPT += "\t\t<else>\n"
        elif event["event"] == "end-else":
            PAF_SCRIPT += "\t\t</else>\n"
            PAF_SCRIPT += "\t</if>\n"
        elif event["event"] == "click":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<script xpath="{xpath}" clickElement="true"></script>\n'
        elif event["event"] == "frame":
            id = event["id"]
            PAF_SCRIPT += f'\t<frame id="{id}"></frame>\n'
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
            after = event["after"]
            before = event["before"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            if not after and not before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}"></getText>\n'
            elif after and not before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotAfter="true"></getText>\n'
            elif not after and before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotBefore="true"></getText>\n'
            else:
               PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotAfter="true" snapshotBefore="true"></getText>\n' 
        elif event["event"] == "variable-value":
            variable_name = event["name"]
            variable_value = event["value"]
            after = event["after"]
            before = event["before"]
            if not after and not before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}"></variable>\n'
            elif after and not before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotAfter="true"></variable>\n'
            elif not after and before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotBefore="true"></variable>\n'
            else:
               PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotAfter="true" snapshotBefore="true"></variable>\n'
        elif event["event"] in ["validation-exists", "validation-not-exists"]:
            if event["validation_name"] == "Enter validation name(optional)":
                event["validation_name"] = name_engine.get_validation_name()
            if event["pass_msg"] == "Enter pass message(optional)":
                event["pass_msg"] = "STEP PASSED"
            if event["fail_msg"] == "Enter fail message(optional)":
                event["fail_msg"] = "STEP FAILED"  
            validation_name = event["validation_name"]
            xpath = event["xpath"]
            after = event["after"]
            before = event["before"]
            passMsg = event["pass_msg"]
            failMsg = event["fail_msg"]
            if_condition = event["if_condition"]
            if_else_condition = event["if_else_condition"]
            #PAF_SCRIPT += '\t<wait time="5000"></wait>\n'
            if not if_condition and not if_else_condition:
                PAF_SCRIPT += f'\t<validation valGroupIds="{validation_name}"></validation>\n'
            elif if_else_condition:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}">\n'
                PAF_SCRIPT += f'\t<then>\n'
            else:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}">\n'
            VALIDATION_SCRIPT += f'\n<valGroup groupId="{validation_name}">\n'
            if event["event"] == "validation-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="true" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            elif event["event"] == "validation-not-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="false" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            VALIDATION_SCRIPT += f'</valGroup>\n'
        elif event["event"] in ["validation-equals", "validation-not-equals", "validation-num-equals", "validation-num-not-equals"]:
            if event["validation_name"] == "Enter validation name(optional)":
                event["validation_name"] = name_engine.get_validation_name()
            if event["pass_msg"] == "Enter pass message(optional)":
                event["pass_msg"] = "STEP PASSED"
            if event["fail_msg"] == "Enter fail message(optional)":
                event["fail_msg"] = "STEP FAILED"    
            validation_name = event["validation_name"]
            variable1 = event["variable1"]
            variable2 = event["variable2"]
            passMsg = event["pass_msg"]
            failMsg = event["fail_msg"]
            if_condition = event["if_condition"]
            if_else_condition = event["if_else_condition"]
            if not if_condition and not if_else_condition:
                PAF_SCRIPT += f'\t<validation valGroupIds="{validation_name}"></validation>\n'
            elif if_else_condition:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}">\n'
                PAF_SCRIPT += f'\t\t<then>\n'
            else:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}">\n'
            VALIDATION_SCRIPT += f'\n<valGroup groupId="{validation_name}">\n'
            if event["event"] == "validation-equals":
                VALIDATION_SCRIPT += f'\t<validate variable="{variable1}" condition="equals" value="{variable2}" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            elif event["event"] == "validation-not-equals":
                VALIDATION_SCRIPT += f'\t<validate variable="{variable1}" condition="not_equals" value="{variable2}" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            elif event["event"] == "validation-num-equals":
                VALIDATION_SCRIPT += f'\t<validate variable="{variable1}" condition="num_equals" value="{variable2}" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
            elif event["event"] == "validation-num-not-equals":
                VALIDATION_SCRIPT += f'\t<validate variable="{variable1}" condition="num_not_equals" value="{variable2}" passMsg="{passMsg}" failMsg="{failMsg}"></validate>\n'
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
              
    


        
            
