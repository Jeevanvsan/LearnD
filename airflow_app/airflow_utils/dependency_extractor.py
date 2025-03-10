import ast

class AirflowDependencyExtractor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = []

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.RShift):  # Looking for the >> operator
            left_tasks = self.extract_task_names(node.left)
            right_tasks = self.extract_task_names(node.right)
            
            if left_tasks and right_tasks:
                # If the right side is a list, break down each task
                for left_task in left_tasks:
                    if isinstance(node.right, ast.List):
                        for right_task in right_tasks:
                            self.dependencies.append({"from": left_task, "to": right_task})
                    else:
                        # If not a list, add the direct dependency
                        self.dependencies.append({"from": left_task, "to": right_tasks[0]})
        
        self.generic_visit(node)

    def extract_task_names(self, node):
        if isinstance(node, ast.Name):  # Single task name
            return [node.id]
        elif isinstance(node, ast.List):  # List of tasks
            task_list = []
            for elt in node.elts:
                task_list += self.extract_task_names(elt)
            return task_list
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.RShift):  # Handling chains
            left_tasks = self.extract_task_names(node.left)
            right_tasks = self.extract_task_names(node.right)
            # Return only the right-most task names as the valid target
            return right_tasks  
        return []

    def extract(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.dependencies

# Example DAG code
if __name__ == "__main__":
    dag_code = '''
training_model_tasks >> choose_best_model >> [is_accurate, is_inaccurate]
    '''

    # Extracting dependencies
    extractor = AirflowDependencyExtractor()
    dependencies = extractor.extract(dag_code)

    # Printing the extracted dependencies
    print(dependencies)
    for dep in dependencies:
        print(f"From: {dep['from']}  ->  To: {dep['to']}")
