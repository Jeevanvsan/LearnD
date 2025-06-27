let editor;

window.require = { paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs' } };

function loadEditor() {
    require(['vs/editor/editor.main'], function () {
        editor = monaco.editor.create(document.getElementById('code-editor'), {
            value: "# Write your DAG code here\n",
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
        });
    });
}

document.addEventListener('DOMContentLoaded', loadEditor);

function runCode() {
    const code = editor.getValue();

    fetch('/run-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ 
          code:code, 
          tool:"PY"
        })
    })
    .then(response => response.json())
    .then(data => {
        //  ('Output: ' + data.output);
        console.log(data.output)
        run(data.output)
    })
    .catch(error => console.error('Error:', error));
}

function SubmitCode() {
  const code = editor.getValue();

  fetch('/submit-code/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
      },
      body: JSON.stringify({ code:code, tool:'PY' })
  })
  .then(response => response.json())
  .then(data => {
      //  ('Output: ' + data.output);
      console.log(data.output)
      // run(data.code_extr)
      resultShow(data.output)
  })
  .catch(error => console.error('Error:', error));
}

function getCSRFToken() {
    return document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='))
        .split('=')[1];
}

function resultShow(data) {
    const resultContainer = document.getElementById('result-pane');
    resultContainer.innerHTML = ''; // Clear previous results

    const p = document.createElement('p');
    p.className = 'result-text';
    p.style.fontSize = '20px';
  
    const pre = document.createElement('pre');
    if(data['response'] == 'Correct'){ 
        p.textContent = `${data['response']} Answer!`;
        p.style.color = 'green';
        p.style.fontWeight = 'bold';
        resultContainer.appendChild(p);
    }
    else if(data['response'] == 'Incorrect'){
        p.textContent = `${data['response']} Answer!`;
        p.style.color = 'red';
        resultContainer.appendChild(p);
        pre.textContent = data['Error'];
        resultContainer.appendChild(pre);
    }
    
}

function run(data) {
    console.log(data);


    // Step 5: Create Network Data
    const container = document.getElementById('task-flow');
    container.innerHTML = `<p>${data}</P>`; 
  }

let timerInterval;
let startTime;
let elapsedTime = 0; // Time in seconds

// Function to start the timer
function startTimer() {
    startTime = Date.now() - elapsedTime * 1000; // Sync the time with previous elapsed time
    timerInterval = setInterval(updateTimer, 1000); // Update every second
}

// Function to update the timer
function updateTimer() {
    elapsedTime = Math.floor((Date.now() - startTime) / 1000); // Calculate elapsed time in seconds

    let hours = Math.floor(elapsedTime / 3600); // Get hours
    let minutes = Math.floor((elapsedTime % 3600) / 60); // Get minutes
    let seconds = elapsedTime % 60; // Get seconds

    // Format hours, minutes, and seconds to always show two digits
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = seconds < 10 ? '0' + seconds : seconds;

    // Display the timer
    document.getElementById("timer").textContent = `${hours}:${minutes}:${seconds}`;
}

// Function to stop the timer when quiz ends
function endQuiz() {
    clearInterval(timerInterval);
    alert(`Quiz ended! Time taken: ${formatTime(elapsedTime)}`);
}

// Function to format elapsed time
function formatTime(seconds) {
    let hours = Math.floor(seconds / 3600);
    let minutes = Math.floor((seconds % 3600) / 60);
    seconds = seconds % 60;
    return `${hours < 10 ? '0' + hours : hours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
}

startTimer()