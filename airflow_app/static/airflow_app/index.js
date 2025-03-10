let editor;

window.require = { paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs' } };

function loadEditor() {
    require(['vs/editor/editor.main'], function () {
        editor = monaco.editor.create(document.getElementById('code-editor'), {
            value: "# Write your Python code here\n\ndef sum_of_evens(numbers):\n    return sum(x for x in numbers if x % 2 == 0)",
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
        });
    });
}

document.addEventListener('DOMContentLoaded', loadEditor);

function runCode() {
    const code = editor.getValue();

    fetch('/run_code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        alert('Output: ' + data.output);
    })
    .catch(error => console.error('Error:', error));
}

function getCSRFToken() {
    return document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='))
        .split('=')[1];
}