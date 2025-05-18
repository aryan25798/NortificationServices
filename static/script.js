const BASE_URL = window.location.hostname === "localhost"
  ? "http://127.0.0.1:8000"
  : "https://web-production-66a2.up.railway.app";

const notificationForm = document.getElementById("notificationForm");
const getNotificationsForm = document.getElementById("getNotificationsForm");
const notificationsList = document.getElementById("notificationsList");

const filterType = document.getElementById("filterType");
const filterStatus = document.getElementById("filterStatus");
const exportCsvBtn = document.getElementById("exportCsvBtn");

const darkModeToggle = document.getElementById("darkModeToggle");
const body = document.body;

let notificationsData = [];

function showToast(message, isError = false) {
  const toastContainer = document.getElementById("toastContainer");
  const toastMessage = document.getElementById("toastMessage");

  toastMessage.textContent = message;
  toastContainer.classList.remove("d-none", "bg-success", "bg-danger");
  toastContainer.classList.add(isError ? "bg-danger" : "bg-success");

  toastContainer.style.opacity = "1";
  setTimeout(() => {
    toastContainer.style.opacity = "0";
    setTimeout(() => toastContainer.classList.add("d-none"), 500);
  }, 2500);
}

function launchConfetti() {
  confetti({
    particleCount: 80,
    spread: 60,
    origin: { y: 0.6 }
  });
}

function renderNotifications(notifs) {
  notificationsList.innerHTML = "";

  const filtered = notifs.filter(n => {
    const typeMatch = !filterType.value || n.type === filterType.value;
    const statusMatch = !filterStatus.value || n.status === filterStatus.value;
    return typeMatch && statusMatch;
  });

  if (filtered.length === 0) {
    notificationsList.innerHTML = `<p class="text-center fst-italic text-muted">No notifications found.</p>`;
    return;
  }

  filtered.forEach((n, index) => {
    const col = document.createElement("div");
    col.className = "col-md-6";

    const card = document.createElement("div");
    card.className = "card shadow-sm border-0 h-100";
    card.style.animation = "fadeIn 0.8s ease";

    const cardBody = document.createElement("div");
    cardBody.className = "card-body";

    const emoji = n.type === "email" ? "📧" : n.type === "sms" ? "📱" : "💬";

    const header = document.createElement("h5");
    header.className = "card-title d-flex justify-content-between align-items-center";
    header.innerHTML = `<span>${index + 1}. ${emoji} ${n.type.toUpperCase()}</span>`;

    const toggleIcon = document.createElement("i");
    toggleIcon.className = "fas fa-chevron-down collapse-toggle";
    toggleIcon.title = "Toggle details";
    header.appendChild(toggleIcon);

    const contentDiv = document.createElement("div");
    contentDiv.className = "collapse-content mt-2";
    contentDiv.style.maxHeight = "0";
    contentDiv.style.overflow = "hidden";
    contentDiv.style.transition = "max-height 0.3s ease";

    contentDiv.innerHTML = `
      <p class="card-text"><strong>Message:</strong> ${escapeHtml(n.message)}</p>
      <p class="card-text"><strong>Status:</strong> ${escapeHtml(n.status)}</p>
      <p class="card-text text-muted"><i class="fas fa-clock"></i> ${new Date(n.created_at).toLocaleString()}</p>
      <span class="badge bg-secondary">ID: ${n.id}</span>
    `;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn btn-sm btn-outline-danger mt-2";
    deleteBtn.setAttribute("aria-label", `Delete notification ${n.id}`);
    deleteBtn.innerHTML = `<i class="fas fa-trash-alt"></i> Delete`;
    deleteBtn.addEventListener("click", () => deleteNotification(n.id));

    const p = document.createElement("p");
    p.appendChild(deleteBtn);

    contentDiv.appendChild(p);

    toggleIcon.addEventListener("click", () => {
      if (contentDiv.style.maxHeight === "0px" || !contentDiv.style.maxHeight) {
        contentDiv.style.maxHeight = contentDiv.scrollHeight + "px";
        toggleIcon.classList.remove("collapsed");
      } else {
        contentDiv.style.maxHeight = "0";
        toggleIcon.classList.add("collapsed");
      }
    });

    cardBody.appendChild(header);
    cardBody.appendChild(contentDiv);
    card.appendChild(cardBody);
    col.appendChild(card);
    notificationsList.appendChild(col);
  });
}

function escapeHtml(text) {
  const map = {
    '&': "&amp;",
    '<': "&lt;",
    '>': "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function setDarkMode(isDark) {
  if (isDark) {
    body.classList.add("dark-mode");
    darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    localStorage.setItem("darkMode", "true");
  } else {
    body.classList.remove("dark-mode");
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    localStorage.setItem("darkMode", "false");
  }
}

function initTheme() {
  const saved = localStorage.getItem("darkMode");
  setDarkMode(saved === "true");
}

function exportToCSV(data) {
  if (!data.length) {
    showToast("No notifications to export", true);
    return;
  }
  const headers = ["ID", "Type", "Message", "Status", "Created At"];
  const csvRows = [
    headers.join(","),
    ...data.map(n =>
      `"${n.id}","${n.type}","${n.message.replace(/"/g, '""')}","${n.status}","${new Date(n.created_at).toLocaleString()}"`
    )
  ];
  const csvString = csvRows.join("\n");
  const blob = new Blob([csvString], { type: "text/csv" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `notifications_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("CSV exported successfully!");
}

async function deleteNotification(id) {
  if (!confirm("Are you sure you want to delete this notification?")) return;

  try {
    const response = await fetch(`${BASE_URL}/notifications/${id}`, {
      method: "DELETE"
    });

    if (response.ok) {
      showToast("Notification deleted!");
      notificationsData = notificationsData.filter(n => n.id !== id);
      renderNotifications(notificationsData);
    } else {
      showToast("Failed to delete notification.", true);
    }
  } catch (err) {
    showToast("Error deleting notification.", true);
  }
}

notificationForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userId = document.getElementById("userId").value;
  const type = document.getElementById("type").value;
  const message = document.getElementById("message").value;

  try {
    const response = await fetch(`${BASE_URL}/notifications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: parseInt(userId), type, message })
    });

    if (response.ok) {
      showToast("Notification sent!");
      notificationForm.reset();
      launchConfetti();
    } else {
      const data = await response.json();
      const errorMsg = data.detail || "Failed to send notification.";
      showToast(errorMsg, true);
    }
  } catch (err) {
    showToast("Network error: Could not send notification.", true);
  }
});

getNotificationsForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userId = document.getElementById("queryUserId").value;
  notificationsList.innerHTML = "";

  try {
    const response = await fetch(`${BASE_URL}/users/${userId}/notifications`);
    if (response.ok) {
      const data = await response.json();
      notificationsData = data;
      filterType.value = "";
      filterStatus.value = "";
      renderNotifications(notificationsData);
      showToast("Notifications fetched!");
      launchConfetti();
    } else {
      showToast("Failed to fetch notifications.", true);
    }
  } catch (err) {
    showToast("Network error: Could not fetch notifications.", true);
  }
});

filterType.addEventListener("change", () => renderNotifications(notificationsData));
filterStatus.addEventListener("change", () => renderNotifications(notificationsData));
exportCsvBtn.addEventListener("click", () => exportToCSV(notificationsData));
darkModeToggle.addEventListener("click", () => setDarkMode(!body.classList.contains("dark-mode")));

initTheme();
