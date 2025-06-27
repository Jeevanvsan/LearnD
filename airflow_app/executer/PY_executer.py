import io
import contextlib

def PY_executer(code):
    output = io.StringIO()
    op = {}
    with contextlib.redirect_stdout(output):
        exec(code, op)
    return output.getvalue() or op.get('result', 'No result found')
