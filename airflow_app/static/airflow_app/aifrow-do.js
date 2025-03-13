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
        body: JSON.stringify({ code })
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
      body: JSON.stringify({ code })
  })
  .then(response => response.json())
  .then(data => {
      //  ('Output: ' + data.output);
      console.log(data.output)
      run(data.output)
  })
  .catch(error => console.error('Error:', error));
}

function getCSRFToken() {
    return document.cookie.split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='))
        .split('=')[1];
}

function run(data) {
    console.log(data);

    // Extract tasks and dependencies from the provided data
    const tasks = data.tasks;
    const dependencies = data.dependencies;
  
    // Step 1: Create a Mapping Between Task Names and Their Original Names
    const taskNames = tasks.map(task => task.task_id);
      
    // Step 2: Create Task Name Mapping Dynamically
    const taskNameMapping = {};

    // Map dependency keys to their corresponding task names dynamically
    dependencies.forEach(dep => {
      const from = dep.from;
      const to = dep.to;

      if (!taskNameMapping[from]) taskNameMapping[from] = from;
      if (!taskNameMapping[to]) taskNameMapping[to] = to;
    });
  
    console.log("Task Name Mapping:", taskNameMapping);
  
    // Step 3: Create Nodes
    const nodes = new vis.DataSet(
      tasks.map(task => ({
        id: task.task_id,
        label: task.task_id.replace(/_/g, ' ').toUpperCase(),
        color: '#4caf50' // Default color (Green)
      }))
    );
  
    // Step 4: Create Edges Dynamically
    const edges = dependencies.map(dep => ({ from: dep.from, to: dep.to }));

    // Step 5: Create Network Data
    const container = document.getElementById('task-flow');
    const dataSet = {
      nodes: nodes,
      edges: new vis.DataSet(edges)
    };
  
    // Step 6: Configure Network Options
    const options = {
      nodes: {
        shape: 'box',
        font: { size: 14, color: '#fff' },
        margin: 5
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.7 } },
        color: { color: '#000' }
      },
      physics: {
        enabled: false,
        hierarchicalRepulsion: { nodeDistance: 400 }
      },
      layout: {
        hierarchical: {
          direction: 'LR', // Left to Right
          sortMethod: 'directed'
        }
      }
    };
  
    // Step 7: Initialize the Network
    const network = new vis.Network(container, dataSet, options);
  }