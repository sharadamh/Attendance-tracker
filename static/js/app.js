/**
 * app.js — shared utilities used across all pages.
 *
 * Functions exported to global scope (used via inline onclick / page scripts):
 *   esc(str)                    — HTML-escape a string
 *   openModal(title, bodyHTML)  — show the shared modal
 *   closeModal()                — hide the shared modal
 *   openConfirm(msg, callback)  — show the confirm dialog
 *   showNotification(msg, type) — show a temporary top-right toast
 *   apiFetch(url, method, data) — JSON API helper, returns parsed response
 */

// ── HTML escaping ────────────────────────────────────────────────────────────
function esc(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ── API fetch helper ─────────────────────────────────────────────────────────
async function apiFetch(url, method = "GET", data = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (data !== null) {
    options.body = JSON.stringify(data);
  }
  try {
    const res = await fetch(url, options);
    return await res.json();
  } catch (err) {
    return { success: false, message: "Network error — is the server running?" };
  }
}

// ── Modal ────────────────────────────────────────────────────────────────────
function openModal(title, bodyHTML) {
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalBody").innerHTML = bodyHTML;
  document.getElementById("modalOverlay").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modalOverlay").classList.add("hidden");
  document.getElementById("modalBody").innerHTML = "";
}

// Close modal when overlay background is clicked
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("modalOverlay");
  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal();
    });
  }

  // Close button inside modal header
  const closeBtn = document.getElementById("modalClose");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
});

// ── Confirm dialog ───────────────────────────────────────────────────────────
let _confirmCallback = null;

function openConfirm(message, callback) {
  _confirmCallback = callback;
  document.getElementById("confirmMessage").textContent = message;
  document.getElementById("confirmOverlay").classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const confirmOverlay = document.getElementById("confirmOverlay");
  const confirmYes = document.getElementById("confirmYes");
  const confirmNo  = document.getElementById("confirmNo");

  if (confirmYes) {
    confirmYes.addEventListener("click", async () => {
      confirmOverlay.classList.add("hidden");
      if (_confirmCallback) await _confirmCallback();
      _confirmCallback = null;
    });
  }

  if (confirmNo) {
    confirmNo.addEventListener("click", () => {
      confirmOverlay.classList.add("hidden");
      _confirmCallback = null;
    });
  }
});

// ── Toast notification ───────────────────────────────────────────────────────
let _notifTimer = null;

function showNotification(message, type = "success") {
  const el = document.getElementById("notification");
  if (!el) return;

  clearTimeout(_notifTimer);
  el.textContent = message;
  el.className = `notification notification--${type}`;
  el.classList.remove("hidden");

  _notifTimer = setTimeout(() => {
    el.classList.add("hidden");
  }, 4000);
}

// ── Sidebar toggle (mobile) ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("sidebarToggle");
  const sidebar   = document.getElementById("sidebar");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // Display current date in header
  const dateEl = document.getElementById("currentDate");
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString("en-GB", {
      weekday: "short", day: "numeric", month: "short", year: "numeric"
    });
  }
});
