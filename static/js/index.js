import { createUI } from "./ui.js";

async function fetchNewsSummary(topic) {
    try {
        const response = await fetch('/api/get_news_summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("✅ API Response:", data); 

        if (!data.summary || !data.citations) {
            console.error("🚨 API Response is missing required fields!", data);
            document.getElementById("newsSummary").innerHTML = "<p>Error: Incomplete API response.</p>";
            return;
        }
        
        let summaryHtml = `<p>${data.summary}</p><h3>Sources:</h3><ul>`;
        data.citations.forEach(cite => {
            summaryHtml += `<li><strong>${cite.intextCitation}:</strong> <a href="${cite.link}" target="_blank">${cite.articleName}</a></li>`;
        });
        summaryHtml += "</ul>";
        
        document.getElementById("newsSummary").innerHTML = summaryHtml;

    } catch (error) {
        console.error("🚨 Error fetching news summary:", error);
        document.getElementById("newsSummary").innerHTML = "<p>Failed to fetch news. Please try again.</p>";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    createUI();
    const form = document.getElementById("news-form");
    
    if (form) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const topicInput = document.getElementById("news-topic");
            if (topicInput.value.trim()) {
                fetchNewsSummary(topicInput.value.trim());
            }
        });
    }
});