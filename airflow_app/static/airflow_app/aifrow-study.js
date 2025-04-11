var data = ''
var tutorials = ''
var quizQuestions = ''
let currentPage = 0;
let userAnswers = {};
let isQuizMode = false;

const urlParams = new URLSearchParams(window.location.search);
const courseId = new URLSearchParams(window.location.search).get('course_id');


document.addEventListener("DOMContentLoaded", () => {
    // Fetch course progress first
    fetch(`/get-courses/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ course_id: courseId })
    })
    .then(res => res.json())
    .then(data => { 
        current_existing_course = data[0];
        if (current_existing_course){
            currentPage = current_existing_course['chapters']-1 || 0;
            loadJSON();
        }
        else{
            updateProgress(currentPage+1)
            loadJSON();
        }
    });
});

async function loadJSON() {
    try {
        const response = await fetch(`/static/airflow_app/json_data/${courseId}.json`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        tutorials = await response.json();
        const response2 = await fetch(`/static/airflow_app/json_data/${courseId}_quiz.json`);
        if (!response2.ok) throw new Error(`HTTP error! Status: ${response2.status}`);
        quizQuestions = await response2.json();

        updateView();
        document.getElementById('prev-btn').addEventListener('click', () => {
            if (isQuizMode) {
                isQuizMode = false;
                currentPage = tutorials.length - 1;
                updateView();
            } else if (currentPage > 0) {
                currentPage--;
                updateView();
            }
        });

        document.getElementById('next-btn').addEventListener('click', () => {
            if (currentPage < tutorials.length - 1) {
                currentPage++;
                updateView();
                updateProgress(currentPage+1);
            } else if (currentPage === tutorials.length - 1) {
                isQuizMode = true;
                renderQuiz();
                document.getElementById('tutorial-container').style.display = 'none';
                document.getElementById('next-btn').style.display = 'none';
            }
        });

    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}

// document.addEventListener("DOMContentLoaded", loadJSON);

function updateProgress(pg){
    fetch('/update-progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            course_id: courseId,
            chapter: pg  
        })
        })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            console.log("Progress updated successfully.");
        } else {
            console.error("Failed to update:", data);
    }
    });

}

function updateQuiz(score){
    fetch('/update-quiz/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            course_id: courseId,
            score: score  
        })
        })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            console.log("Progress updated successfully.");
        } else {
            console.error("Failed to update:", data);
    }
    });

}



function renderLevelTracker() {
    const levelTracker = document.getElementById('level-tracker');
    levelTracker.innerHTML = '';
    for (let i = 0; i < tutorials.length; i++) {
        const circle = document.createElement('div');
        circle.classList.add('level-circle');
        if (i <= currentPage) circle.classList.add('completed');
        circle.addEventListener('click', () => {
            if (!isQuizMode && i <= currentPage) {
                currentPage = i;
                updateView();
            }
        });
        levelTracker.appendChild(circle);
    }
}

function renderTutorial() {
    document.getElementById('tutorial-container').innerHTML = `
        <h2>${tutorials[currentPage].title}</h2>
        <div>${tutorials[currentPage].content}</div>`;
    renderLevelTracker();

    Prism.highlightAll();
}

function renderQuiz() {
    const quizContainer = document.getElementById("quiz-container");
    quizContainer.innerHTML = quizQuestions.map((q, index) => `
        <div class="quiz-question">
          <h3>${index + 1}. ${q.question}</h3>
          <div class="quiz-options">
            ${q.options.map(option => `
              <div class="quiz-option" onclick="selectAnswer(${index}, this, '${option}')">${option}</div>
            `).join('')}
          </div>
        </div>
    `).join('') + `<button class="btn" id="submit-quiz">Submit Answers</button>`;
    
    quizContainer.style.display = 'block';
    document.getElementById("submit-quiz").addEventListener("click", submitQuiz);
}

function submitQuiz() {
    let score = 0;

    quizQuestions.forEach((q, index) => {
        const questionElement = document.querySelector(`.quiz-question:nth-child(${index + 1})`);
        const options = questionElement.querySelectorAll('.quiz-option');
        const selectedOption = Array.from(options).find(option => option.classList.contains('selected'));

        if (selectedOption) {
            if (selectedOption.textContent === q.answer) {
                score++;
            } else {
                selectedOption.classList.add('wrong');
            }
        }
    });

    updateQuiz(score)

    const modalOverlay = document.getElementById('modal-overlay');
    const scoreText = document.getElementById('score-text');
    scoreText.textContent = `Your Score: ${score} / ${quizQuestions.length}`;
    modalOverlay.style.display = 'flex';

    document.getElementById("submit-quiz").remove();
    document.querySelectorAll('.quiz-option').forEach(option => option.style.pointerEvents = 'none');
}

function selectAnswer(questionIndex, element, option) {
    const questionElement = element.closest('.quiz-question');
    const options = questionElement.querySelectorAll('.quiz-option');
    options.forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');
    userAnswers[questionIndex] = option;
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

function updateView() {
    if (!isQuizMode) {
        renderTutorial();
        document.getElementById('tutorial-container').style.display = 'block';
        document.getElementById('quiz-container').style.display = 'none';

        const nextBtn = document.getElementById('next-btn');
        if (currentPage === tutorials.length - 1) {
            nextBtn.textContent = 'Take Exam';
        } else {
            nextBtn.textContent = 'Next';
        }
        nextBtn.style.display = 'block';
    } else {
        document.getElementById('next-btn').style.display = 'none';
    }
}

function copyCode() {
    const codeElement = document.querySelector('pre code');
    const codeText = codeElement.innerText;
    navigator.clipboard.writeText(codeText)
        .then(() => {
            const copyButton = document.getElementById('copyButton');
            copyButton.innerText = 'Copied!';
            setTimeout(() => copyButton.innerText = 'Copy', 2000);
        })
        .catch(err => alert("Failed to copy code: " + err));
}

