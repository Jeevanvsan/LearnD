import io
import contextlib

def PY_executer(code):
    output = io.StringIO()
    op = {}
    try:
        with contextlib.redirect_stdout(output):
            exec(code, op)
    except SyntaxError as e:
        output.write(f"Syntax Error: {str(e)}\n")
        return str(e)
    except Exception as e:
        output.write(f"Error: {str(e)}\n")
        return str(e)
    
    return output.getvalue() or op.get('result', 'No result found')
