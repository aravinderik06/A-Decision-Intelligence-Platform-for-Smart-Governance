
const trackForm = document.getElementById("track-form");
const complaintIdInput = document.getElementById("complaint-id");
const trackButton = document.getElementById("track-button");
const trackingMessage = document.getElementById("tracking-message");
const trackingResult = document.getElementById("tracking-result");

function setText(id, value) {
    document.getElementById(id).textContent =
        value === null || value === undefined || value === ""
            ? "Not available"
            : String(value);
}

function formatDate(value) {
    if (!value) return "Not available";

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? String(value)
        : date.toLocaleString();
}

function displayComplaint(data) {
    setText("result-id", data.complaint_id);
    setText("result-date", formatDate(data.complaint_date));
    setText("result-area", data.area_id);
    setText("result-status", data.status);
    setText("result-category", data.problem_category);
    setText("result-priority", data.priority);

    setText(
        "result-severity",
        data.severity_score === null || data.severity_score === undefined
            ? "Not available"
            : `${Number(data.severity_score).toFixed(2)} / 100`
    );

    setText("result-recommendation", data.recommendation);
    setText("result-action", data.suggested_action);
    setText("result-decision", data.officer_decision);
    setText("result-remarks", data.officer_reason);
    setText("result-decision-date", formatDate(data.decision_date));

    trackingResult.classList.remove("hidden");
}

trackForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const complaintId = complaintIdInput.value.trim();

    if (!/^[1-9]\d*$/.test(complaintId)) {
        trackingMessage.textContent =
            "Please enter a valid positive complaint ID.";
        trackingMessage.classList.add("tracking-error");
        trackingResult.classList.add("hidden");
        return;
    }

    trackButton.disabled = true;
    trackingMessage.classList.remove("tracking-error");
    trackingMessage.textContent = "Looking up your complaint...";
    trackingResult.classList.add("hidden");

    try {
        const response = await fetch(
            `/complaints/${encodeURIComponent(complaintId)}/track`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to retrieve the complaint."
            );
        }

        displayComplaint(data);
        trackingMessage.textContent =
            "Complaint details retrieved successfully.";

    } catch (error) {
        trackingMessage.textContent = error.message;
        trackingMessage.classList.add("tracking-error");

    } finally {
        trackButton.disabled = false;
    }
});
