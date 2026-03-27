// Holds the full questions data (including options) after load.
// Keyed by question text, same structure as Flask's /questions response.
let questionsData = {};

// Load questions from the server on page load.
fetch("/questions")
  .then((res) => res.json())
  .then((data) => {
    questionsData = data;
    populateQuestionDropdown(data);
  })
  .catch(() => {
    // No questions yet (no CSV uploaded) - silently do nothing.
  });

// Fills the question <select> with one <option> per question.
function populateQuestionDropdown(data) {
  const select = document.getElementById("questionSelect");
  select.innerHTML = '<option value="">-- Choose a question --</option>';

  Object.keys(data).forEach(function (q) {
    const option = document.createElement("option");
    option.value = q;
    // Truncate long question text so the dropdown stays readable.
    option.textContent = q.length > 80 ? q.substring(0, 80) + "..." : q;
    select.appendChild(option);
  });
}

// --- QUESTION SELECTION HANDLER ---
document
  .getElementById("questionSelect")
  .addEventListener("change", function () {
    const selected = this.value;

    if (!selected) {
      document.getElementById("question-detail").style.display = "none";
      return;
    }

    const question = questionsData[selected];

    // Show the full question text as a heading.
    document.getElementById("question-heading").textContent = selected;

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
  });

// --- TYPE SELECTION HANDLER ---
// Recalculates and displays stats whenever the user changes the type dropdown.
document.getElementById("typeSelect").addEventListener("change", function () {
  const type = this.value;
  const question = document.getElementById("questionSelect").value;

  if (!type || !question) {
    document.getElementById("stats-section").style.display = "none";
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

      statsOutput.innerHTML =
        `<p>Responses counted: ${numbers.length}</p>` +
        `<p>Mean: ${mean.toFixed(2)}</p>` +
        `<p>Median: ${median}</p>` +
        `<p>Mode: ${mode}</p>`;
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
  } else if (type === "short_answer") {
    // Free text — can't do numeric stats, just show the response count.
    statsOutput.innerHTML =
      `<p>Responses counted: ${responses.length}</p>` +
      "<p>Mean / median / mode are not applicable for short answer questions.</p>";
  }

  document.getElementById("stats-section").style.display = "block";
});

// --- SAVE TYPE HANDLER ---
document.getElementById("saveTypeBtn").addEventListener("click", function () {
  const question = document.getElementById("questionSelect").value;
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
