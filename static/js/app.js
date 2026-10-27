/**
 * Societal Innovation Collaboration Platform - Frontend JavaScript
 * Handles tab navigation, Chart.js analytics, dynamic API calls,
 * university workflows, CSR pledges, and AI Viva Inspector.
 */

// Global State
let allProblems = [];
let allSolutions = [];
let allUniversities = [];
let allLocations = [];
let domainChartInstance = null;
let priorityChartInstance = null;
let vivaProbChartInstance = null;

// Presets for the Viva Inspector
const VIVA_PRESETS = {
  water: {
    title: "Groundwater Fluoride Contamination in Palamu",
    desc: "High fluoride levels in borewell drinking water (>3.5 mg/L) causing dental and skeletal fluorosis among rural children in Palamu district. Need community water filtration plant.",
    state: "Jharkhand",
    district: "Palamu",
    urgency: "Critical"
  },
  agri: {
    title: "Paddy crop fungal blight outbreak in Bero block",
    desc: "Rice harvest is turning brown with fungal leaf blast. Smallholder tribal farmers face severe crop loss and debt without rapid remedy.",
    state: "Jharkhand",
    district: "Ranchi",
    urgency: "High"
  },
  health: {
    title: "Sickle Cell Disease Diagnostic Lag in Santhal Pargana",
    desc: "Tribal children in remote villages of Deoghar and Dumka suffer chronic pain, anemia and early mortality due to delayed sickle cell screening.",
    state: "Jharkhand",
    district: "Deoghar",
    urgency: "Critical"
  },
  edu: {
    title: "Adolescent Tribal Girl School Dropouts due to Sanitation Deficit",
    desc: "In government Kasturba Gandhi Balika Vidyalaya in Torpa block, lack of regular running water supply and broken latrines has caused an alarming 40% absentee rate during menstrual cycles.",
    state: "Jharkhand",
    district: "Khunti",
    urgency: "High"
  },
  env: {
    title: "Thermal Fly Ash Runoff and Dust Pollution in Bokaro Periphery",
    desc: "Fly ash ponds near power generation units are overflowing into surrounding farmlands and breathing air. Heavy metals contaminating local drinking wells.",
    state: "Jharkhand",
    district: "Bokaro",
    urgency: "High"
  },
  jk: {
    title: "Flash Flood Risk and Severe Siltation in Jhelum River Catchment",
    desc: "Early monsoon cloudburst and heavy silt accumulation threatening river embankments and low-lying apple orchards in Srinagar and Anantnag. Urgent need for automated early warning flood telemetry sensors.",
    state: "Jammu and Kashmir",
    district: "Srinagar",
    urgency: "Critical"
  }
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  await loadLocations();
  await loadUniversities();
  await refreshDashboard();
  setupLiveInputWatcher();
});

// Nationwide Location Loader & Dynamic Linking
async function loadLocations() {
  try {
    const res = await fetch("/api/locations");
    const data = await res.json();
    allLocations = data.states || [];
    setupLocationSelectors();
  } catch (err) {
    console.error("Failed to load nationwide locations:", err);
  }
}

function setupLocationSelectors() {
  const pState = document.getElementById("p-state");
  const pDistrict = document.getElementById("p-district");
  const vivaState = document.getElementById("viva-state");
  const vivaDistrict = document.getElementById("viva-district");

  if (!pState || !allLocations.length) return;

  const sortedStates = [...allLocations].sort((a, b) => a.name.localeCompare(b.name));

  // Populate Citizen Form State Dropdown
  pState.innerHTML = "";
  sortedStates.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.name;
    opt.textContent = `${s.name}${s.type === 'Union Territory' ? ' (UT)' : ''}`;
    if (s.name === "Jharkhand") opt.selected = true;
    pState.appendChild(opt);
  });

  // Populate Viva Inspector State Dropdown
  if (vivaState) {
    vivaState.innerHTML = "";
    sortedStates.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s.name;
      opt.textContent = `${s.name}${s.type === 'Union Territory' ? ' (UT)' : ''}`;
      if (s.name === "Jharkhand") opt.selected = true;
      vivaState.appendChild(opt);
    });
  }

  function updateDistrictsFor(stateEl, districtEl, preferredDistrict = null) {
    if (!stateEl || !districtEl) return;
    const selectedState = stateEl.value;
    const found = allLocations.find(s => s.name === selectedState);
    districtEl.innerHTML = "";

    if (found && found.districts && found.districts.length) {
      found.districts.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = d;
        if (preferredDistrict && d.toLowerCase() === preferredDistrict.toLowerCase()) {
          opt.selected = true;
        }
        districtEl.appendChild(opt);
      });
    } else {
      const opt = document.createElement("option");
      opt.value = "General";
      opt.textContent = "General";
      districtEl.appendChild(opt);
    }
  }

  pState.addEventListener("change", () => {
    updateDistrictsFor(pState, pDistrict);
    triggerInstantAIPreview();
  });

  if (vivaState && vivaDistrict) {
    vivaState.addEventListener("change", () => {
      updateDistrictsFor(vivaState, vivaDistrict);
    });
  }

  // Set default initial districts
  updateDistrictsFor(pState, pDistrict, "Ranchi");
  if (vivaState && vivaDistrict) {
    updateDistrictsFor(vivaState, vivaDistrict, "Palamu");
  }
}

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active", "bg-indigo-600"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  const targetNav = document.getElementById(`nav-${tabId}`);

  if (targetTab) targetTab.classList.remove("hidden");
  if (targetNav) targetNav.classList.add("active", "bg-indigo-600");

  if (tabId === "dashboard") {
    refreshDashboard();
  } else if (tabId === "university") {
    renderUniversityPortal();
  } else if (tabId === "industry") {
    renderIndustryPortal();
  } else if (tabId === "viva") {
    executeVivaAIInspection();
  }
}

// Fetch Master Universities
async function loadUniversities() {
  try {
    const res = await fetch("/api/universities");
    allUniversities = await res.json();
  } catch (err) {
    console.error("Failed to load universities:", err);
  }
}

// -------------------------------------------------------------
// DASHBOARD & ANALYTICS
// -------------------------------------------------------------
async function refreshDashboard() {
  await loadAnalytics();
  await loadProblems();
}

async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();

    document.getElementById("stat-total-problems").innerText = data.total_problems;
    document.getElementById("stat-total-solutions").innerText = data.total_solutions;
    document.getElementById("stat-total-funds").innerText = `₹${(data.total_csr_funds || 0).toLocaleString("en-IN")}`;
    document.getElementById("stat-total-resolved").innerText = data.resolved_problems || 0;

    renderDomainChart(data.domain_distribution || {});
    renderPriorityChart(data.priority_distribution || {});
  } catch (err) {
    console.error("Error loading analytics:", err);
  }
}

function renderDomainChart(domainCounts) {
  const ctx = document.getElementById("domainChart").getContext("2d");
  const labels = Object.keys(domainCounts);
  const counts = Object.values(domainCounts);

  if (domainChartInstance) domainChartInstance.destroy();

  domainChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels.length ? labels : ["None"],
      datasets: [{
        label: "Reported Challenges",
        data: counts.length ? counts : [0],
        backgroundColor: "rgba(99, 102, 241, 0.8)",
        borderColor: "rgba(99, 102, 241, 1)",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
        x: { ticks: { font: { size: 10 } } }
      }
    }
  });
}

function renderPriorityChart(priorityCounts) {
  const ctx = document.getElementById("priorityChart").getContext("2d");
  const labels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
  const data = labels.map(l => priorityCounts[l] || 0);

  if (priorityChartInstance) priorityChartInstance.destroy();

  priorityChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Critical", "High", "Medium", "Low"],
      datasets: [{
        data: data,
        backgroundColor: [
          "#ef4444", // Critical
          "#f59e0b", // High
          "#3b82f6", // Medium
          "#94a3b8"  // Low
        ],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
      },
      cutout: "68%"
    }
  });
}

async function loadProblems() {
  const domain = document.getElementById("filter-domain").value;
  const status = document.getElementById("filter-status").value;

  try {
    const res = await fetch(`/api/problems?domain=${encodeURIComponent(domain)}&status=${encodeURIComponent(status)}`);
    allProblems = await res.json();

    const tbody = document.getElementById("problems-table-body");
    tbody.innerHTML = "";

    if (!allProblems.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">No societal problems found for selected filters.</td></tr>`;
      return;
    }

    allProblems.forEach(p => {
      const priorityClass = getPriorityBadgeClass(p.priority_level);
      const statusBadge = getStatusBadge(p.status);

      const row = document.createElement("tr");
      row.className = "hover:bg-slate-50 transition border-b border-slate-100";
      row.innerHTML = `
        <td class="px-4 py-3 font-mono font-semibold text-slate-700">
          ${p.id}
          <div class="text-[10px] text-slate-400 font-sans">${new Date(p.created_at).toLocaleDateString()}</div>
        </td>
        <td class="px-4 py-3 max-w-xs">
          <div class="font-bold text-slate-900 truncate" title="${p.title}">${p.title}</div>
          <div class="text-[11px] text-slate-500 flex items-center space-x-1 mt-0.5">
            <i class="fa-solid fa-location-dot text-red-500"></i>
            <span>${p.district}${p.state ? ', ' + p.state : ''}${p.locality ? ' • ' + p.locality : ''}</span>
          </div>
        </td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
            ${p.predicted_domain}
          </span>
          <div class="text-[10px] text-indigo-500 mt-0.5 font-medium">Confidence: ${p.ai_confidence}%</div>
        </td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded text-[11px] font-bold ${priorityClass}">
            ${p.priority_level} (${p.priority_score})
          </span>
        </td>
        <td class="px-4 py-3 max-w-xs text-xs text-slate-700 font-medium truncate">
          ${p.assigned_university_name || '<span class="text-slate-400 italic">Unassigned</span>'}
        </td>
        <td class="px-4 py-3">
          ${statusBadge}
        </td>
        <td class="px-4 py-3 text-right">
          <button onclick="openProblemModal('${p.id}')" class="px-2.5 py-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 rounded-md transition">
            View / Assign
          </button>
        </td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to load problems:", err);
  }
}

function getPriorityBadgeClass(level) {
  switch (level) {
    case "CRITICAL": return "badge-critical";
    case "HIGH": return "badge-high";
    case "MEDIUM": return "badge-medium";
    default: return "badge-low";
  }
}

function getStatusBadge(status) {
  const map = {
    "Submitted": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700">Submitted</span>',
    "AI_Screened": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-100 text-blue-800">AI Screened</span>',
    "Assigned_University": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-sky-100 text-sky-800">Assigned</span>',
    "Solution_Proposed": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-800">Solution Proposed</span>',
    "Industry_Funded": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-100 text-emerald-800">Industry Funded</span>',
    "In_Progress": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-purple-100 text-purple-800">In Progress</span>',
    "Resolved": '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-green-100 text-green-800 font-bold"><i class="fa-solid fa-check mr-1"></i>Resolved</span>'
  };
  return map[status] || `<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700">${status}</span>`;
}

// -------------------------------------------------------------
// CITIZEN SUBMISSION & LIVE AI ASSISTANT
// -------------------------------------------------------------
let aiTypingTimeout = null;
function setupLiveInputWatcher() {
  const descInput = document.getElementById("p-description");
  if (descInput) {
    descInput.addEventListener("input", () => {
      clearTimeout(aiTypingTimeout);
      aiTypingTimeout = setTimeout(() => {
        if (descInput.value.length > 25) {
          triggerInstantAIPreview();
        }
      }, 700);
    });
  }
}

async function triggerInstantAIPreview() {
  const title = document.getElementById("p-title").value || "Societal Issue";
  const desc = document.getElementById("p-description").value;
  const state = document.getElementById("p-state") ? document.getElementById("p-state").value : "Jharkhand";
  const district = document.getElementById("p-district").value;
  const urgency = document.getElementById("p-urgency").value;
  const impact = document.getElementById("p-impact").value;

  if (!desc || desc.trim().length < 10) return;

  try {
    const res = await fetch("/api/ai/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: title,
        description: desc,
        state: state,
        district: district,
        urgency: urgency,
        impact: impact
      })
    });
    const data = await res.json();

    const box = document.getElementById("ai-preview-box");
    box.classList.remove("hidden");

    // Domain
    document.getElementById("preview-domain").innerText = data.nlp_classification.predicted_domain;
    document.getElementById("preview-confidence").innerText = `Confidence: ${data.nlp_classification.confidence}%`;

    // Duplicate Check
    const dup = data.duplicate_detection;
    if (dup.has_duplicates) {
      document.getElementById("preview-duplicate").innerHTML = `<span class="text-amber-600"><i class="fa-solid fa-triangle-exclamation mr-1"></i>${dup.duplicate_count} Duplicate(s) Found</span>`;
      document.getElementById("preview-duplicate-sub").innerText = `Top Match Similarity: ${dup.highest_similarity}%`;
    } else {
      document.getElementById("preview-duplicate").innerHTML = `<span class="text-emerald-600"><i class="fa-solid fa-circle-check mr-1"></i>Unique Submission</span>`;
      document.getElementById("preview-duplicate-sub").innerText = `Max Similarity: ${dup.highest_similarity}% (Below threshold)`;
    }

    // Recommended University
    if (data.recommended_universities && data.recommended_universities.length) {
      const topUni = data.recommended_universities[0];
      document.getElementById("preview-university").innerText = topUni.name;
      document.getElementById("preview-uni-sub").innerText = `Match Score: ${topUni.match_score}% (${topUni.rationale})`;
    }
  } catch (err) {
    console.error("AI preview failed:", err);
  }
}

async function submitCitizenProblem(e) {
  e.preventDefault();
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Analyzing & Registering...</span>`;

  try {
    const fileInput = document.getElementById("p-file");
    const formData = new FormData();
    formData.append("title", document.getElementById("p-title").value);
    formData.append("description", document.getElementById("p-description").value);
    formData.append("state", document.getElementById("p-state") ? document.getElementById("p-state").value : "Jharkhand");
    formData.append("district", document.getElementById("p-district").value);
    formData.append("locality", document.getElementById("p-locality").value);
    formData.append("citizen_name", document.getElementById("p-name").value);
    formData.append("citizen_contact", document.getElementById("p-contact").value);
    formData.append("urgency", document.getElementById("p-urgency").value);
    formData.append("impact", document.getElementById("p-impact").value);

    if (fileInput && fileInput.files[0]) {
      formData.append("file", fileInput.files[0]);
    }

    const res = await fetch("/api/problems/upload", {
      method: "POST",
      body: formData
    });
    const result = await res.json();

    if (result.success) {
      alert(`Problem registered successfully!\nAssigned ID: ${result.problem_id}\nClassified Domain: ${result.analysis.nlp_classification.predicted_domain}\nPriority: ${result.analysis.priority.priority_level}`);
      document.getElementById("problem-form").reset();
      document.getElementById("ai-preview-box").classList.add("hidden");
      switchTab("dashboard");
    } else {
      alert("Submission failed. Please check inputs.");
    }
  } catch (err) {
    console.error("Submission error:", err);
    alert("Error submitting problem. See console.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i><span>Submit Societal Challenge</span>`;
  }
}

// -------------------------------------------------------------
// UNIVERSITY PORTAL & PROJECT LIFECYCLE
// -------------------------------------------------------------
async function renderUniversityPortal() {
  const uniSelect = document.getElementById("university-filter-select");
  const selectedUniId = uniSelect.value;
  const uni = allUniversities.find(u => u.id === selectedUniId) || allUniversities[0];

  if (!uni) return;

  // Render Profile Card
  const profileCard = document.getElementById("university-profile-card");
  profileCard.innerHTML = `
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <span class="text-xs font-semibold text-sky-300 uppercase tracking-wider">Institution Profile</span>
        <h3 class="text-xl font-bold text-white mt-0.5">${uni.name}</h3>
        <p class="text-xs text-sky-100 mt-1"><i class="fa-solid fa-user-tie mr-1 text-sky-400"></i>Lead Faculty: ${uni.faculty_lead}</p>
        <div class="flex flex-wrap gap-1.5 mt-2">
          ${uni.primary_domains.map(d => `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-sky-500/30 text-sky-200 border border-sky-400/30">${d}</span>`).join("")}
        </div>
      </div>
      <div class="text-xs text-right text-slate-300">
        <p><strong>Departments:</strong> ${uni.departments.slice(0, 3).join(", ")}</p>
        <p class="mt-0.5"><strong>Districts:</strong> ${uni.districts.join(", ")}</p>
      </div>
    </div>
  `;

  // Fetch all problems & solutions to match
  try {
    const [pRes, sRes] = await Promise.all([
      fetch("/api/problems"),
      fetch("/api/solutions")
    ]);
    const problems = await pRes.json();
    const solutions = await sRes.json();

    // 1. Challenges assigned to or matched with this university
    const assignedChallenges = problems.filter(p =>
      p.assigned_university_id === uni.id ||
      uni.primary_domains.includes(p.predicted_domain)
    );

    document.getElementById("uni-challenge-count").innerText = `${assignedChallenges.length} Challenges`;

    const challengesList = document.getElementById("uni-assigned-challenges-list");
    challengesList.innerHTML = "";

    if (!assignedChallenges.length) {
      challengesList.innerHTML = `<div class="p-6 text-center text-slate-400 text-xs">No pending challenges matched for this institution yet.</div>`;
    } else {
      assignedChallenges.forEach(p => {
        const item = document.createElement("div");
        item.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white hover:border-sky-300 transition shadow-sm space-y-2";
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold text-slate-500">${p.id} • ${p.district}${p.state ? ', ' + p.state : ''}</span>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded ${getPriorityBadgeClass(p.priority_level)}">${p.priority_level}</span>
          </div>
          <h4 class="font-bold text-slate-900 text-xs leading-snug">${p.title}</h4>
          <p class="text-[11px] text-slate-600 line-clamp-2">${p.description}</p>
          <div class="flex items-center justify-between pt-2 border-t border-slate-200/80">
            <span class="text-[10px] text-sky-700 font-semibold bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
              ${p.predicted_domain}
            </span>
            <button onclick="openSolutionModal('${p.id}', '${escapeQuotes(p.title)}', '${uni.id}', '${escapeQuotes(uni.name)}', '${escapeQuotes(uni.faculty_lead)}')" class="px-3 py-1 bg-sky-600 hover:bg-sky-700 text-white text-[11px] font-bold rounded-lg transition shadow-sm flex items-center space-x-1">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Submit Solution Proposal</span>
            </button>
          </div>
        `;
        challengesList.appendChild(item);
      });
    }

    // 2. Solutions submitted by this university
    const uniSolutions = solutions.filter(s => s.university_id === uni.id);
    document.getElementById("uni-project-count").innerText = `${uniSolutions.length} Projects`;

    const solutionsList = document.getElementById("uni-solutions-list");
    solutionsList.innerHTML = "";

    if (!uniSolutions.length) {
      solutionsList.innerHTML = `<div class="p-6 text-center text-slate-400 text-xs">No active innovation projects submitted yet. Click 'Submit Solution Proposal' on a challenge.</div>`;
    } else {
      uniSolutions.forEach(s => {
        const card = document.createElement("div");
        card.className = "p-4 rounded-xl border border-emerald-200 bg-white shadow-sm space-y-3";
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              For: ${s.problem_id}
            </span>
            <span class="text-[10px] font-semibold text-slate-500">${s.timeline_months} Months • ₹${Number(s.estimated_budget).toLocaleString("en-IN")}</span>
          </div>
          <h4 class="font-bold text-slate-900 text-xs">${s.solution_title}</h4>
          <p class="text-[11px] text-slate-600 leading-relaxed">${s.proposal_summary}</p>
          <div class="text-[10px] text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100">
            <p><strong>Faculty:</strong> ${s.lead_faculty}</p>
            <p><strong>Team:</strong> ${s.student_team}</p>
          </div>
          <!-- Milestones Checklist -->
          <div class="pt-2 border-t border-slate-100">
            <p class="text-[11px] font-bold text-slate-700 mb-1.5 flex items-center justify-between">
              <span>Project Lifecycle Milestones</span>
              <span class="text-[10px] font-normal text-slate-400">Click to advance</span>
            </p>
            <div class="space-y-1">
              ${s.milestones.map((m, idx) => `
                <div class="flex items-center justify-between text-[11px] p-1.5 rounded bg-slate-50 border border-slate-200/60">
                  <span class="${m.status === 'Completed' ? 'line-through text-slate-400' : 'text-slate-700'}">
                    <i class="fa-solid ${m.status === 'Completed' ? 'fa-circle-check text-emerald-500' : 'fa-circle-dot text-amber-500'} mr-1.5"></i>
                    ${m.title} (${m.date})
                  </span>
                  <button onclick="toggleMilestone(${s.id}, ${idx}, '${m.status === 'Completed' ? 'In Progress' : 'Completed'}')" class="text-[10px] px-2 py-0.5 rounded ${m.status === 'Completed' ? 'bg-emerald-100 text-emerald-800 font-semibold' : 'bg-slate-200 text-slate-700 hover:bg-emerald-600 hover:text-white'} transition">
                    ${m.status}
                  </button>
                </div>
              `).join("")}
            </div>
          </div>
        `;
        solutionsList.appendChild(card);
      });
    }

  } catch (err) {
    console.error("Failed to render university portal:", err);
  }
}

async function toggleMilestone(solutionId, milestoneIndex, newStatus) {
  try {
    const formData = new FormData();
    formData.append("milestone_index", milestoneIndex);
    formData.append("new_status", newStatus);

    const res = await fetch(`/api/solutions/${solutionId}/milestone`, {
      method: "POST",
      body: formData
    });
    if (res.ok) {
      renderUniversityPortal();
    }
  } catch (err) {
    console.error("Milestone update failed:", err);
  }
}

// -------------------------------------------------------------
// INDUSTRY & CSR COLLABORATION PORTAL
// -------------------------------------------------------------
async function renderIndustryPortal() {
  try {
    const [sRes, indRes] = await Promise.all([
      fetch("/api/solutions"),
      fetch("/api/industry")
    ]);
    const solutions = await sRes.json();
    const pledges = await indRes.json();

    const projContainer = document.getElementById("industry-projects-list");
    projContainer.innerHTML = "";

    if (!solutions.length) {
      projContainer.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs">No active university proposals seeking CSR funding yet.</div>`;
    } else {
      solutions.forEach(s => {
        const item = document.createElement("div");
        item.className = "p-4 rounded-xl border border-slate-200 bg-white hover:border-emerald-300 transition shadow-sm space-y-2";
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">${s.university_name}</span>
            <span class="text-[11px] font-extrabold text-slate-900">Budget Required: ₹${Number(s.estimated_budget).toLocaleString("en-IN")}</span>
          </div>
          <h4 class="font-bold text-slate-900 text-sm">${s.solution_title}</h4>
          <p class="text-xs text-slate-600 leading-relaxed">${s.proposal_summary}</p>
          <div class="bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-[11px] text-slate-600 flex justify-between items-center">
            <span><strong>Technical Approach:</strong> ${s.technical_approach || 'Prototyping & field trials'}</span>
            <span><strong>Timeline:</strong> ${s.timeline_months} Months</span>
          </div>
          <div class="pt-2 flex justify-end">
            <button onclick="openIndustryPledgeModal('${s.problem_id}', ${s.id}, '${escapeQuotes(s.solution_title)}')" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg transition shadow-sm flex items-center space-x-1.5">
              <i class="fa-solid fa-coins"></i>
              <span>Pledge CSR Capital / Mentorship</span>
            </button>
          </div>
        `;
        projContainer.appendChild(item);
      });
    }

    // Pledges Log
    const pledgeContainer = document.getElementById("industry-pledges-list");
    pledgeContainer.innerHTML = "";

    if (!pledges.length) {
      pledgeContainer.innerHTML = `<div class="p-4 text-center text-slate-400 text-xs">No corporate pledges registered yet.</div>`;
    } else {
      pledges.forEach(p => {
        const item = document.createElement("div");
        item.className = "p-3 rounded-lg border border-emerald-200 bg-emerald-50/50 space-y-1 text-xs";
        item.innerHTML = `
          <div class="flex items-center justify-between font-bold text-slate-900">
            <span>${p.company_name}</span>
            <span class="text-emerald-700 font-extrabold">₹${Number(p.amount_pledged).toLocaleString("en-IN")}</span>
          </div>
          <p class="text-[11px] text-slate-600">Support Type: <strong>${p.support_type}</strong></p>
          ${p.mentor_name ? `<p class="text-[10px] text-slate-500"><i class="fa-solid fa-user-check mr-1 text-emerald-600"></i>Mentor: ${p.mentor_name}</p>` : ''}
          <div class="text-[10px] text-emerald-800 font-semibold pt-1">
            <i class="fa-solid fa-circle-check mr-1 text-emerald-600"></i>Status: ${p.status}
          </div>
        `;
        pledgeContainer.appendChild(item);
      });
    }

  } catch (err) {
    console.error("Failed to render industry portal:", err);
  }
}

// -------------------------------------------------------------
// AI VIVA DEMONSTRATION INSPECTOR (COLLEGE EVALUATION SUITE)
// -------------------------------------------------------------
function loadVivaPreset() {
  const sel = document.getElementById("viva-sample-select").value;
  if (sel === "custom") return;

  const preset = VIVA_PRESETS[sel];
  if (preset) {
    document.getElementById("viva-title").value = preset.title;
    document.getElementById("viva-desc").value = preset.desc;

    const vivaState = document.getElementById("viva-state");
    const vivaDistrict = document.getElementById("viva-district");
    if (vivaState && preset.state) {
      vivaState.value = preset.state;
      // Populate districts for this state
      const found = allLocations.find(s => s.name === preset.state);
      if (found && found.districts && vivaDistrict) {
        vivaDistrict.innerHTML = "";
        found.districts.forEach(d => {
          const opt = document.createElement("option");
          opt.value = d;
          opt.textContent = d;
          if (d.toLowerCase() === preset.district.toLowerCase()) opt.selected = true;
          vivaDistrict.appendChild(opt);
        });
      }
    } else if (vivaDistrict) {
      vivaDistrict.value = preset.district;
    }

    document.getElementById("viva-urgency").value = preset.urgency;
    executeVivaAIInspection();
  }
}

async function executeVivaAIInspection() {
  const title = document.getElementById("viva-title").value;
  const desc = document.getElementById("viva-desc").value;
  const state = document.getElementById("viva-state") ? document.getElementById("viva-state").value : "Jharkhand";
  const district = document.getElementById("viva-district").value;
  const urgency = document.getElementById("viva-urgency").value;

  try {
    const res = await fetch("/api/ai/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: title,
        description: desc,
        state: state,
        district: district,
        urgency: urgency,
        impact: "Community"
      })
    });
    const data = await res.json();

    // 1. TF-IDF Features
    const featBox = document.getElementById("viva-features-container");
    featBox.innerHTML = "";
    if (data.nlp_classification.key_features && data.nlp_classification.key_features.length) {
      data.nlp_classification.key_features.forEach(f => {
        const badge = document.createElement("span");
        badge.className = "px-2.5 py-1 rounded-md text-[11px] font-mono bg-purple-50 text-purple-900 border border-purple-200 flex items-center space-x-1";
        badge.innerHTML = `<strong>${f.term}</strong> <span class="text-purple-500 font-bold ml-1">(${f.weight})</span>`;
        featBox.appendChild(badge);
      });
    } else {
      featBox.innerHTML = `<span class="text-slate-400 text-xs">No significant n-grams extracted.</span>`;
    }

    // 2. Probability Chart
    const probs = data.nlp_classification.all_probabilities;
    document.getElementById("viva-top-domain-badge").innerText = `Predicted: ${data.nlp_classification.predicted_domain} (${data.nlp_classification.confidence}%)`;

    renderVivaProbChart(probs);

    // 3. Cosine Duplicate Detection
    const dup = data.duplicate_detection;
    const simList = document.getElementById("viva-similarity-list");
    simList.innerHTML = "";

    const dupBadge = document.getElementById("viva-duplicate-status-badge");
    if (dup.has_duplicates) {
      dupBadge.className = "px-2 py-0.5 text-xs font-bold rounded bg-red-100 text-red-800";
      dupBadge.innerText = `DUPLICATE ALERT: ${dup.duplicate_count} Detected`;
    } else {
      dupBadge.className = "px-2 py-0.5 text-xs font-bold rounded bg-emerald-100 text-emerald-800";
      dupBadge.innerText = `UNIQUE PROBLEM (${dup.highest_similarity}% max sim)`;
    }

    if (dup.matches && dup.matches.length) {
      dup.matches.forEach(m => {
        const row = document.createElement("div");
        row.className = "p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs";
        row.innerHTML = `
          <div>
            <span class="font-bold text-slate-800">${m.problem_id}</span>: ${m.title}
            <span class="text-[10px] text-slate-500 block">Location: ${m.district || 'General'}${m.state ? ', ' + m.state : ''}</span>
          </div>
          <span class="px-2 py-0.5 font-bold rounded text-xs ${m.similarity >= 65 ? 'bg-red-100 text-red-700' : 'bg-sky-100 text-sky-700'}">
            ${m.similarity}% (${m.type})
          </span>
        `;
        simList.appendChild(row);
      });
    } else {
      simList.innerHTML = `<div class="text-slate-400 text-xs py-1">No similar issues detected in current registry (Cosine Similarity < 35%).</div>`;
    }

    // 4. University Ranking Matrix
    const uniBox = document.getElementById("viva-university-matrix");
    uniBox.innerHTML = "";
    if (data.recommended_universities && data.recommended_universities.length) {
      data.recommended_universities.forEach((u, i) => {
        const item = document.createElement("div");
        item.className = "p-2.5 rounded-lg border border-slate-200 bg-slate-50/80 flex items-center justify-between text-xs";
        item.innerHTML = `
          <div class="max-w-[75%]">
            <div class="font-bold text-slate-900">${i + 1}. ${u.name}</div>
            <div class="text-[10px] text-slate-500 mt-0.5">${u.rationale}</div>
            <div class="text-[10px] text-indigo-600 mt-0.5 font-semibold">Lead: ${u.faculty_lead}</div>
          </div>
          <div class="text-right">
            <span class="px-2.5 py-1 text-xs font-extrabold rounded-md bg-indigo-600 text-white">${u.match_score}%</span>
            <div class="text-[9px] text-slate-400 mt-0.5 font-mono">Affinity Index</div>
          </div>
        `;
        uniBox.appendChild(item);
      });
    }

  } catch (err) {
    console.error("Viva inspection failed:", err);
  }
}

function renderVivaProbChart(probs) {
  const ctx = document.getElementById("vivaProbChart").getContext("2d");
  const labels = probs.map(p => p.domain);
  const data = probs.map(p => p.confidence);

  if (vivaProbChartInstance) vivaProbChartInstance.destroy();

  vivaProbChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Confidence Probability (%)",
        data: data,
        backgroundColor: [
          "#6366f1", "#8b5cf6", "#ec4899", "#f43f5e",
          "#f97316", "#eab308", "#10b981", "#06b6d4"
        ],
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } },
        y: { ticks: { font: { size: 10 } } }
      }
    }
  });
}

// -------------------------------------------------------------
// MODALS LOGIC
// -------------------------------------------------------------
let activeModalProblemId = null;

async function openProblemModal(problemId) {
  activeModalProblemId = problemId;
  try {
    const res = await fetch(`/api/problems/${problemId}`);
    const data = await res.json();
    const p = data.problem;

    document.getElementById("modal-p-id").innerText = p.id;
    document.getElementById("modal-p-domain").innerText = p.predicted_domain;
    document.getElementById("modal-p-title").innerText = p.title;
    document.getElementById("modal-p-location").innerHTML = `<i class="fa-solid fa-location-dot mr-1 text-red-500"></i>${p.district}${p.state ? ', ' + p.state : ''}${p.locality ? ' • ' + p.locality : ''}`;
    document.getElementById("modal-p-desc").innerText = p.description;

    document.getElementById("modal-p-category-val").innerText = p.predicted_domain;
    document.getElementById("modal-p-conf-val").innerText = `${p.ai_confidence}%`;
    document.getElementById("modal-p-prio-score").innerText = `${p.priority_score}/100 (${p.priority_level})`;
    document.getElementById("modal-p-assigned-val").innerText = p.assigned_university_name || "Unassigned";

    const prioBadge = document.getElementById("modal-p-priority");
    prioBadge.className = `px-2 py-0.5 font-bold rounded text-white ${p.priority_level === 'CRITICAL' ? 'bg-red-600' : 'bg-amber-600'}`;
    prioBadge.innerText = p.priority_level;

    // Media
    const mediaContainer = document.getElementById("modal-p-media-container");
    const mediaImg = document.getElementById("modal-p-media-img");
    if (p.evidence_media) {
      mediaContainer.classList.remove("hidden");
      mediaImg.src = `/uploads/${p.evidence_media}`;
    } else {
      mediaContainer.classList.add("hidden");
    }

    document.getElementById("modal-problem").classList.remove("hidden");
  } catch (err) {
    console.error("Failed to open problem modal:", err);
  }
}

function closeProblemModal() {
  document.getElementById("modal-problem").classList.add("hidden");
}

async function submitAssignmentFromModal() {
  if (!activeModalProblemId) return;
  const select = document.getElementById("modal-assign-uni-select");
  const uniId = select.value;
  const uniName = select.options[select.selectedIndex].getAttribute("data-name");

  try {
    const formData = new FormData();
    formData.append("university_id", uniId);
    formData.append("university_name", uniName);

    const res = await fetch(`/api/problems/${activeModalProblemId}/assign`, {
      method: "POST",
      body: formData
    });
    const resData = await res.json();
    if (resData.success) {
      alert(`Problem ${activeModalProblemId} successfully assigned to ${uniName}!`);
      closeProblemModal();
      refreshDashboard();
    }
  } catch (err) {
    console.error("Assignment error:", err);
  }
}

function openSolutionModal(probId, probTitle, uniId, uniName, facultyLead) {
  document.getElementById("sol-problem-id").value = probId;
  document.getElementById("sol-problem-title-display").value = `[${probId}] ${probTitle}`;
  document.getElementById("sol-uni-id").value = uniId;
  document.getElementById("sol-uni-name").value = uniName;
  document.getElementById("sol-faculty").value = facultyLead;
  document.getElementById("modal-solution-form").classList.remove("hidden");
}

function closeSolutionModal() {
  document.getElementById("modal-solution-form").classList.add("hidden");
}

async function submitUniversityProposal(e) {
  e.preventDefault();
  const payload = {
    problem_id: document.getElementById("sol-problem-id").value,
    university_id: document.getElementById("sol-uni-id").value,
    university_name: document.getElementById("sol-uni-name").value,
    lead_faculty: document.getElementById("sol-faculty").value,
    student_team: document.getElementById("sol-team").value,
    solution_title: document.getElementById("sol-title").value,
    proposal_summary: document.getElementById("sol-summary").value,
    technical_approach: "Prototyping & field validation",
    estimated_budget: parseFloat(document.getElementById("sol-budget").value) || 200000,
    timeline_months: parseInt(document.getElementById("sol-timeline").value) || 6,
    milestones: [
      { title: "Lab Prototyping & Design", status: "In Progress", date: "Month 2" },
      { title: "Pilot Field Testing", status: "Upcoming", date: "Month 4" },
      { title: "Final Evaluation & Community Handover", status: "Upcoming", date: "Month 6" }
    ]
  };

  try {
    const res = await fetch("/api/solutions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      alert("Innovation proposal registered successfully!");
      closeSolutionModal();
      renderUniversityPortal();
      refreshDashboard();
    }
  } catch (err) {
    console.error("Error submitting solution:", err);
  }
}

function openIndustryPledgeModal(problemId, solutionId, projectTitle) {
  document.getElementById("pledge-problem-id").value = problemId;
  document.getElementById("pledge-solution-id").value = solutionId;
  document.getElementById("pledge-project-name").value = projectTitle;
  document.getElementById("modal-industry-pledge").classList.remove("hidden");
}

function closeIndustryModal() {
  document.getElementById("modal-industry-pledge").classList.add("hidden");
}

async function submitIndustryPledge(e) {
  e.preventDefault();
  const payload = {
    problem_id: document.getElementById("pledge-problem-id").value,
    solution_id: parseInt(document.getElementById("pledge-solution-id").value),
    company_name: document.getElementById("pledge-company").value,
    support_type: document.getElementById("pledge-type").value,
    amount_pledged: parseFloat(document.getElementById("pledge-amount").value) || 0,
    mentor_name: document.getElementById("pledge-mentor").value
  };

  try {
    const res = await fetch("/api/industry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      alert(`CSR pledge registered successfully from ${payload.company_name}!`);
      closeIndustryModal();
      renderIndustryPortal();
      refreshDashboard();
    }
  } catch (err) {
    console.error("Error submitting CSR pledge:", err);
  }
}

function toggleVivaGuideModal() {
  const modal = document.getElementById("modal-viva-guide");
  modal.classList.toggle("hidden");
}

// QR Code & Sharing Logic
function openQRModal() {
  const currentUrl = window.location.href;
  document.getElementById("share-link-input").value = currentUrl;
  const qrImg = document.getElementById("qr-code-img");
  qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(currentUrl)}`;
  document.getElementById("modal-qr-share").classList.remove("hidden");
}

function closeQRModal() {
  document.getElementById("modal-qr-share").classList.add("hidden");
}

function copyShareLink() {
  const input = document.getElementById("share-link-input");
  input.select();
  navigator.clipboard.writeText(input.value);
  const btnText = document.getElementById("copy-btn-text");
  btnText.innerText = "Copied!";
  setTimeout(() => { btnText.innerText = "Copy"; }, 2000);
}

// Utility: Escape quotes for inline HTML attributes
function escapeQuotes(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
