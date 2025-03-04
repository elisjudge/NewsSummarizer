function createUI() {
    const appContainer = document.getElementById("app");

    const header = document.createElement("h1");
    header.textContent = "News Summary Assistant";

    const form = document.createElement("form");
    form.id = "news-form";

    const input = document.createElement("input");
    input.type = "text";
    input.id = "news-topic";
    input.placeholder = "Enter a topic...";
    input.required = true;

    const button = document.createElement("button");
    button.type = "submit";
    button.textContent = "Get Summary";

    form.appendChild(input);
    form.appendChild(button);

    const resultContainer = document.createElement("div");
    resultContainer.id = "newsSummary";
    resultContainer.textContent = "Your news summary will appear here...";

    appContainer.appendChild(header);
    appContainer.appendChild(form);
    appContainer.appendChild(resultContainer);
}

export { createUI };