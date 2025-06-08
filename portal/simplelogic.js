/* This file controls simple logical elements for the HTML Portal in order to keep clean files that don't interpolate other languages.
  If this setup is causing performance issues, cut & copy the relavent tags from this file into a <script> element in every HTML file,
  and delete the <script src="simplelogic.js"></script> in every file as well. */


// Authentication helper
function checkSession() {
  if (!document.body.classList.contains('noauth')) {
    if (!document.cookie.includes('session=')) {
      window.location.href = '/';
    }
  }
}


// Live Clock
function updateClock() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const strTime = hours.toString().padStart(2, '0') + ':' +
        minutes.toString().padStart(2, '0') + ':' +
        seconds.toString().padStart(2, '0') + ' ' + ampm;
    const clockElement = document.getElementById('clockTime');
    if (clockElement) clockElement.textContent = strTime;
}
setInterval(updateClock, 1000);
window.onload = () => {
  updateClock();
  setupDarkMode();
  checkSession();
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js');
  }
}

// Dark Mode Toggle
function setupDarkMode() {
  const toggle = document.getElementById("themeToggle");
  const body = document.body;

  if (!toggle) return;

  // Load saved mode
  if (localStorage.getItem("darkMode") === "true") {
    body.classList.add("dark-mode");
    toggle.checked = true;
  }

  toggle.addEventListener("change", () => {
    if (toggle.checked) {
      body.classList.add("dark-mode");
      localStorage.setItem("darkMode", "true");
    } else {
      body.classList.remove("dark-mode");
      localStorage.setItem("darkMode", "false");
    }
  });
}

// Device Information Requester

// Mist Scheduling Handler
function populateTimeOptions() {
  const timeOptions = ["None"];
  for (let h = 1; h <= 12; h++) {
    for (let m = 0; m < 60; m += 15) {
      const mm = m === 0 ? "00" : m.toString().padStart(2, "0");
      timeOptions.push(`${h}:${mm}`);
    }
  }

  document.querySelectorAll(".timeDropdown").forEach(drop => {
    drop.innerHTML = "";
    timeOptions.forEach(t => {
      const opt = document.createElement("option");
      opt.textContent = t;
      opt.value = t;
      drop.appendChild(opt);
    });
  });

  document.querySelectorAll(".ampmDropdown").forEach(drop => {
    drop.innerHTML = "";
    ["AM", "PM"].forEach(period => {
      const opt = document.createElement("option");
      opt.textContent = period;
      opt.value = period;
      drop.appendChild(opt);
    });
  });
}

function toggleDay(day) {
  const checkbox = document.getElementById(`${day}-check`);
  const container = document.getElementById(`${day}-times`);
  const selects = container.querySelectorAll("select");

  selects.forEach(select => {
    select.disabled = !checkbox.checked;
    select.style.opacity = checkbox.checked ? "1" : "0.5";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  populateTimeOptions();

  const days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
  days.forEach(day => {
    toggleDay(day);
    const checkbox = document.getElementById(`${day}-check`);
    if (checkbox) {
      checkbox.addEventListener("change", () => toggleDay(day));
    }
  });

  const form = document.getElementById('scheduleForm');
  if (form) form.addEventListener('submit', saveSchedule);

  const mistToggle = document.getElementById('mistToggle');
  const autoMistToggle = document.getElementById('autoMistToggle');
  if (mistToggle && autoMistToggle) {
    mistToggle.addEventListener('change', sendMisting);
    autoMistToggle.addEventListener('change', sendMisting);
  }

  loadConfig();
});



// Misting (Automated & Manual) Alert
function alertBox() {
  const mistToggle = document.getElementById('mistToggle');
  const autoMistToggle = document.getElementById('autoMistToggle');

  if (mistToggle.checked && !autoMistToggle.checked) {
    alert("Mist is currently running manually. Turn this switch off to stop it. Do not leave it active for long periods.");
  } else if (!mistToggle.checked && autoMistToggle.checked) {
    alert("Automated misting is enabled. It will activate on the schedule you've set.");
  } else if (mistToggle.checked && autoMistToggle.checked) {
    alert("Manual misting is currently active, and automation is also enabled. Be sure to turn off manual misting when no longer needed.");
  } else {
    alert("Both misting options are currently disabled. No misting will occur unless enabled.");
  }
}

async function sendMisting() {
  const enabled = document.getElementById('autoMistToggle').checked;
  const active = document.getElementById('mistToggle').checked;
  try {
    await fetch('/api/misting', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({enabled, active})
    });
  } catch (e) {
    console.error('Failed to update misting', e);
  }
}

function minsToTime(mins) {
  const h24 = Math.floor(mins / 60);
  const m = mins % 60;
  const ampm = h24 >= 12 ? 'PM' : 'AM';
  let h12 = h24 % 12;
  if (h12 === 0) h12 = 12;
  return {time: `${h12}:${m.toString().padStart(2,'0')}`, ampm};
}

async function loadConfig() {
  try {
    const resp = await fetch('/api/config');
    const cfg = await resp.json();
    const days = ['sun','mon','tue','wed','thu','fri','sat'];
    if ('automation_enabled' in cfg) {
      const auto = document.getElementById('autoMistToggle');
      if (auto) auto.checked = cfg.automation_enabled;
    }
    if ('active' in cfg) {
      const mist = document.getElementById('mistToggle');
      if (mist) mist.checked = cfg.active;
    }
    if (cfg.schedule) {
      days.forEach(day => {
        const times = cfg.schedule[day] || [];
        const checkbox = document.getElementById(`${day}-check`);
        const slots = document.querySelectorAll(`#${day}-times .timeSlot`);
        const valid = times.filter(t => t > 0);
        if (checkbox) checkbox.checked = valid.length > 0;
        valid.forEach((val, idx) => {
          if (slots[idx]) {
            const {time, ampm} = minsToTime(val);
            slots[idx].querySelector('.timeDropdown').value = time;
            slots[idx].querySelector('.ampmDropdown').value = ampm;
          }
        });
        for (let i = valid.length; i < slots.length; i++) {
          slots[i].querySelector('.timeDropdown').value = 'None';
          slots[i].querySelector('.ampmDropdown').value = 'AM';
        }
        toggleDay(day);
      });
    }
  } catch (e) {
    console.error('Failed to load config', e);
  }
}

function gatherSchedule() {
  const out = {};
  const days = ['sun','mon','tue','wed','thu','fri','sat'];
  days.forEach(day => {
    const checkbox = document.getElementById(`${day}-check`);
    if (!checkbox || !checkbox.checked) return;
    const slots = document.querySelectorAll(`#${day}-times .timeSlot`);
    const times = [];
    slots.forEach(slot => {
      const timeVal = slot.querySelector('.timeDropdown').value;
      const ampm = slot.querySelector('.ampmDropdown').value;
      if (timeVal !== 'None') {
        let [h, m] = timeVal.split(':').map(n => parseInt(n,10));
        if (ampm === 'PM' && h !== 12) h += 12;
        if (ampm === 'AM' && h === 12) h = 0;
        times.push(`${h}:${m.toString().padStart(2,'0')}`);
      }
    });
    if (times.length) out[day] = times;
  });
  return out;
}

async function saveSchedule(event) {
  event.preventDefault();
  const schedule = gatherSchedule();
  try {
    await fetch('/api/schedule', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({schedule})
    });
    alert('Schedule saved.');
  } catch (e) {
    console.error('Failed to save schedule', e);
    alert('Failed to save schedule');
  }
}

