
/* =========================================================
   SMART GOVERNANCE - OFFICER DASHBOARD
   Connects the dashboard UI to the FastAPI backend.
   ========================================================= */

// 1. SESSION AND PAGE ELEMENTS
// =========================================================

const token = sessionStorage.getItem("officer_token");
const storedOfficer = sessionStorage.getItem("officer_details");

const officerName = document.getElementById("officer-name");
const officerDepartment = document.getElementById("officer-department");
const totalCount = document.getElementById("total-count");
const criticalCount = document.getElementById("critical-count");
const highCount = document.getElementById("high-count");
const pendingCount = document.getElementById("pending-count");
const complaintList = document.getElementById("complaint-list");
const pageMessage = document.getElementById("page-message");
const priorityFilter = document.getElementById("priority-filter");

const dialog = document.getElementById("complaint-dialog");
const detailTitle = document.getElementById("detail-title");
const detailContent = document.getElementById("detail-content");
const decisionForm = document.getElementById("decision-form");
const decisionMessage = document.getElementById("decision-message");
const decisionComplaintId = document.getElementById(
    "decision-complaint-id"
);
const officerReason = document.getElementById("officer-reason");

let complaints = [];
let selectedComplaint = null;


// 2. SAFE HTML HELPERS
// =========================================================

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}

function formatNumber(value, digits = 1) {
    const number = Number(value);

    return Number.isFinite(number)
        ? number.toFixed(digits)
        : "N/A";
}

function priorityClass(priority) {
    const value = String(priority || "").toLowerCase();

    if (value === "critical") return "priority-critical";
    if (value === "high") return "priority-high";
    if (value === "medium") return "priority-medium";
    if (value === "low") return "priority-low";

    return "";
}

function formatDate(value) {
    if (!value) return "N/A";

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? String(value)
        : date.toLocaleString();
}

function isFinalStatus(status) {
    return [
        "Approved by Officer",
        "Modified by Officer",
        "Rejected by Officer"
    ].includes(status);
}


// 3. AUTHENTICATED API REQUEST HELPER
// =========================================================

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`,
            ...(options.body
                ? { "Content-Type": "application/json" }
                : {})
        }
    });

    const contentType = response.headers.get("content-type") || "";

    const data = contentType.includes("application/json")
        ? await response.json()
        : {};

    if (response.status === 401) {
        sessionStorage.removeItem("officer_token");
        sessionStorage.removeItem("officer_details");

        window.location.replace("/officer-login");

        throw new Error("Your session has expired. Please sign in again.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || "The request failed."
        );
    }

    return data;
}


// 4. CHECK LOGIN SESSION
// =========================================================

if (!token || !storedOfficer) {
    window.location.replace("/officer-login");
} else {
    try {
        const officer = JSON.parse(storedOfficer);

        officerName.textContent = officer.name || "Officer";
        officerDepartment.textContent =
            officer.department || "Department not available";

        loadComplaints();
    } catch {
        sessionStorage.removeItem("officer_token");
        sessionStorage.removeItem("officer_details");
        window.location.replace("/officer-login");
    }
}


// 5. LOAD DEPARTMENT COMPLAINTS
// =========================================================

async function loadComplaints() {
    pageMessage.textContent = "Loading department complaints...";

    try {
        const data = await apiRequest("/officer/complaints");

        complaints = Array.isArray(data.complaints)
            ? data.complaints
            : [];

        if (data.officer) {
            officerName.textContent = data.officer.name;
            officerDepartment.textContent = data.officer.department;
        }

        updateSummary();
        renderComplaints();

        pageMessage.textContent = complaints.length
            ? `${complaints.length} complaint(s) assigned to your department.`
            : "No complaints are currently assigned to your department.";

    } catch (error) {
        pageMessage.textContent = error.message;
        complaintList.replaceChildren();
    }
}


// 6. UPDATE DASHBOARD SUMMARY
// =========================================================

function updateSummary() {
    totalCount.textContent = complaints.length;

    criticalCount.textContent = complaints.filter(
        item => String(item.priority).toLowerCase() === "critical"
    ).length;

    highCount.textContent = complaints.filter(
        item => String(item.priority).toLowerCase() === "high"
    ).length;

    pendingCount.textContent = complaints.filter(
        item => !isFinalStatus(item.status)
    ).length;
}


// 7. RENDER COMPLAINT CARDS
// =========================================================

function renderComplaints() {
    const selectedPriority = priorityFilter.value;

    const filtered = complaints.filter(item => {
        return selectedPriority === "All"
            || item.priority === selectedPriority;
    });

    complaintList.replaceChildren();

    if (filtered.length === 0) {
        const emptyMessage = document.createElement("p");

        emptyMessage.className = "message";
        emptyMessage.textContent =
            "No complaints match the selected priority.";

        complaintList.appendChild(emptyMessage);
        return;
    }

    filtered.forEach(complaint => {
        const card = document.createElement("article");

        card.className = "complaint-card";

        const header = document.createElement("div");
        header.className = "complaint-card-header";

        const titleBlock = document.createElement("div");

        const title = document.createElement("h3");
        title.textContent = `Complaint #${complaint.complaint_id}`;

        const date = document.createElement("p");
        date.className = "muted";
        date.textContent = formatDate(complaint.complaint_date);

        titleBlock.append(title, date);

        const priority = document.createElement("span");
        priority.className =
            `pill ${priorityClass(complaint.priority)}`;
        priority.textContent = complaint.priority || "Unclassified";

        header.append(titleBlock, priority);

        const preview = document.createElement("p");
        preview.className = "complaint-preview";
        preview.textContent = complaint.complaint_text || "";

        const meta = document.createElement("div");
        meta.className = "complaint-meta";

        const category = document.createElement("span");
        category.className = "pill";
        category.textContent =
            complaint.problem_category || "Uncategorized";

        const area = document.createElement("span");
        area.className = "pill";
        area.textContent = complaint.area_id || "Unknown area";

        const status = document.createElement("span");
        status.className = "pill";
        status.textContent = complaint.status || "Unknown status";

        meta.append(category, area, status);

        const footer = document.createElement("div");
        footer.className = "card-footer";

        const severity = document.createElement("span");
        severity.className = "muted";
        severity.textContent =
            `AI severity: ${formatNumber(complaint.severity_score)}/100`;

        const viewButton = document.createElement("button");
        viewButton.className = "button button-primary";
        viewButton.textContent = "Review complaint";

        viewButton.addEventListener("click", () => {
            openComplaintDetails(complaint.complaint_id);
        });

        footer.append(severity, viewButton);

        card.append(header, preview, meta, footer);
        complaintList.appendChild(card);
    });
}


// 8. DISPLAY COMPLAINT DETAILS AND SHAP
// =========================================================

function openComplaintDetails(complaintId) {
    selectedComplaint = complaints.find(
        item => item.complaint_id === complaintId
    );

    if (!selectedComplaint) return;

    const item = selectedComplaint;

    detailTitle.textContent = `Complaint #${item.complaint_id}`;
    decisionComplaintId.value = item.complaint_id;
    officerReason.value = "";
    decisionMessage.textContent = "";

    const shap = Array.isArray(item.shap_explanation)
        ? item.shap_explanation
        : [];

    const shapHtml = shap.length
        ? shap.map(factor => {
            let feature = "Feature";
            let contribution = "N/A";

            if (factor && typeof factor === "object") {
                feature = factor.feature
                    ?? factor.name
                    ?? factor.label
                    ?? "Feature";

                const rawValue = factor.contribution
                    ?? factor.shap_value
                    ?? factor.impact
                    ?? factor.value;

                contribution = rawValue === undefined
                    ? "N/A"
                    : formatNumber(rawValue, 3);
            } else {
                feature = String(factor);
            }

            return `
                <div class="shap-row">
                    <span>${escapeHtml(feature)}</span>
                    <span class="shap-value">
                        ${escapeHtml(contribution)}
                    </span>
                </div>
            `;
        }).join("")
        : "<p>No SHAP explanation is available for this complaint.</p>";

    detailContent.innerHTML = `
        <section class="detail-section">
            <h3>Citizen complaint</h3>
            <p>${escapeHtml(item.complaint_text)}</p>
            <p class="muted">
                Area: ${escapeHtml(item.area_id || "N/A")}
                · Submitted: ${escapeHtml(formatDate(item.complaint_date))}
            </p>
        </section>

        <section class="detail-section">
            <h3>AI assessment</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <small>Problem category</small>
                    <strong>${escapeHtml(item.problem_category || "N/A")}</strong>
                </div>
                <div class="detail-item">
                    <small>Classification confidence</small>
                    <strong>${escapeHtml(
                        formatNumber(
                            Number(item.classification_confidence) * 100
                        )
                    )}%</strong>
                </div>
                <div class="detail-item">
                    <small>Severity score</small>
                    <strong>${escapeHtml(
                        formatNumber(item.severity_score)
                    )}/100</strong>
                </div>
                <div class="detail-item">
                    <small>Priority</small>
                    <strong>${escapeHtml(item.priority || "N/A")}</strong>
                </div>
                <div class="detail-item">
                    <small>Current status</small>
                    <strong>${escapeHtml(item.status || "N/A")}</strong>
                </div>
                <div class="detail-item">
                    <small>Department</small>
                    <strong>${escapeHtml(
                        item.assigned_department || "N/A"
                    )}</strong>
                </div>
            </div>
        </section>

        <section class="detail-section">
            <h3>AI recommendation</h3>
            <p><strong>Recommendation:</strong>
                ${escapeHtml(item.recommendation || "N/A")}
            </p>
            <p><strong>Suggested action:</strong>
                ${escapeHtml(item.suggested_action || "N/A")}
            </p>
            <p><strong>Rationale:</strong>
                ${escapeHtml(item.reason || "N/A")}
            </p>
        </section>

        <section class="detail-section">
            <h3>SHAP explanation</h3>
            <p class="muted">
                Feature contributions explain the model's severity prediction.
                Positive values increase the prediction relative to the baseline;
                negative values decrease it.
            </p>
            <div class="shap-list">${shapHtml}</div>
        </section>
    `;

    const alreadyDecided = isFinalStatus(item.status);

    decisionForm.querySelectorAll("[data-decision]").forEach(button => {
        button.disabled = alreadyDecided;
    });

    officerReason.disabled = alreadyDecided;

    if (alreadyDecided) {
        decisionMessage.textContent =
            "A decision has already been recorded for this complaint.";
    }

    dialog.showModal();
}


// 9. SUBMIT OFFICER DECISION
// =========================================================

decisionForm.querySelectorAll("[data-decision]").forEach(button => {
    button.addEventListener("click", async () => {
        if (!selectedComplaint) return;

        const decision = button.dataset.decision;
        const complaintId = Number(decisionComplaintId.value);

        const confirmed = window.confirm(
            `Confirm ${decision.toLowerCase()} for complaint #${complaintId}?`
        );

        if (!confirmed) return;

        decisionMessage.textContent = "Saving your decision...";

        decisionForm.querySelectorAll("[data-decision]").forEach(item => {
            item.disabled = true;
        });

        try {
            const result = await apiRequest("/officer/decisions", {
                method: "POST",
                body: JSON.stringify({
                    complaint_id: complaintId,
                    decision,
                    officer_reason: officerReason.value.trim()
                })
            });

            decisionMessage.textContent = result.message
                || "Decision saved successfully.";

            await loadComplaints();

            const updatedComplaint = complaints.find(
                item => item.complaint_id === complaintId
            );

            if (updatedComplaint) {
                openComplaintDetails(complaintId);
            } else {
                dialog.close();
            }

        } catch (error) {
            decisionMessage.textContent = error.message;

            decisionForm.querySelectorAll("[data-decision]").forEach(item => {
                item.disabled = false;
            });
        }
    });
});


// 10. DASHBOARD CONTROLS
// =========================================================

priorityFilter.addEventListener("change", renderComplaints);

document.getElementById("refresh-button").addEventListener(
    "click",
    loadComplaints
);

document.getElementById("close-dialog").addEventListener(
    "click",
    () => dialog.close()
);

document.getElementById("logout-button").addEventListener(
    "click",
    () => {
        sessionStorage.removeItem("officer_token");
        sessionStorage.removeItem("officer_details");

        window.location.replace("/officer-login");
    }
);
