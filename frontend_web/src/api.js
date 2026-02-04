const API_BASE = process.env.REACT_APP_API_URL || 'https://fossee-webbasedapp-1.onrender.com/api';

export function getAuthHeaders() {
  const user = localStorage.getItem('api_user');
  const pass = localStorage.getItem('api_pass');
  if (user && pass) {
    return {
      Authorization: 'Basic ' + btoa(`${user}:${pass}`),
    };
  }
  return {};
}

export async function uploadCSV(file, name) {
  const form = new FormData();
  form.append('file', file);
  if (name) form.append('name', name);
  const res = await fetch(`${API_BASE}/upload/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || 'Upload failed');
  }
  return res.json();
}

export async function getSummary(datasetId) {
  const res = await fetch(`${API_BASE}/summary/${datasetId}/`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to load summary');
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history/`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}

export function getPDFReportUrl(datasetId) {
  return `${API_BASE}/report/${datasetId}/pdf/`;
}

export async function downloadPDFReport(datasetId) {
  const url = getPDFReportUrl(datasetId);
  const opts = { headers: getAuthHeaders() };
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error('Failed to download PDF');
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `equipment_report_${datasetId}.pdf`;
  a.click();
  URL.revokeObjectURL(a.href);
}

export function setBasicAuth(username, password) {
  if (username) localStorage.setItem('api_user', username);
  else localStorage.removeItem('api_user');
  if (password) localStorage.setItem('api_pass', password);
  else localStorage.removeItem('api_pass');
}

export function clearBasicAuth() {
  localStorage.removeItem('api_user');
  localStorage.removeItem('api_pass');
}
