async function fetchForecast(lat, lon) {
  try {
    const pointResp = await fetch(`https://api.weather.gov/points/${lat},${lon}`);
    const point = await pointResp.json();
    const forecastUrl = point.properties.forecast;
    const forecastResp = await fetch(forecastUrl);
    const forecast = await forecastResp.json();
    return forecast.properties.periods;
  } catch (e) {
    console.error('Failed to fetch forecast', e);
    return [];
  }
}

function displayForecast(periods) {
  const container = document.getElementById('forecastContainer');
  container.innerHTML = '';
  periods.slice(0, 7).forEach(p => {
    const div = document.createElement('div');
    div.className = 'forecastDay';
    div.innerHTML = `<strong>${p.name}</strong><br>${p.temperature}°${p.temperatureUnit}<br>${p.shortForecast}<br>Precip: ${p.probabilityOfPrecipitation.value || 0}%`;
    container.appendChild(div);
  });
}

async function handleForm(e) {
  e.preventDefault();
  const lat = document.getElementById('lat').value.trim();
  const lon = document.getElementById('lon').value.trim();
  const periods = await fetchForecast(lat, lon);
  if (!periods.length) return;

  displayForecast(periods);

  const maxProb = periods.reduce((m, p) => Math.max(m, p.probabilityOfPrecipitation.value || 0), 0);
  if (maxProb >= 60) {
    document.getElementById('autoMessage').textContent = 'Automation will skip misting due to high precipitation chance.';
  } else {
    document.getElementById('autoMessage').textContent = '';
  }

  await fetch('/api/weather_log', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({timestamp: Date.now(), periods: periods.slice(0,7)})
  });
  loadLog();
}

async function loadLog() {
  try {
    const resp = await fetch('/api/weather_log');
    const data = await resp.json();
    const list = document.getElementById('weatherLog');
    list.innerHTML = '';
    (data.log || []).forEach(entry => {
      const li = document.createElement('li');
      const date = new Date(entry.timestamp);
      const p = entry.periods && entry.periods[0];
      const desc = p ? p.shortForecast : 'n/a';
      li.textContent = `${date.toLocaleDateString()} - ${desc}`;
      list.appendChild(li);
    });
  } catch (e) {
    console.error('Failed to load log', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('locationForm');
  if (form) {
    form.addEventListener('submit', handleForm);
  }
  loadLog();
});
