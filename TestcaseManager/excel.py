import pandas as pd
import os


def create_excel(flow_name, base_path):
    # Check if the base_path exists, if not, create it
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print(f"Created directory: {base_path}")

    # Construct the full file path
    file_name = f"{flow_name}.xlsx"
    file_path = os.path.join(base_path, file_name)

    # Check if the file path is correctly formed
    if not os.path.isabs(file_path):
        print("Error: The file path is not an absolute path.")
        return

    # Define the columns
    columns = ['stepId', 'tag', 'xpath', 'keyName', 'value', 'condition', 'exists', 'variable1', 'variable2']

    # Create an empty DataFrame with these columns
    df = pd.DataFrame(columns=columns)

    # Save the DataFrame as an Excel file
    try:
        df.to_excel(file_path, index=False)
        print(f"Excel file created at: {file_path}")
    except Exception as e:
        print(f"Error occurred: {e}")




def is_legitimate_path(path):
    # Check if the path is a non-empty string
    if not isinstance(path, str) or not path.strip():
        return False

    # Check if the path exists
    return os.path.exists(path)



