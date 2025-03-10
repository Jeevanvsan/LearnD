import ast
import json
import re

import yaml

from airflow_app.airflow_utils.task_group_extractor import extract_taskgroups_from_code
from airflow_app.airflow_utils.dependency_extractor import AirflowDependencyExtractor


class DagExtract:
    def __init__(self):
        self.airflow_config = self.load_config()
        
        
    @staticmethod
    def load_config():
        with open("airflow_app/airflow_utils/airflow_config.yml", "r") as dag_conf:
            return yaml.safe_load(dag_conf)

    def extract_dag_prop(self,dag_props):

        
        if dag_props.arg == "dag_id":
            self.dag_info["dag_id"] = ast.literal_eval(dag_props.value)

        # elif dag_props.args and isinstance(dag_props.args[0], ast.Constant) and isinstance(dag_props.args[0].value, str):
        #     print(ast.dump(dag_props.args[0].value)) 
        elif dag_props.arg == "description":
            self.dag_info["description"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "schedule_interval" or dag_props.arg == "schedule":
            if isinstance(dag_props.value, ast.Call) and isinstance(dag_props.value.func, ast.Name):
                # print(ast.dump(dag_props.value.func.id))
                if dag_props.value.func.id == 'timedelta':
                    args = []
                    for keyword_date in dag_props.value.keywords:
                        if isinstance(keyword_date.value, ast.Constant):  # For Python 3.8+
                            args.append(f"{keyword_date.arg}={keyword_date.value.value}")
                        elif isinstance(keyword_date.value, ast.Str):  # For Python < 3.8
                            args.append(f"{keyword_date.arg}={keyword_date.value.s}")
                    st_ =  f"timedelta({', '.join(args)})"
                    self.dag_info["schedule"] = st_
            else:
                self.dag_info["schedule"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "start_date":
            if isinstance(dag_props.value, ast.Call) and isinstance(dag_props.value.func, ast.Name):
                args = []
                for keyword_date in dag_props.value.keywords:
                    if isinstance(keyword_date.value, ast.Constant):  # For Python 3.8+
                        args.append(f"{keyword_date.arg}={keyword_date.value.value}")
                    elif isinstance(keyword_date.value, ast.Str):  # For Python < 3.8
                        args.append(f"{keyword_date.arg}={keyword_date.value.s}")

                if dag_props.value.func.id == 'datetime':
                    st_ =  f"datetime({', '.join(args)})"
                elif dag_props.value.func.id == 'days_ago':
                    st_ =  f"days_ago({', '.join(args)})"

                self.dag_info["start_date"] = st_
        elif dag_props.arg == "catchup":
            self.dag_info["catchup"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "max_active_runs":
            self.dag_info["max_active_runs"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "render_template_as_native_obj":
            self.dag_info["render_template_as_native_obj"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "tags":
            self.dag_info["tags"] = ast.literal_eval(dag_props.value)
        elif dag_props.arg == "default_args":
            if isinstance(dag_props.value, ast.Dict):
                for key, value in zip(dag_props.value.keys, dag_props.value.values):
                    if isinstance(key, ast.Constant):
                        try:
                            self.dag_info["default_args"][key.value] = ast.literal_eval(value)
                        except:
                            self.dag_info["default_args"][key.value] = ast.unparse(value)
            else:
                if isinstance(dag_props.value, ast.Name):
                    df_id = dag_props.value.id
                    self.dag_info["default_args"] =  self.dag_info.get("variables").get(df_id,"")
            

    def run(self,dag_code: str) -> dict:
            """
            Extract dag properties from code.

            Args: 
                dag_code(str): Airflow dag code

            Return:
                self.dag_info(json): Extracted data as json
            
            """
            tree = ast.parse(dag_code)

            self.dag_info = {
                "imports":[],
                "dag_id": None,
                "tags":None,
                "description":None,
                "schedule": None,
                "start_date":None,
                "catchup":None,
                "max_active_runs":None,
                "render_template_as_native_obj":None,
                "default_args": {},
                "tasks": [],
                "dependencies": [],
                "variables":{},
                "task_group":[],

            }

            task_names = set()  # Store task IDs


            for node in ast.walk(tree):  

                # Extract Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.asname:
                            self.dag_info["imports"].append(f"import {alias.name} as {alias.asname}")
                        else:
                            self.dag_info["imports"].append(f"import {alias.name}")
                        

                if isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    for alias in node.names:
                        import_statement = f"from {module} import {alias.name}"
                        self.dag_info["imports"].append(import_statement)

                # Extract Variables
                if isinstance(node, ast.Assign):

                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # print(var_name,ast.dump(node.value))
                            try:
                                self.dag_info["variables"][var_name] = ast.literal_eval(node.value)
                            except:
                                self.dag_info["variables"][var_name] = ast.unparse(node.value)

                # Extract DAG properties
                if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == "DAG":
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        # print(node.args[0].value) 
                        self.dag_info["dag_id"] = node.args[0].value


                    for keyword in node.keywords:
                        self.extract_dag_prop(keyword)                    
                        
                if isinstance(node, ast.FunctionDef):

                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and getattr(decorator.func, 'id', '') == 'dag':
                            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                                self.dag_info["dag_id"] = node.args[0].value
                            for keys in decorator.keywords:
                                self.extract_dag_prop(keys)

                # Extract Task Definitions
                if isinstance(node, ast.Assign):  # Check for task assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                            func_name = (
                                node.value.func.attr if isinstance(node.value.func, ast.Attribute) else node.value.func.id
                            )
                            if func_name in self.airflow_config['airflow_operators']:
                                task_names.add(target.id)
                                self.dag_info["tasks"].append({"task_id": target.id})

                # Extract Decorated Tasks
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        # print(ast.dump(decorator))
                        if isinstance(decorator, ast.Name) and decorator.id == "task":
                            task_names.add(node.name)
                            self.dag_info["tasks"].append({"task_id": node.name})
                        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "task":
                            task_names.add(node.name)
                            self.dag_info["tasks"].append({"task_id": node.name})



            # Extract Task Dependencies
            extractor = AirflowDependencyExtractor()
            dependencies = extractor.extract(dag_code)
            self.dag_info["dependencies"] = dependencies

            task_grp = extract_taskgroups_from_code(dag_code)
            if task_grp:
                # print(task_grp)
                flag = []
                self.dag_info["task_group"].append({"task_id": grp["name"], "details": grp})
                deps = self.dag_info["dependencies"]

                for grp in task_grp:
                    
                    for i, dep in enumerate(deps):
                        if dep["from"] in grp["name"]:
                            flag.append(i)
                            to_ = dep["to"]
                            deps.append({"from": grp["tasks"][-1]["task_id"],"to":to_})                        
                        elif dep["to"] in grp["name"]:
                            flag.append(i)
                            from_ = dep["from"]
                            deps.append({"from": from_,"to":grp["tasks"][0]["task_id"]})
                        
                self.dag_info["dependencies"] = [item for i, item in enumerate(deps) if i not in flag]


                
            return self.dag_info
    

# if __name__ == "__main__":
#     code = """

# from airflow import DAG
# from airflow.operators.python import PythonOperator, BranchPythonOperator
# from airflow.operators.dummy import DummyOperator
# from airflow.utils.dates import days_ago
# from airflow.utils.task_group import TaskGroup
# from datetime import timedelta
# import random

# # Default arguments for the DAG
# default_args = {
#     'owner': 'user',
#     'depends_on_past': False,
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# # Define the DAG
# with DAG(
#     'complex_dag',
#     default_args=default_args,
#     description='A complex DAG example',
#     schedule_interval=timedelta(days=1),
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:

#     # Start Task
#     start_task = DummyOperator(task_id='start_task')

#     # Branching function
#     def choose_branch():
#         branches = ['path_a', 'path_b']
#         chosen_branch = random.choice(branches)
#         print(f"Chosen path: {chosen_branch}")
#         return chosen_branch

#     branching_task = BranchPythonOperator(
#         task_id='branching_task',
#         python_callable=choose_branch,
#     )

#     # Define Task Groups for parallel processing
#     with TaskGroup("path_a_tasks", tooltip="Tasks for Path A") as path_a_tasks:
        
#         task_a1 = PythonOperator(
#             task_id='task_a1',
#             python_callable=lambda: print("Task A1 executed."),
#         )
        
#         task_a2 = PythonOperator(
#             task_id='task_a2',
#             python_callable=lambda: print("Task A2 executed."),
#         )
        
#         task_a1 >> task_a2

#     with TaskGroup("path_b_tasks", tooltip="Tasks for Path B") as path_b_tasks:
        
#         task_b1 = PythonOperator(
#             task_id='task_b1',
#             python_callable=lambda: print("Task B1 executed."),
#         )
        
#         task_b2 = PythonOperator(
#             task_id='task_b2',
#             python_callable=lambda: print("Task B2 executed."),
#         )
        
#         task_b1 >> task_b2

#     # Merging paths
#     join_task = DummyOperator(task_id='join_task', trigger_rule='none_failed_min_one_success')

#     # End Task
#     end_task = DummyOperator(task_id='end_task')

#     # Define task dependencies
#     start_task >> branching_task
#     branching_task >> path_a_tasks >> join_task
#     branching_task >> path_b_tasks >> join_task
#     join_task >> end_task

  
# """
#     ob = DagExtract()
#     with open("airflow_app/airflow_utils/airflow_json.json", "w") as airflow_data:
#         json.dump(ob.run(code),airflow_data, indent=4)
    