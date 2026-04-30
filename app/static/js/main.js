/**
 * MediCare Hospital — Main JavaScript
 * Handles UI interactions across all pages.
 */

document.addEventListener("DOMContentLoaded", () => {

  // ── Auto-dismiss flash alerts after 5 seconds ────────────────
  document.querySelectorAll(".alert.alert-dismissible").forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Live search filter for tables ────────────────────────────
  const searchInput = document.getElementById("liveSearch");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase().trim();
      const rows = document.querySelectorAll("tbody tr[data-search]");
      rows.forEach(row => {
        const text = row.dataset.search.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });

      // Show empty state if no results
      const visible = [...rows].filter(r => r.style.display !== "none");
      const emptyRow = document.getElementById("emptyRow");
      if (emptyRow) emptyRow.style.display = visible.length === 0 ? "" : "none";
    });
  }

  // ── Confirm delete / cancel dialogs ──────────────────────────
  document.querySelectorAll("[data-confirm]").forEach(el => {
    el.addEventListener("click", function (e) {
      const msg = this.dataset.confirm || "Are you sure?";
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Tooltip initialization ────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // ── Auto-set min date on appointment date inputs ──────────────
  const dateInput = document.getElementById("appointmentDate");
  if (dateInput) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.setAttribute("min", today);
  }

  // ── Character count for textareas ────────────────────────────
  document.querySelectorAll("textarea[maxlength]").forEach(ta => {
    const max = parseInt(ta.getAttribute("maxlength"));
    const counter = document.createElement("small");
    counter.className = "text-muted d-block text-end mt-1";
    counter.textContent = `0 / ${max}`;
    ta.parentNode.insertBefore(counter, ta.nextSibling);
    ta.addEventListener("input", () => {
      counter.textContent = `${ta.value.length} / ${max}`;
    });
  });

  // ── Navbar active state from URL ──────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll("#mainNav .nav-link").forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });

});
