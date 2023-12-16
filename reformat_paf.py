from name_generator import NameGenerator


def reformat_paf_activity(event_queue):
    PAF_SCRIPT = ""
    for event in event_queue:
        if event["event"] == "WaitForPageLoad":
            PAF_SCRIPT += "\t<WaitForPageLoad/>\n"
        elif event["event"] == "click":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<script xpath="{xpath}" clickElement="true"></script>\n'
        elif event["event"] == "input":
            xpath = event["xpath"]
            value = event["value"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<input xpath="{xpath}" value="{value}"></input>\n'
        elif event["event"] == "dblClick":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click"></WaitTillElement>\n'
            PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<dblClick xpath="{xpath}"></dblClick>\n'
        elif event["event"] == "scroll":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible"></WaitTillElement>\n'
            PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<scroll xpath="{xpath}"></scroll>\n'
    

    name_engine = NameGenerator()
    activity_name = name_engine.get_activity_name()
    
    PAF_SCRIPT = f'<activity id="{activity_name}">\n' + PAF_SCRIPT + '</activity>'
    return {"PAF_SCRIPT" : PAF_SCRIPT, "activity_id" : activity_name}




def reformat_paf_flow(activity_id):

    name_engine = NameGenerator()
    flow_name = name_engine.get_flow_name()

    PAF_FLOW = f'<flow id="{flow_name}">\n'
    PAF_FLOW += f'\t<call activity="{activity_id}" xml="./sample_xml/activity.xml"></call>'
    PAF_FLOW += '</flow>'

    return {"PAF_FLOW": PAF_FLOW, "flow_id": flow_name}
              
    


        
            
