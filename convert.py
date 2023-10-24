import pandas as pd

excel_file = "TC-data.xlsx"
sheet_name = "Sheet1"
indent_count = 1
indentation = "\t"

df = pd.read_excel(excel_file, sheet_name=sheet_name)

def generate_tag(row):
    global indent_count

    if not pd.isna(row['tag']):
        tagName = row['tag']
        row = row.drop(['tag'])
        attributes = ''
        for column, cell in row.items():
            if not pd.isna(cell):
                attributes += f'{column}="{cell}" '
        
        indent = indentation * indent_count
        return f"{indent}<{tagName} {attributes}></{tagName}>\n"
    
    elif not pd.isna(row['tag_start']):
        tagName = row['tag_start']
        row = row.drop(['tag_start'])
        attributes = ''
        for column, cell in row.items():
            if not pd.isna(cell):
                attributes += f'{column}="{cell}" '

        indent = indentation * indent_count
        result = f"{indent}<{tagName} {attributes}>\n"
        indent_count += 1
        return result
    
    elif not pd.isna(row['tag_end']):
        tagName = row['tag_end']
        indent_count -= 1
        indent = indentation * indent_count
        return f"{indent}</{tagName}>\n\n"
    

def main():
    code = ""
    for index, row in df.iterrows():
        tag = generate_tag(row)
        code += tag
    print(code)
    


if __name__=="__main__":
    main()

