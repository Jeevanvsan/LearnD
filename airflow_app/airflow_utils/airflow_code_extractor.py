import ast
import json
import re

import yaml


class DagExtract:
    def __init__(self):
        self.airflow_config = self.load_config()
        
    @staticmethod
    def load_config():
        with open("airflow_app/airflow_utils/airflow_config.yml", "r") as dag_conf:
            return yaml.safe_load(dag_conf)

    def run(self,dag_code: str) -> dict:
            """
            Extract dag properties from code.

            Args: 
                dag_code(str): Airflow dag code

            Return:
                dag_info(json): Extracted data as json
            
            """
            tree = ast.parse(dag_code)

            dag_info = {
                "imports":[],
                "dag_id": None,
                "schedule_interval": None,
                "default_args": {},
                "tasks": [],
                "dependencies": [],
                "variables":{}
            }

            task_names = set()  # Store task IDs

            for node in ast.walk(tree):
                # Extract Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dag_info["imports"].append(alias.name)

                if isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    for alias in node.names:
                        import_statement = f"from {module} import {alias.name}"
                        dag_info["imports"].append(import_statement)

                # Extract Variables
                if isinstance(node, ast.Assign):

                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # print(var_name,ast.dump(node.value))
                            try:
                                dag_info["variables"][var_name] = ast.literal_eval(node.value)
                            except:
                                dag_info["variables"][var_name] = ast.unparse(node.value)

                # Extract DAG properties
                if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == "DAG":
                    for keyword in node.keywords:
                        # print(ast.dump(keyword))

                        if keyword.arg == "dag_id":
                            dag_info["dag_id"] = ast.literal_eval(keyword.value)
                        elif keyword.arg == "schedule_interval":
                            dag_info["schedule_interval"] = ast.literal_eval(keyword.value)
                        elif keyword.arg == "default_args":
                            if isinstance(keyword.value, ast.Dict):
                                for key, value in zip(keyword.value.keys, keyword.value.values):
                                    if isinstance(key, ast.Constant):
                                        try:
                                            dag_info["default_args"][key.value] = ast.literal_eval(value)
                                        except:
                                            dag_info["default_args"][key.value] = ast.unparse(value)
                            else:
                                if isinstance(keyword.value, ast.Name):
                                    df_id = keyword.value.id
                                    dag_info["default_args"] =  dag_info.get("variables").get(df_id,"")



                                

                # Extract Task Definitions
                if isinstance(node, ast.Assign):  # Check for task assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                            func_name = (
                                node.value.func.attr if isinstance(node.value.func, ast.Attribute) else node.value.func.id
                            )
                            if func_name in self.airflow_config['airflow_operators']:
                                task_names.add(target.id)
                                dag_info["tasks"].append({"task_id": target.id})

                # Extract Decorated Tasks
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "task":
                            task_names.add(node.name)
                            dag_info["tasks"].append({"task_id": node.name})

            # Extract Task Dependencies
            dependencies = re.findall(r"(\w+)\s*>>\s*(\w+)", dag_code)
            for dep in dependencies:
                if dep[0] in task_names and dep[1] in task_names:  # Ensure valid task names
                    dag_info["dependencies"].append({"from": dep[0], "to": dep[1]})

            return json.dumps(dag_info, indent=4)
    

if __name__ == "__main__":
    code = """
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

# Define default arguments
# default_args = {
#     'owner': 'airflow',
#     'start_date': days_ago(1),
#     'retries': 1,
# }

# Define DAG
with DAG(
    dag_id='sample_etl_dag',
    default_args={'owner': 'airflow','start_date': days_ago(1),'retries': 1},
    schedule_interval='@daily',  # Runs daily
    catchup=False,
    tags=['etl', 'example']
) as dag:
    @task
    def start_task():
        print("Starting ETL process...")
    @task
    def extract_data():
        print("Extracting data...")
        return {"data": "raw_data"}  # Example output
    @task
    def transform_data(extracted_data):
        print(f"Transforming data: {extracted_data}")
        transformed_data = extracted_data["data"].upper()
        return {"data": transformed_data}
    @task
    def load_data(transformed_data):
        print(f"Loading data: {transformed_data}")
        return "Data loaded successfully!"
    @task
    def end_task():
        print("ETL process completed!")

    # Task Dependencies
    start = start_task()
    extracted_data = extract_data()
    transformed_data = transform_data(extracted_data)
    loaded_data = load_data(transformed_data)
    end = end_task()
    start >> extracted_data >> transformed_data >> loaded_data >> end

"""
    ob = DagExtract()
    print(ob.run(code))
    