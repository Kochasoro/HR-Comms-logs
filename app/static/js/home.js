function initializeColumnResize() {

    const table = document.querySelector(".records-table");
    if (!table) return;

    const headers = table.querySelectorAll("th");

    headers.forEach((header, index) => {

        const resizer = document.createElement("div");
        resizer.classList.add("column-resizer");
        header.appendChild(resizer);

        let startX, startWidth;

        resizer.addEventListener("mousedown", function (e) {

            startX = e.pageX;
            startWidth = header.offsetWidth;

            function mouseMove(e) {
                const newWidth = startWidth + (e.pageX - startX);

                header.style.width = newWidth + "px";

                const columnCells = table.querySelectorAll(
                    `td:nth-child(${index + 1})`
                );

                columnCells.forEach(cell => {
                    cell.style.width = newWidth + "px";
                });
            }

            function mouseUp() {
                document.removeEventListener("mousemove", mouseMove);
                document.removeEventListener("mouseup", mouseUp);
            }

            document.addEventListener("mousemove", mouseMove);
            document.addEventListener("mouseup", mouseUp);
        });

    });
}

/* =========================
INITIAL LOAD
========================= */

let timeout = null;
let currentType = new URLSearchParams(window.location.search).get("type") || "CM";

document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener("click", function (e) {

        if (e.target.closest(".action-menu")) {
            e.stopPropagation();
            return;
        }

    });
    initializeColumnResize();

    loadHolidays();

    const monthFilter = document.getElementById("monthFilter");
    const yearFilter = document.getElementById("yearFilter");
    const searchInput = document.getElementById("searchInput");
    const filterBtn = document.getElementById("filterBtn");
    const filterPanel = document.getElementById("filterPanel");
    const toggleOptions = document.querySelectorAll(".toggle-option");


    const today = new Date();
    monthFilter.value = today.getMonth() + 1;
    yearFilter.value = today.getFullYear();


    toggleOptions.forEach(btn => {
        if (btn.dataset.type === currentType) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    toggleOptions.forEach(btn => {
        btn.addEventListener("click", function () {

            toggleOptions.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            currentType = this.dataset.type;

            fetchTable();
        });
    });


    searchInput.addEventListener("input", () => {
        clearTimeout(timeout);
        timeout = setTimeout(fetchTable, 300);
    });


    monthFilter.addEventListener("change", fetchTable);
    yearFilter.addEventListener("change", fetchTable);



    document.querySelectorAll(".sort-option").forEach(option => {

        option.addEventListener("change", fetchTable);

    });
    document.querySelectorAll(
        ".office-filter, .forwarded-filter, .released-filter"
    ).forEach(option => {

        option.addEventListener("change", fetchTable);

    });

    filterBtn.addEventListener("click", (e) => {

        e.stopPropagation();

        filterPanel.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {

        if (
            !filterPanel.contains(e.target) &&
            !filterBtn.contains(e.target)
        ) {
            filterPanel.classList.remove("active");
        }
    });

});



/* =========================
FETCH TABLE
========================= */
function fetchTable() {

    const search = document.getElementById("searchInput")?.value || "";
    const month = document.getElementById("monthFilter")?.value || "";
    const year = document.getElementById("yearFilter")?.value || "";

    // SORT (RADIO BUTTON)
    const selectedSort = document.querySelector(".sort-option:checked");
    const sort = selectedSort ? selectedSort.value : "";

    // FROM OFFICE FILTERS
    const offices = Array.from(
        document.querySelectorAll(".office-filter:checked")
    ).map(cb => cb.value);

    // FORWARDED FILTERS
    const forwarded = Array.from(
        document.querySelectorAll(".forwarded-filter:checked")
    ).map(cb => cb.value);

    // RELEASED FILTERS
    const released = Array.from(
        document.querySelectorAll(".released-filter:checked")
    ).map(cb => cb.value);

    // BUILD PARAMS
    const params = new URLSearchParams();

    params.append("search", search);
    params.append("month", month);
    params.append("year", year);
    params.append("type", currentType);
    params.append("sort", sort);

    offices.forEach(o => {
        params.append("office", o);
    });

    forwarded.forEach(f => {
        params.append("forwarded", f);
    });

    released.forEach(r => {
        params.append("released", r);
    });

    fetch("/?" + params.toString())
        .then(res => res.text())
        .then(html => {

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");

            const newTable = doc.querySelector("#tableContainer");
            const currentTable = document.querySelector("#tableContainer");

            if (newTable && currentTable) {

                currentTable.innerHTML = newTable.innerHTML;

                initializeColumnResize();
            }
        })
        .catch(err => {
            console.error("Fetch table error:", err);
        });
}
document.addEventListener("click", function (e) {

    const btn = e.target.closest(".menu-btn");

    if (btn) {

        e.stopPropagation();

        const menu = btn.nextElementSibling;

        const isOpen = menu.style.display === "flex";

        document.querySelectorAll(".menu-dropdown")
            .forEach(m => m.style.display = "none");

        if (!isOpen) {

            menu.style.display = "flex";

            const rect = btn.getBoundingClientRect();

            menu.style.position = "fixed";
            menu.style.top = rect.bottom + "px";
            menu.style.left =
                rect.right - menu.offsetWidth + "px";
        }

        return;
    }

    document.querySelectorAll(".menu-dropdown")
        .forEach(m => m.style.display = "none");

});

function renderMemoData(data) {
    return {
        remarks: data.type !== "OP" ? data.remarks : data.memo_number,
        showRelease: data.type !== "OP"
    };
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "2-digit"
    });
}

document.addEventListener("DOMContentLoaded", function () {

    let activeRow = null;

    document.addEventListener("click", function (e) {

        const drawer = document.getElementById("memoDrawer");

        if (
            e.target.closest(".action-menu") ||
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest("input")
        ) {
            return;
        }

        const row = e.target.closest(".memo-row");

        if (row) {

            if (activeRow === row) {
                closeDrawer();
                return;
            }

            document.querySelectorAll(".memo-row")
                .forEach(r => r.classList.remove("active-row"));

            row.classList.add("active-row");
            activeRow = row;

            const memoData = renderMemoData(row.dataset);

            document.getElementById("drawerSubject").innerText = row.dataset.subject || "-";
            document.getElementById("drawerNumber").innerText = row.dataset.serial || "-";
            document.getElementById("drawerDate").innerText = formatDate(row.dataset.date);

            document.getElementById("drawerRemarks").innerText = memoData.remarks || "-";

            document.getElementById("drawerFrom").innerText = row.dataset.from || "-";
            document.getElementById("drawerForwarded").innerText = row.dataset.forwarded || "-";

            document.getElementById("drawerNotes").innerText = row.dataset.notes || "-";
            document.getElementById("drawerReleasedTo").innerText = row.dataset.released_to || "-";
            const releasedDate = row.dataset.released_date;

            document.getElementById("drawerReleasedDate").innerText =
                releasedDate && releasedDate !== "None" && releasedDate !== "null"
                    ? formatDate(releasedDate)
        : "N/A";
            const releaseRow = document.querySelector(".drawer-release-row");
            releaseRow.style.display = memoData.showRelease ? "flex" : "none";

            const threadId = row.dataset.thread;
            const relatedList = document.getElementById("relatedMemos");
            relatedList.innerHTML = "";

            const related = [];

            document.querySelectorAll(".memo-row").forEach(r => {
                if (r.dataset.thread === threadId) {
                    related.push(r);
                }
            });

            related.sort((a, b) =>
                new Date(a.dataset.date) - new Date(b.dataset.date)
            );

            related.forEach((r) => {

                const wrapper = document.createElement("li");
                wrapper.classList.add("memo-collapse");

                const isActive = r === row;
                const itemData = renderMemoData(r.dataset);

                const header = document.createElement("div");
                header.classList.add("memo-collapse-header");

                header.innerHTML = `
                    <span>#${r.dataset.serial || "-"}</span>
                    <span>${formatDate(r.dataset.date)}</span>
                    <span class="toggle-icon">${isActive ? "▼" : "▶"}</span>
                `;

                const content = document.createElement("div");
                content.classList.add("memo-collapse-body");
                content.style.display = isActive ? "block" : "none";

                content.innerHTML = `
                    <span class="badge badge-urgent">${itemData.remarks || "-"}</span>

                    <h3 class="drawer-subject">${r.dataset.subject || "-"}</h3>

                    <div class="drawer-meta">
                        <p>From: ${r.dataset.from || "-"}</p>
                        <p>Forwarded by: ${r.dataset.forwarded || "-"}</p>
                    </div>

                    <div class="drawer-notes">
                        Notes: ${r.dataset.notes || "-"}
                    </div>

                    ${itemData.showRelease ? `
                    <div class="drawer-release-row">
                        <div class="release-col">
                            <span class="text-secondary">Released to:</span>
                            <span>${r.dataset.released_to || "-"}</span>
                        </div>
                        <div class="release-col">
                            <span class="text-secondary">Released Date:</span>
                            <span>
                                ${
                                    r.dataset.released_date &&
                                    r.dataset.released_date !== "None" &&
                                    r.dataset.released_date !== "null"
                                        ? formatDate(r.dataset.released_date)
                                        : "N/A"
                                }
                            </span>
                        </div>
                    </div>
                    ` : ""}
                `;

                header.addEventListener("click", () => {
                    const isOpen = content.style.display === "block";
                    content.style.display = isOpen ? "none" : "block";
                    header.querySelector(".toggle-icon").innerText = isOpen ? "▶" : "▼";
                });

                content.addEventListener("click", () => {
                    r.click();
                });

                wrapper.appendChild(header);
                wrapper.appendChild(content);
                relatedList.appendChild(wrapper);
            });

            drawer.classList.add("active");
            return;
        }


        const isInsideDrawer = drawer && drawer.contains(e.target);

        if (!isInsideDrawer) {
            closeDrawer();
        }

    });

    window.closeDrawer = function () {
        const drawer = document.getElementById("memoDrawer");

        if (drawer) drawer.classList.remove("active");

        document.querySelectorAll(".memo-row")
            .forEach(r => r.classList.remove("active-row"));

        activeRow = null;
    };

});



/* =========================
HOLIDAY FUNCTIONS
========================= */


function renderHolidayCard(holiday){

const panel=document.querySelector('.holiday-panel');

const card=document.createElement('div');

card.className='holiday-card';

card.innerHTML=`
<iconify-icon icon="mdi:calendar"></iconify-icon>
<div>
<div class="holiday-top">
<span class="holiday-title">${holiday.title}</span>
<span class="holiday-badge">${holiday.badge}</span>
</div>
<p>${holiday.desc}</p>
</div>
`;

panel.insertBefore(card,panel.firstChild);

}

function loadHolidays(){

const holidays=JSON.parse(localStorage.getItem('holidays')||'[]');

holidays.forEach(renderHolidayCard);

}


function updateFormFields() {
    const type = document.getElementById("source_type_outside").value;

    const memoNumberGroup = document.getElementById("memoNumberGroup");
    const remarksGroup = document.getElementById("remarksGroup");
    const releaseSection = document.getElementById("releaseSection");

    const fromInput = document.getElementById("memoFrom");
    const forwardedInput = document.getElementById("memoForwarded");

    if (type === "OP") {

        memoNumberGroup.style.display = "block";

        remarksGroup.style.display = "none";
        releaseSection.style.display = "none";

        fromInput.value = "OP";
        forwardedInput.value = "RECORDS";

        fromInput.readOnly = true;
        forwardedInput.readOnly = true;

        fromInput.classList.add("locked");
        forwardedInput.classList.add("locked");

    } else {

        memoNumberGroup.style.display = "none";

        remarksGroup.style.display = "block";
        releaseSection.style.display = "flex"; // because it's form-row

        fromInput.readOnly = false;
        forwardedInput.readOnly = false;

        fromInput.classList.remove("locked");
        forwardedInput.classList.remove("locked");

        fromInput.value = "";
        forwardedInput.value = "";

        document.getElementById("memoNumber").value = "";
    }

    const hidden = document.getElementById("hiddenSourceType");
    if (hidden) {
        hidden.value = type;
    }
}

let editingSeries=null;
let deleteSeries=null;
let deleteRow=null;
let deleteId = null;

function openAddMemo() {
    const modal = document.getElementById("addMemoModal");
    const select = document.getElementById("source_type_outside");
    const hidden = document.getElementById("hiddenSourceType");

    if (!select.value) {
        select.value = currentType;
    }

    hidden.value = select.value;

    updateFormFields();

    modal.classList.add("show");
}
function openEditMemo(){
  const modal = document.getElementById("editMemoModal");
  console.log("Opening edit modal", modal);
  modal.classList.add("show");
}
function closeModals(){
  document.querySelectorAll(".modal").forEach(modal => {
    modal.classList.remove("show");
  });
}
document.addEventListener("click", function(e) {
  if (e.target.classList.contains("modal")) {
    closeModals();
  }
});

function showSuccessModal(message) {
    const modal = document.getElementById("successModal");
    document.getElementById("successMessage").textContent = message;
    modal.classList.add("show");

    setTimeout(() => {
        modal.classList.remove("show");
    }, 1500);
}

function closeSuccessModal() {
    document.getElementById("successModal").classList.remove("show");
}

function showErrorModal(message) {
    const modal = document.getElementById("errorModal");
    document.getElementById("errorMessage").textContent = message;
    modal.classList.add("show");
}

function closeErrorModal() {
    document.getElementById("errorModal").classList.remove("show");
}
/* ADD MEMO */
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("memo_form");

    if (form) {
        form.addEventListener("submit", async function (e) {
            console.log("ADD FORM SUBMIT"); // debug
            e.preventDefault();

            const formData = new FormData(form);

            const from = formData.get("from_office")?.trim();
            const subject = formData.get("subject")?.trim();

            if (!from || !subject) {
                alert("Please fill From and Subject");
                return;
            }

            await saveItem("remarks", document.getElementById("memoRemarks").value);
            await saveItem("from", document.getElementById("memoFrom").value);
            await saveItem("forwarded", document.getElementById("memoForwarded").value);
            await saveItem("released_to", document.getElementById("memoReleaseTo").value.trim());

            try {
                const res = await fetch("/secretary/new", {
                    method: "POST",
                    body: formData
                });

                const data = await res.json();

                if (!res.ok) {
                    showErrorModal(data.error || "Something went wrong");
                    return;
                }

                if (data.success) {
                    form.reset();
                    fetchTable();
                    showSuccessModal("Memo added successfully!");
                }

            } catch (err) {
                console.error("ERROR:", err);
            }
        });
    }

});

document.addEventListener('click', function(e) {
    const btn = e.target.closest(".update-new-btn, .update-btn");
    if (!btn) return;

    const form = document.getElementById("editMemoForm");
    const title = document.getElementById("editMemoTitle");

    const id = btn.getAttribute("data-id");

    if (!id) {
        console.error("Missing ID", btn);
        return;
    }

    title.textContent = btn.classList.contains("update-new-btn")
        ? "Update Memo"
        : "Edit Memo";

    form.dataset.actionUrl = btn.classList.contains("update-btn")
        ? `/secretary/edit/${id}`
        : `/secretary/update/${id}`;

    console.log("SET URL:", form.dataset.actionUrl);

    const sourceType = btn.dataset.source_type;
    console.log("RAW ID:", btn.dataset.id);
    console.log("TYPE:", typeof btn.dataset.id);
    const memoFrom = document.getElementById("editMemoFrom");
    const memoForwarded = document.getElementById("editMemoForwarded");
    const memoSubject = document.getElementById("editMemoSubject");
    const memoDate = document.getElementById("editMemoDate");
    const remarksRow = document.getElementById("editRemarksRow");
    const releaseRow = document.getElementById("editReleaseRow");
    const memoNumberRow = document.getElementById("editMemoNumberRow");
    
    if (btn.classList.contains("update-new-btn")) {
        title.textContent = "Update Memo";
    } else {
        title.textContent = "Edit Memo";
    }
    memoFrom.value = btn.dataset.from || "";
    memoForwarded.value = btn.dataset.forwarded || "";
    memoSubject.value = btn.dataset.subject || "";

    document.getElementById("editMemoRemarks").value = btn.dataset.remarks || "";
    document.getElementById("editMemoNotes").value = btn.dataset.notes || "";
    memoDate.value = btn.dataset.date || "";
    document.getElementById("editMemoReleaseTo").value = btn.dataset.released_to || "";
    document.getElementById("editMemoReleaseDate").value = btn.dataset.released_date || "";
    document.getElementById("editMemoNumber").value = btn.dataset.number || "";

    if (sourceType === "OP") {

        remarksRow.style.display = "none";
        releaseRow.style.display = "none";
        memoNumberRow.style.display = "flex";  
    } else {
        memoNumberRow.style.display = "none";
        remarksRow.style.display = "flex";
        releaseRow.style.display = "flex";

    }

    if (btn.classList.contains("update-new-btn")) {

        memoFrom.disabled = true;
        memoForwarded.disabled = true;
        memoSubject.disabled = true;
        memoNumberRow.disabled = true;

        memoFrom.classList.add("locked");
        memoForwarded.classList.add("locked");
        memoSubject.classList.add("locked");
        memoDate.classList.add("locked");
        memoNumberRow.classList.add("locked");

    } 

    else {

        memoSubject.disabled = false;
        memoNumberRow.disabled = false;

        memoSubject.classList.remove("locked");
        memoDate.classList.remove("locked");
        memoNumberRow.classList.remove("locked");   

        if (sourceType === "OP") {
            memoFrom.disabled = true;
            memoForwarded.disabled = true;

            memoFrom.classList.add("locked");
            memoForwarded.classList.add("locked");
        } else {
            memoFrom.disabled = false;
            memoForwarded.disabled = false;

            memoFrom.classList.remove("locked");
            memoForwarded.classList.remove("locked");
        }
    }


    if (btn.classList.contains("update-btn")) {
        form.action = `/secretary/edit/${id}`;
    } else {
        form.action = `/secretary/update/${id}`;
    }

    openEditMemo();
});

document.addEventListener("DOMContentLoaded", function () {

    const editForm = document.getElementById("editMemoForm");

    if (editForm) {
        editForm.addEventListener("submit", function(e) {
            e.preventDefault();

            const form = document.getElementById("editMemoForm");
            const url = form.dataset.actionUrl;
            const formData = new FormData(form);

            if (!url) {
                console.error("No URL set before submit");
                return;
            }

            console.log("Submitting to:", url);

            fetch(url, {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    console.error("Server error:", data.error);
                }
            })
            .catch(err => {
                console.error("Fetch error:", err);
            });
        });
    }

});

let rowToDelete = null;
let memoIdToDelete = null;

document.addEventListener("DOMContentLoaded", function() {
    document.addEventListener('click', function(e){ 
        const btn = e.target.closest(".delete-btn");
        if(!btn) return;

        console.log("Delete button clicked!", btn.dataset.id);

        rowToDelete = btn.closest("tr");
        memoIdToDelete = btn.dataset.id;

        const modal = document.getElementById("deleteConfirmModal");
        if(modal){
            modal.classList.add("show");  
            console.log("Modal opened");
        } else {
            console.error("Modal not found!");
        }
    });
});

function confirmDelete() {
    if (!memoIdToDelete) return;

    fetch(`/secretary/delete/${memoIdToDelete}`, { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            if(rowToDelete){
                rowToDelete.classList.add("row-fade");
                setTimeout(() => rowToDelete.remove(), 300);
            }
        } else {
            alert(data.error || "Delete failed");
        }
    })
    .catch(err => console.error(err))
    .finally(() => closeDeleteConfirm());
}

function closeDeleteConfirm(){
    const modal = document.getElementById("deleteConfirmModal");
    if(modal){
        modal.classList.remove("show"); 
    }

    rowToDelete = null;
    memoIdToDelete = null;
}



/* ===========
AUTOCOMPLETE
==============*/

async function fetchList(type) {
    const res = await fetch(`/secretary/autocomplete/${type}`);
    return await res.json();
}

async function saveItem(type, value) {
    if (!value) return;

    value = value.trim();
    if (!value) return;

    await fetch("/secretary/autocomplete", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ type: type, value: value })
    });
}

async function deleteItem(type, value) {
    await fetch("/secretary/autocomplete", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ type: type, value: value })
    });
}

function setupAutocomplete(inputId, dropdownId, type) {

    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    if (!input || !dropdown) {
        console.warn(`Autocomplete skipped: ${inputId}`);
        return;
    }

    input.addEventListener("focus", load);
    input.addEventListener("input", load);

    async function load() {
        const list = await fetchList(type);
        const filter = input.value.toLowerCase();

        dropdown.innerHTML = "";

        const filtered = list.filter(item =>
            item.toLowerCase().includes(filter)
        );

        if (!filtered.length) {
            dropdown.style.display = "none";
            return;
        }

        filtered.forEach(item => {
            const div = document.createElement("div");
            div.classList.add("dropdown-item");

            div.innerHTML = `
                <span class="item-text">${item}</span>
                <span class="delete-btn">✕</span>
            `;

            div.querySelector(".item-text").onclick = () => {
                input.value = item;
                dropdown.style.display = "none";
            };

            div.querySelector(".delete-btn").onclick = async (e) => {
                e.stopPropagation();
                await deleteItem(type, item);
                load();
            };

            dropdown.appendChild(div);
        });

        dropdown.style.display = "block";
    }
}

if (!window._autocompleteClickBound) {
    document.addEventListener("click", (e) => {
        document.querySelectorAll(".dropdown").forEach(dropdown => {
            const input = dropdown.previousElementSibling;

            if (input &&
                !input.contains(e.target) &&
                !dropdown.contains(e.target)) {
                dropdown.style.display = "none";
            }
        });
    });

    window._autocompleteClickBound = true;
}


document.addEventListener("DOMContentLoaded", () => {

    setupAutocomplete("memoRemarks", "remarksDropdown", "remarks");
    setupAutocomplete("memoFrom", "fromDropdown", "from");
    setupAutocomplete("memoForwarded", "forwardedDropdown", "forwarded");
    setupAutocomplete("memoReleaseTo", "releaseToDropdown", "released_to");
    
    setupAutocomplete("editMemoFrom", "editFromDropdown", "from");
    setupAutocomplete("editMemoForwarded", "editForwardedDropdown", "forwarded");
    setupAutocomplete("editMemoRemarks", "editRemarksDropdown", "remarks");
    setupAutocomplete("editMemoReleaseTo", "editReleaseToDropdown", "released_to");

});