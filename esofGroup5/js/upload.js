// --- UPLOAD HANDLER ---
// Intercept the form submit so we can send the file via fetch
// instead of doing a full page reload.
document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const fileInput = document.getElementById("fileToUpload");

  // Guard: make sure the user actually picked a file before sending.
  if (!fileInput.files.length) {
    document.getElementById("status").textContent = "Please select a file.";
    return;
  }

  // FormData is the browser's built-in way to package a file
  // for a multipart POST — Flask's request.files reads this on the other end.
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  document.getElementById("status").textContent = "Uploading...";

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("status").textContent = "Error: " + data.error;
        return;
      }
      document.getElementById("status").textContent = data.message;
    })
    .catch(() => {
      document.getElementById("status").textContent =
        "Failed to connect to server. Is the Flask app running?";
    });
});
