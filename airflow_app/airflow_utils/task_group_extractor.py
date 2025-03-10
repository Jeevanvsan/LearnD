import ast

class TaskGroupExtractor(ast.NodeVisitor):
    def __init__(self):
        self.task_groups = []

    def visit_With(self, node):
        for item in node.items:  # Iterate over 'withitem' nodes
            if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == 'TaskGroup':
                task_group_info = self.extract_task_group_info(node, item)
                self.task_groups.append(task_group_info)
        self.generic_visit(node)

    def extract_task_group_info(self, node, item):
        task_group_info = {
            'name': '',
            'tooltip': '',
            'tasks': []
        }

        if isinstance(item.context_expr, ast.Call):
            for kw in item.context_expr.keywords:
                if kw.arg == 'tooltip':
                    task_group_info['tooltip'] = kw.value.s

            if isinstance(item.context_expr.args[0], ast.Constant):
                task_group_info['name'] = item.context_expr.args[0].value

        for n in node.body:
            if isinstance(n, ast.Assign):
                task_info = self.extract_task_info(n)
                if task_info:
                    task_group_info['tasks'].append(task_info)

        return task_group_info

    def extract_task_info(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'PythonOperator':
            task_id = None
            python_callable = None

            for kw in node.value.keywords:
                if kw.arg == 'task_id':
                    task_id = kw.value.s
                elif kw.arg == 'python_callable':
                    python_callable = ast.unparse(kw.value)

            return {
                'task_id': task_id,
                'python_callable': python_callable
            }
        return None


def extract_taskgroups_from_code(code):
    tree = ast.parse(code)
    extractor = TaskGroupExtractor()
    extractor.visit(tree)
    return extractor.task_groups


# # Example usage:
# code = '''
# with TaskGroup("path_a_tasks", tooltip="Tasks for Path A") as path_a_tasks:
        
#         task_a1 = PythonOperator(
#             task_id='task_a1',
#             python_callable=lambda: print("Task A1 executed."),
#         )
        
#         task_a2 = PythonOperator(
#             task_id='task_a2',
#             python_callable=lambda: print("Task A2 executed."),
#         )
        
#         task_a1 >> task_a2
# '''

# result = extract_taskgroups_from_code(code)
# print(result)
