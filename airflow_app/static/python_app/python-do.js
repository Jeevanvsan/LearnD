let editor;

window.require = {
    paths: {
        'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs'
    }
};

function loadEditor() {
    require(['vs/editor/editor.main'], function () {
        editor = monaco.editor.create(document.getElementById('code-editor'), {
            value: "# Write your Python code here\n",
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
        });
    });
}

document.addEventListener('DOMContentLoaded', loadEditor);

// Run code (no score, just execution)
function runCode() {
    const code = editor.getValue();

    fetch('/run-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            code: code,
            tool: "PY"
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.output);
            run(data.output);
        })
        .catch(error => console.error('Error:', error));
}

// Submit code for evaluation and scoring
function SubmitCode() {
    const code = editor.getValue();

    fetch('/submit-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            code: code,
            tool: 'PY',
            time: elapsedTime
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.output);
            resultShow(data.output);
        })
        .catch(error => console.error('Error:', error));
}

// Get CSRF token from cookie
function getCSRFToken() {
    return document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='))
        .split('=')[1];
}

// Show result in UI
function resultShow(data) {
    const resultContainer = document.getElementById('result-pane');
    resultContainer.innerHTML = ''; // Clear previous results

    const p = document.createElement('p');
    p.className = 'result-text';
    p.style.fontSize = '20px';

    const pre = document.createElement('pre');

    if (data['response'] === 'Correct') {
        p.textContent = `Correct Answer!`;
        p.style.color = 'green';
        p.style.fontWeight = 'bold';
        resultContainer.appendChild(p);

        // ✅ Stop the timer if answer is correct
        clearInterval(timerInterval);

    } else if (data['response'] === 'Incorrect') {
        p.textContent = `Incorrect Answer!`;
        p.style.color = 'red';
        resultContainer.appendChild(p);

        pre.textContent = data['Error'];
        resultContainer.appendChild(pre);
    }
}

// Display output (could be execution result or task flow)
function run(data) {
    const container = document.getElementById('task-flow');
    container.innerHTML = `<p>${data}</p>`;
}

// ------------------- TIMER SECTION ---------------------

let timerInterval;
let startTime;
let elapsedTime = 0; // Time in seconds

function startTimer() {
    startTime = Date.now() - elapsedTime * 1000;
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    elapsedTime = Math.floor((Date.now() - startTime) / 1000);

    let hours = Math.floor(elapsedTime / 3600);
    let minutes = Math.floor((elapsedTime % 3600) / 60);
    let seconds = elapsedTime % 60;

    // Format digits to two digits
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = seconds < 10 ? '0' + seconds : seconds;

    document.getElementById("timer").textContent = `${hours}:${minutes}:${seconds}`;
}

function endQuiz() {
    clearInterval(timerInterval);
    alert(`Quiz ended! Time taken: ${formatTime(elapsedTime)}`);
}

function formatTime(seconds) {
    let hours = Math.floor(seconds / 3600);
    let minutes = Math.floor((seconds % 3600) / 60);
    seconds = seconds % 60;

    return `${hours < 10 ? '0' + hours : hours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
}

// Start timer on load
startTimer();
