
  // LOADING SCREEN HIDE FUNCTION
  function hideLoader() {
    const loader = document.getElementById('loading-screen');
    loader.style.transition = 'opacity 0.5s ease';
    loader.style.opacity = 0;
    setTimeout(() => {
      loader.style.display = 'none';
    }, 500);
  }

//   const pythonStudyUrl = "{% url 'python_study' %}";
  var existing_courses = [];
  let totalPoints = 0;

  // UTIL FUNCTIONS
  function courseOverview(user_course_data, courses, key, chapters, score) {
    return `
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
    `;
  }

  function calculateOverallScore(totalCourses, scores) {
    const totalScore = scores.reduce((sum, score) => sum + score, 0);
    return totalScore / totalCourses;
  }

  function createLevels(levelData, getUserHandson) {
    console.log("Creating levels with data:", getUserHandson);
    let completed_levels =  Object.keys(getUserHandson.task_metadata).length;
    let task_metadata =  getUserHandson.task_metadata

    const levelsContainer = document.getElementById('levels-handson');
    levelsContainer.innerHTML = '';
    let topPos = 0, leftPos = 0;

    levelData.forEach((level, index) => {
      topPos = 5 + index * 20;    
      leftPos = 20 + (index * 15) % 40; 

      if (completed_levels > 0 && index < completed_levels+1) {
        level.unlocked = true;
      }

      const levelEl = document.createElement('div');
      levelEl.className = `level-handson ${level.unlocked ? '' : 'locked'}`;
      levelEl.style.top = topPos + '%';
      levelEl.style.left = leftPos + '%';

      const circle = document.createElement('div');
      circle.className = 'level-circle';
      circle.textContent = level.id;

      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip';
      tooltip.innerHTML = `<strong>${level.title}</strong><br/>difficulty: ${level.difficulty}`;

      const starsContainer = document.createElement('div');
      starsContainer.className = 'stars-container';
      let star_count = task_metadata[level.id] ? task_metadata[level.id].statrs : 0;
      for (let i = 1; i <= 3; i++) {
        const star = document.createElement('span');
        star.className = 'star';
        star.textContent = i <= star_count ? '★' : '☆';
        starsContainer.appendChild(star);
      }

      const title = document.createElement('div');
      title.className = 'level-title';
      title.innerText = level.title;

      circle.addEventListener('click', () => {
        window.location.href = `/python-do/PY/${level.id}/`;
      });

      levelEl.appendChild(circle);
      levelEl.appendChild(tooltip);
      levelEl.appendChild(title);
      levelEl.appendChild(starsContainer);
      levelsContainer.appendChild(levelEl);
    });
  }

  // MAIN LOADING
  Promise.all([
    fetch("/get-user-courses/").then(res => res.json()),
    fetch("/get-user-handson/PY").then(res => res.json()),
    fetch("/static/python_app/json_data/python_courses.json?v=" + new Date().getTime()).then(res => res.json()),
    fetch("/static/python_app/json_data/problems.json").then(res => res.json())
  ])
  .then(([userCourses, userHandson, pythonCourses, problems]) => {
    existing_courses = userCourses;
    const course_overview_div = document.getElementById("tutorial-over");
    const course_score = document.getElementById("course-score");
    const course_status = document.getElementById("course-status");
    const totalCourses = Object.keys(pythonCourses).length;

    let html = '';
    let overview_html = '';
    let chapters_list = [];
    let scores = [];

    const courseFetches = Object.keys(pythonCourses).map(key =>
      fetch(`/get-courses/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_id: key, tool: "PY" })
      })
      .then(res => res.json())
      .then(data => {
        let chapters = 0;
        let score = 0;
        let btn_text = "Start Learning";
        const current_course = data[0];

        if (current_course && current_course['course_id'] === key) {
          const percentComplete = (current_course['chapters'] / current_course['total_chapters']) * 100;
          chapters = Math.round(percentComplete);
          score = current_course['score'];
        }

        if (existing_courses.includes(key)) {
          pythonCourses[key]["status"] = current_course['status'];
          btn_text = "Continue Learning";
          overview_html += courseOverview(current_course, pythonCourses, key, chapters, score);
        }

        scores.push(score);
        chapters_list.push(chapters);

        html += `
          <div class="course-card">
            <span class="level">${pythonCourses[key]["level"]}</span>
            <span class="status">${pythonCourses[key]["status"]}</span>
            <h2>${pythonCourses[key]["title"]}</h2>
            <p>${pythonCourses[key]["description"]}</p>
            <div class="progress-circle">
              <div class="value-chapter">Chapters:${chapters}%</div>
              <div class="value-score">Score:${score}</div>
            </div>
            <a href="${pythonStudyUrl}?course_id=${key}">
              <button class="start-btn" ${pythonCourses[key]["implemented"]}>${btn_text}</button>
            </a>
          </div>
        `;
      })
    );

    // Wait for all course POST fetches
    Promise.all(courseFetches).then(() => {
      course_overview_div.innerHTML = overview_html;
      document.getElementById('course-pane').innerHTML = html;

      const overall_status = calculateOverallScore(totalCourses, chapters_list);
      const overall_score = calculateOverallScore(totalCourses, scores);

      course_status.innerHTML = `
        <div class="progress-main">
          <span>Course status </span>
          <div class="progress-container">
            <div class="progress-bar-course-overall-status" style="width:${overall_status}%"></div> 
          </div>
          <span>${Math.round(overall_status)}% </span>
        </div>`;

      course_score.innerHTML = `
        <div class="progress-main">
          <span>Course score </span>
          <div class="progress-container">
            <div class="progress-bar-course-overall" style="width:${overall_score}%"></div> 
          </div>
          <span>${Math.round(overall_score)}% </span>
        </div>`;

      createLevels(problems, userHandson);
      hideLoader(); // ✅ All done
    });
  })
  .catch(error => {
    console.error("Loading error:", error);
    hideLoader();
  });

