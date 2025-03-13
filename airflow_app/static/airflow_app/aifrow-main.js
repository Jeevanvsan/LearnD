 // Fetch JSON data from file
 fetch('/static/airflow_app/problems.json')
 .then(response => response.json())
 .then(problems => {
     let currentProblems = [...problems];
     let solvedProblems = [2]; // Track solved problems
     // solvedProblems.add(2)
     console.log(solvedProblems)
     function renderProblems(problems) {
         const problemCards = document.getElementById('problem-cards');
         problemCards.innerHTML = '';
         problems.forEach(problem => {
             const card = document.createElement('div');
             card.className = 'card';

             // Check if the problem is solved
             const isSolved = solvedProblems.includes(problem.id); // Assume `solvedProblems` tracks solved IDs

             // Add Completed badge if solved
             const badge = isSolved ? `<div class="completed-badge">Completed</div>` : '';

            

             card.innerHTML = `
                 ${badge}
                 <h3>${problem.title}</h3>
                 <div class="content">
                     <p>${problem.question}</p>
                     <span>Difficulty: <span style="font-weight: bold;font-size:15px">${problem.difficulty}</span>, Max Score: ${problem.max_score}</span>
                 </div>
                 <button onclick="window.location.href='/airflow-do/${ problem.id }/'">Solve Problem</button>
             `;
             problemCards.appendChild(card);
         });
     }

     window.solveProblem = function (id) {
         // Mark the problem as solved
        //  solvedProblems.add(id);

         // Re-render the cards to reflect the updated status
         renderProblems(currentProblems);
     };

     document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
         radio.addEventListener('change', () => {
             const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked')?.value;
             const filteredProblems = selectedDifficulty 
                 ? problems.filter(problem => problem.difficulty === selectedDifficulty) 
                 : problems;
             currentProblems = filteredProblems;
             renderProblems(filteredProblems);
         });
     });

     document.getElementById('sortAsc').addEventListener('click', () => {
         currentProblems.sort((a, b) => a.difficulty.localeCompare(b.difficulty));
         renderProblems(currentProblems);
     });

     document.getElementById('sortDesc').addEventListener('click', () => {
         currentProblems.sort((a, b) => b.difficulty.localeCompare(a.difficulty));
         renderProblems(currentProblems);
     });

     renderProblems(problems);
 })
 .catch(error => console.error('Error loading problems:', error));