const submitButton = document.getElementById("submitButton");

submitButton.addEventListener("click", async () => {

    const complaintText =
        document.getElementById("complaint").value.trim();

    const areaId =
        document.getElementById("area").value;

    const status =
        document.getElementById("status");

    const resultCard =
        document.getElementById("resultCard");


    if (!complaintText) {
        status.textContent =
            "Please describe your complaint.";

        return;
    }


    status.textContent =
        "Submitting complaint and analyzing...";

    submitButton.disabled = true;


    try {

        const response = await fetch(
            "/complaints",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    complaint_text: complaintText,
                    area_id: areaId
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Complaint submission failed."
            );
        }


        document.getElementById(
            "complaintId"
        ).textContent = data.complaint_id;


        document.getElementById(
            "problemCategory"
        ).textContent = data.problem_category;


        document.getElementById(
            "severityScore"
        ).textContent = data.severity_score;


        document.getElementById(
            "priority"
        ).textContent = data.priority;


        document.getElementById(
            "recommendation"
        ).textContent = data.recommendation;


        document.getElementById(
            "suggestedAction"
        ).textContent = data.suggested_action;


        document.getElementById(
            "reason"
        ).textContent = data.reason;


        resultCard.style.display = "block";

        status.textContent =
            "Complaint submitted successfully.";

    }

    catch (error) {

        status.textContent =
            "Error: " + error.message;

    }

    finally {

        submitButton.disabled = false;

    }

});