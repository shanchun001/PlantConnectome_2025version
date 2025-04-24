document.addEventListener("DOMContentLoaded", function () {
  // Your code here
  document
    .getElementById("chat-form")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      let userInput = document.getElementById("user-input");
      let loadingDiv = document.getElementById("loading");
      let warningDiv = document.getElementById("warning");
      if (userInput.value === "") {
        userInput.value = "CESA1";
      }
      let url = `/tldr/search?user_input=${encodeURIComponent(
        userInput.value
      )}`;
      document.getElementById("submitBtn").setAttribute("disabled", "disabled");
      loadingDiv.style.display = "block";
      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          let content = data.content;
          let warning = data.warning;
          if (warning !== "") {
            warningDiv.style.display = "block";
            warningDiv.innerHTML = "<p>" + warning + "</p>";
          } else {
            warningDiv.style.display = "none";
          }
          let resultDiv = document.getElementById("result");
          const regex = /\((\d+(?:, ?\d+)*)\)/g;
          const formattedContent = content.replace(regex, (match, numbers) => {
            const numberArray = numbers
              .split(", ")
              .map(
                (number) =>
                  `<a href="http://www.ncbi.nlm.nih.gov/pubmed/${number}" target="_blank">${number}</a>`
              );
            return `(${numberArray.join(", ")})`;
          });
          resultDiv.innerHTML = formattedContent;
          document.getElementById("submitBtn").removeAttribute("disabled");
          loadingDiv.style.display = "none";
        })
        .catch((error) => {
          console.error("Error fetching response:", error);
          document.getElementById("submitBtn").removeAttribute("disabled");
          loadingDiv.style.display = "none";
        });
    });
});
