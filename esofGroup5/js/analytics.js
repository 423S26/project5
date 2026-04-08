/* global Chart */

// Holds the full questions data (including options) after load.
// Keyed by question text, same structure as Flask's /questions response.
let questionsData = {};

// Tracks the current Chart.js instance so we can destroy it before re-rendering.
let activeChart = null;

let current_question = "";

function renderChart(type, labels, values) {
  const canvas = document.getElementById("stats-chart");
  if (activeChart) {
    activeChart.destroy();
    activeChart = null;
  }
  const isBar = type === "bar";
  activeChart = new Chart(canvas, {
    type: isBar ? "bar" : "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            "#4e79a7",
            "#f28e2b",
            "#e15759",
            "#76b7b2",
            "#59a14f",
            "#edc948",
            "#b07aa1",
            "#ff9da7",
          ],
        },
      ],
    },
    options: {
      plugins: { legend: { display: !isBar } },
      scales: isBar ? { y: { beginAtZero: true, ticks: { stepSize: 1 } } } : {},
    },
  });
}

// Load questions from the server on page load.
fetch("/questions")
  .then((res) => res.json())
  .then((data) => {
    questionsData = data;
    fillQuestionBoxes(data);
  })
  .catch(() => {
    // No questions yet (no CSV uploaded) - silently do nothing.
  });

//------------QUESTION BOXES VISUALISZATION-------------------------
function fillQuestionBoxes(data) {
  const parent_container = document.getElementById("question_boxes");
  parent_container.innerHTML = "";
  Object.keys(data).forEach(function (q) {
    // For each data entry q (Question Name)
    const child_box = document.createElement("div");
    child_box.classList.add("question_box");
    child_box.textContent = q;
    child_box.addEventListener("click", function(){update_question(data, q);});
    parent_container.append(child_box);
  });
}

// ------------UPDATE QUESTION--------------------------------------------
function update_question(data,q){
  // if (!selected) {
  //   document.getElementById("question-detail").style.display = "none";
  //   return;
  // }

  const question = questionsData[q];
  current_question = q;

  // Show the full question text as a heading.
  document.getElementById("question-heading").textContent = q;

  // Show up to 5 non-empty responses as a preview.
  const previewList = document.getElementById("response-preview");
  previewList.innerHTML = "";

  const nonEmpty = question.options.filter((r) => r.trim() !== "");
  const preview = nonEmpty.slice(0, 5); 

  if (preview.length === 0) {
    const li = document.createElement("li");
    li.textContent = "(no responses recorded)";
    previewList.appendChild(li);
  } else {
    preview.forEach(function (response) {
      const li = document.createElement("li");
      li.textContent = response;
      previewList.appendChild(li);
    });
    
    
  }

  // Pre-select the detected/saved type and clear old status.
  document.getElementById("typeSelect").value = question.type || "";
  document.getElementById("saveStatus").textContent = "";

  document.getElementById("question-detail").style.display = "block";

  // If a type is already set, render stats immediately without requiring
  // the user to manually re-select it.
  document.getElementById("typeSelect").dispatchEvent(new Event("change"));

  // Trigger Change to update information
  

  // Window Scroll To section
  const section = document.getElementById("question-detail");

  section.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
  // generateGraph(q);
}

// ------------QUESTION SEARCH---------------------------------------------------------
document.getElementById("question_search").addEventListener('input', function(){
  filter();
  // const val = document.getElementById("question_search").value.toLowerCase();


  //   const new_data = Object.fromEntries(
  //     Object.entries(questionsData).filter(([key, value]) => {
  //       return key.toLowerCase().includes(val);
  //     }),
  //   );

  //   fillQuestionBoxes(new_data);
  });
// ------------SELECT BY QUESTION TYPE--------------------------------------------

document.getElementById("sort_by_category").addEventListener('change', function(){
  filter();
  // const type_search = document.getElementById("sort_by_category").value.toLowerCase();
  // const search_val = document.getElementById("question_search").value.toLowerCase();

  // if(type_search != 'none'){
  //   const keys = Object.keys(questionsData);
  //   const new_data = Object.fromEntries(
  //     Object.entries(questionsData).filter(([key, value]) => {
  //       return (questionsData[key].type == type_search) && (key.toLowerCase().includes(search_val));
  //     })
  //   );
  //   fillQuestionBoxes(new_data);
  // }else{
  //   fillQuestionBoxes(questionsData);
  // }
  
});

function filter(){
  const type_search = document.getElementById("sort_by_category").value.toLowerCase();
  const search_val = document.getElementById("question_search").value.toLowerCase();

  if(type_search != 'none'){
    // Filter by category AND search
    const new_data = Object.fromEntries(
      Object.entries(questionsData).filter(([key]) => {
        return (questionsData[key].type == type_search) && (key.toLowerCase().includes(search_val));
      })
    );
    fillQuestionBoxes(new_data);
  }else{
    // Filter only by search
    const new_data = Object.fromEntries(
      Object.entries(questionsData).filter(([key]) => {
        return (key.toLowerCase().includes(search_val));
      })
    );
    fillQuestionBoxes(new_data);
  }
}


// ---- GENERATE GRAPH--------------------------------------------------------

function generateGraph(){
  const type = document.getElementById("typeSelect").value;
  const question = current_question;
  
  if (!type || !question) {
    document.getElementById("stats-section").style.display = "none";
    if (activeChart) {
      activeChart.destroy();
      activeChart = null;
    }
    return;
  }

  const responses = questionsData[question].options.filter(
    (r) => r.trim() !== "",
  );
  const statsOutput = document.getElementById("stats-output");
  statsOutput.innerHTML = "";

  const numericTypes = ["likert", "ranking"];

  if (numericTypes.includes(type)) {
    // Parse responses as numbers, drop anything that isn't a valid number.
    const numbers = responses
      .map((r) => parseFloat(r))
      .filter((n) => !isNaN(n));

    if (numbers.length === 0) {
      statsOutput.textContent = "No numeric responses found.";
    } else {
      // Mean: sum divided by count.
      const mean = numbers.reduce((a, b) => a + b, 0) / numbers.length;

      // Median: sort then pick the middle value.
      const sorted = [...numbers].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      const median =
        sorted.length % 2 !== 0
          ? sorted[mid]
          : (sorted[mid - 1] + sorted[mid]) / 2;

      // Mode: tally each value, pick the one with the highest count.
      const freq = {};
      numbers.forEach((n) => (freq[n] = (freq[n] || 0) + 1));
      const mode = Object.entries(freq).sort((a, b) => b[1] - a[1])[0][0];
      const standard_deviation = getStandardDeviation(numbers);

      statsOutput.innerHTML =
        `<p>Responses counted: ${numbers.length}</p>` +
        `<p>Mean: ${mean.toFixed(2)}</p>` +
        `<p>Median: ${median}</p>` +
        `<p>Mode: ${mode}</p>` +
        `<p>Standard Deviation: ${standard_deviation}</p>`;

      // Bar chart of value distribution.
      const chartFreq = {};
      numbers.forEach((n) => (chartFreq[n] = (chartFreq[n] || 0) + 1));
      const chartEntries = Object.entries(chartFreq).sort(
        (a, b) => a[0] - b[0],
      );
      renderChart(
        "bar",
        chartEntries.map((e) => e[0]),
        chartEntries.map((e) => e[1]),
      );
    }
  } else if (type === "multiple_choice" || type === "yes_no") {
    // For categorical questions, show a frequency table and the mode.
    const freq = {};
    responses.forEach((r) => (freq[r] = (freq[r] || 0) + 1));

    // Sort by count descending so the most common answer is first.
    const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
    const mode = sorted[0][0];

    let html = `<p>Responses counted: ${responses.length}</p>`;
    html += `<p>Most common: "${mode}"</p>`;
    html +=
      '<table border="1" cellpadding="4"><tr><th>Answer</th><th>Count</th></tr>';
    sorted.forEach(([answer, count]) => {
      html += `<tr><td>${answer}</td><td>${count}</td></tr>`;
    });
    html += "</table>";
    statsOutput.innerHTML = html;

    // Pie chart of answer distribution.
    renderChart(
      "pie",
      sorted.map((e) => e[0]),
      sorted.map((e) => e[1]),
    );
  } else if (type === "short_answer") {
    // Free text — can't do numeric stats, just show the response count.
    statsOutput.innerHTML =
      `<p>Responses counted: ${responses.length}</p>` +
      "<p>Mean / median / mode are not applicable for short answer questions.</p>";
    // Destroy any previous chart — nothing to graph for free text.
    if (activeChart) {
      activeChart.destroy();
      activeChart = null;
    }
  }

  document.getElementById("stats-section").style.display = "block";
}


document.getElementById("typeSelect").addEventListener("change", function () {
  // Recalculates and displays stats whenever the user changes the type dropdown.
  generateGraph();
});

// --- SAVE TYPE HANDLER ---
document.getElementById("saveTypeBtn").addEventListener("click", function () {
  const question = current_question;
  const type = document.getElementById("typeSelect").value;

  if (!type) {
    document.getElementById("saveStatus").textContent =
      " Please select a type.";
    return;
  }

  fetch("/questions/set-type", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question, type: type }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("saveStatus").textContent =
          " Error: " + data.error;
        return;
      }
      // Update local copy so the pre-select works if they revisit this question.
      questionsData[question].type = type;
      document.getElementById("saveStatus").textContent = " Saved!";
    })
    .catch(() => {
      document.getElementById("saveStatus").textContent = " Failed to save.";
    });
});

var download_link = document.getElementById("chart_download");
download_link.addEventListener("click", function(){
  // alert(current_question);
  download_link.setAttribute("download", `${current_question}.png`);
  const canvas = document.getElementById("stats-chart");
  var image = canvas.toDataURL("image/png").replace("image/png","imageoctet-stream");

  download_link.setAttribute("href", image);
});


// Calculate Standard Deviation
function getStandardDeviation(array) {
  const n = array.length;
  const mean = array.reduce((a, b) => a + b) / n;
  return Math.sqrt(
    array.map((x) => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n,
  );
}
