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
    createLevels(problems);

     
 })
 .catch(error => console.error('Error loading problems:', error));



let totalPoints = 0;

// Create level nodes
function createLevels(levelData) {
    const levelsContainer = document.getElementById('levels-handson');
    levelsContainer.innerHTML = ''; // Clear existing levels
    // position: { top: '15%', left: '50%' },

    topPos = 0
    leftPos = 0


    levelData.forEach((level, index) => {
        topPos = 5 + index * 20;     // Start from 10% and increase 12% per level
        leftPos = 20 + (index * 15) % 40; // Keep left within 0–80% range
        
        console.log(`level-handson ${level.id}: top=${topPos}%, left=${leftPos}%`);

        const levelEl = document.createElement('div');
        levelEl.className = `level-handson ${level.unlocked ? '' : 'locked'}`;

        if(index == 0){
            levelEl.className = `level-handson `;

        }
        levelEl.style.top = topPos+'%';
        levelEl.style.left = leftPos+'%';

        // Circle
        const circle = document.createElement('div');
        circle.className = 'level-circle';
        circle.textContent = level.id;

        // Tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.innerHTML = `<strong>${level.title}</strong><br/>difficulty: ${level.difficulty}`;

        // Stars
        const stars = document.createElement('div');
        stars.className = 'stars';
        stars.innerText = level.title;

        // Add click event listener to all levels
        circle.addEventListener('click', () => {
            window.location.href = `/airflow-do/${level.id}/`;

            // if (level.unlocked) {
            //     // If the level is unlocked, prompt the user with the question
            //     const userAnswer = prompt(level.question);
            //     if (userAnswer && userAnswer.toLowerCase().trim() === level.answer.toLowerCase()) {
            //         alert('Correct!');
            //         totalPoints += level.points;
            //         document.querySelector('.score span').textContent = totalPoints;
            //     } else {
            //         alert('Incorrect!');
            //     }
            // } else {

            //     // If the level is locked, notify the user
            //     alert(`Level ${level.id} (${level.name}) is locked. Complete previous levels to unlock it.`);
            // }
        });

        // Append elements
        levelEl.appendChild(circle);
        levelEl.appendChild(tooltip);
        levelEl.appendChild(stars);
        levelsContainer.appendChild(levelEl);
    });
}
                
function handleLevelClick(levelId) {
    const level = levelData.find(l => l.id === levelId);
    if (!level || !level.unlocked) return;

    const answer = prompt(`${level.name}\n\nQuestion: ${level.question}`);
    if (answer === null) return; // User cancelled

    if (answer.toLowerCase() === level.answer.toLowerCase()) {
    alert(`Correct! You earned ${level.points} points!`);
    totalPoints += level.points;

    level.paths.forEach(nextLevelId => {
        const nextLevel = levelData.find(l => l.id === nextLevelId);
        if (nextLevel) {
        nextLevel.unlocked = true;
        }
    });

    createLevels();
} else {
alert('Incorrect answer. Try again!');
}
}

// Initialize the map