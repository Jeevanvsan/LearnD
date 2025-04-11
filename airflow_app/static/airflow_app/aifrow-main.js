var existing_courses = [];

function courseOverview(user_course_data,courses,key,chapters,score){
    html= `
        <p>${courses[key]['title']}</p>
        
        <div class="progress-main">
            <span>chapters </span>
            <div class="progress-container">
                <div class="progress-bar" id="progressBar-${key}" style="width:${chapters}%"></div> 
            </div>
            <span>${chapters}% </span>

        </div>

        <div class="progress-main">
            <span>score </span>
            <div class="progress-container">
                <div class="progress-score-bar" id="progressBar-score-${key}" style="width:${score}%"></div>
            </div>
            <span>${score} / 100 </span>

        </div>
    `
    return html
}

function calculateOverallScore(totalCourses, scores) {
    const totalScore = scores.reduce((sum, score) => sum + score, 0);
    const average = totalScore / totalCourses;
    return average;
  }

fetch("/get-user-courses/")
  .then(res => res.json())
  .then(data => { 
    existing_courses = data;
    // ------------------------------------------------------------ //
    fetch('/static/airflow_app/json_data/airflow_courses.json')
        .then(response => response.json())
        .then(airflow_courses => {
            let html = '';
            let btn_text = "Start Learning";
            let chapters = 0;
            let score = 0;
            let overview_html = '';
            let totalCourses = Object.keys(airflow_courses).length;            ; 
            let scores = [];
            let chapters_list = [];
            const course_overview_div = document.getElementById("tutorial-over");
            const course_score = document.getElementById("course-score");
            const course_status = document.getElementById("course-status");

        for (const key in airflow_courses) 
            {
                    fetch(`/get-courses/`,{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            course_id: key,
                        })
                        })
                    .then(res => res.json())
                    .then(data => { 
                        current_existing_course = data[0]
                        if (current_existing_course){
                            if (current_existing_course['course_id'] = key){
                                const totalChapters = current_existing_course['total_chapters'];
                                const completedChapters = current_existing_course['chapters'];

                                const percentComplete = (completedChapters / totalChapters) * 100;
                                const roundedPercent = Math.round(percentComplete);
                                chapters = roundedPercent;
                            }
                            
                        }

                        if( existing_courses.includes(key)) {
                            airflow_courses[key]["status"] = current_existing_course['status']
                            btn_text = "Continue Learning"
                            score = current_existing_course['score']

                            overview_html += courseOverview(current_existing_course,airflow_courses,key,chapters,score)
                            
                        }
                        scores.push(score);
                        chapters_list.push(chapters);
                        course_overview_div.innerHTML = overview_html;                        
                        html += `
                            <div class="course-card">
                                <span class="level">${airflow_courses[key]["level"]}</span>
                                <span class="status">${airflow_courses[key]["status"]}</span>            
                                <h2>${airflow_courses[key]["title"]}</h2>
                                <p>${airflow_courses[key]["description"]}</p>
                                <div class="progress-circle">
                                <div class="value-chapter">Chapters:${chapters}%</div>
                                <div class="value-score">Score:${score}</div>
                                </div>
                                <a href="${airflowStudyUrl}?course_id=${key}"><button class="start-btn" id="AF-T-1-start-btn" ${airflow_courses[key]["implemented"]}>${btn_text}</button></a>
                            </div>
                            </div>
                            `

                        document.getElementById('course-pane').innerHTML = html;

                        const overall_status = calculateOverallScore(totalCourses, chapters_list);

                        const overall_score = calculateOverallScore(totalCourses, scores);
                        

                        course_status.innerHTML = `<div class="progress-main">
                            <span>Course status </span>
                            <div class="progress-container">
                                <div class="progress-bar-course-overall-status" id="progressBar-course-overall" style="width:${overall_status}%"></div> 
                            </div>
                            <span>${overall_status}% </span>

                        </div>`;

                        course_score.innerHTML = `<div class="progress-main">
                                                <span>Course score </span>
                                                <div class="progress-container">
                                                    <div class="progress-bar-course-overall" id="progressBar-course-overall" style="width:${overall_score}%"></div> 
                                                </div>
                                                <span>${overall_score}% </span>

                                            </div>`;

                    });
                
                
        }
        
          
          
    });
});



// Fetch JSON data from file
 fetch('/static/airflow_app/json_data/problems.json')
 .then(response => response.json())
 .then(problems => {
     let currentProblems = [...problems];
     let solvedProblems = [2]; // Track solved problems
     // solvedProblems.add(2)
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