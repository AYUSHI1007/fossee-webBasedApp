import React, { useState, useEffect, useCallback } from 'react';
import { uploadCSV, getHistory, setBasicAuth, clearBasicAuth, downloadPDFReport } from './api';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function App() {
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadName, setUploadName] = useState('');
  const [authModal, setAuthModal] = useState(false);
  const [authUser, setAuthUser] = useState(localStorage.getItem('api_user') || '');
  const [authPass, setAuthPass] = useState('');

  const loadHistory = useCallback(async () => {
    setError(null);
    try {
      const data = await getHistory();
      setHistory(data);
      if (data.length && !selected) setSelected(data[0]);
    } catch (e) {
      setError(e.message);
    }
  }, [selected]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await uploadCSV(file, uploadName || file.name);
      setHistory((h) => [result, ...h.slice(0, 4)]);
      setSelected(result);
      setUploadName('');
      e.target.value = '';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSubmit = (e) => {
    e.preventDefault();
    setBasicAuth(authUser, authPass);
    setAuthModal(false);
    setAuthPass('');
    loadHistory();
  };

  const typeDistributionChart = selected?.type_distribution
    ? {
        labels: Object.keys(selected.type_distribution),
        datasets: [
          {
            data: Object.values(selected.type_distribution),
            backgroundColor: ['#38bdf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'],
            borderWidth: 0,
          },
        ],
      }
    : null;

  const numericChart = selected?.raw_rows?.length
    ? (() => {
        const rows = selected.raw_rows;
        const labels = rows.map((r, i) => r['Equipment Name'] || `#${i + 1}`);
        return {
          labels: labels.length > 15 ? labels.slice(0, 15) : labels,
          datasets: [
            { label: 'Flowrate', data: (rows.length > 15 ? rows.slice(0, 15) : rows).map((r) => r.Flowrate), backgroundColor: 'rgba(56, 189, 248, 0.7)' },
            { label: 'Pressure', data: (rows.length > 15 ? rows.slice(0, 15) : rows).map((r) => r.Pressure), backgroundColor: 'rgba(52, 211, 153, 0.7)' },
            { label: 'Temperature', data: (rows.length > 15 ? rows.slice(0, 15) : rows).map((r) => r.Temperature), backgroundColor: 'rgba(251, 191, 36, 0.7)' },
          ],
        };
      })()
    : null;

  const [pdfLoading, setPdfLoading] = useState(false);
  const hasAuth = !!localStorage.getItem('api_user');

  const handleDownloadPDF = async () => {
    if (!selected) return;
    setPdfLoading(true);
    try {
      await downloadPDFReport(selected.id);
    } catch (e) {
      setError(e.message);
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <p className="tagline">Upload CSV • View summary & charts • Download PDF</p>
        <div className="header-actions">
          <button type="button" className="btn btn-ghost" onClick={() => setAuthModal(true)}>
            {hasAuth ? `Auth: ${authUser}` : 'Basic Auth'}
          </button>
          {hasAuth && (
            <button type="button" className="btn btn-ghost" onClick={() => { clearBasicAuth(); setAuthModal(false); loadHistory(); }}>
              Log out
            </button>
          )}
        </div>
      </header>

      {authModal && (
        <div className="modal-overlay" onClick={() => setAuthModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Basic Authentication</h3>
            <form onSubmit={handleAuthSubmit}>
              <input
                type="text"
                placeholder="Username"
                value={authUser}
                onChange={(e) => setAuthUser(e.target.value)}
                autoComplete="username"
              />
              <input
                type="password"
                placeholder="Password"
                value={authPass}
                onChange={(e) => setAuthPass(e.target.value)}
                autoComplete="current-password"
              />
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setAuthModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <main className="main">
        <section className="upload-section card">
          <h2>Upload CSV</h2>
          <p className="hint">Columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
          <div className="upload-row">
            <input
              type="text"
              placeholder="Dataset name (optional)"
              value={uploadName}
              onChange={(e) => setUploadName(e.target.value)}
              className="input-name"
            />
            <label className="btn btn-primary">
              {loading ? 'Uploading…' : 'Choose file'}
              <input type="file" accept=".csv" onChange={handleFileUpload} disabled={loading} hidden />
            </label>
          </div>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="history-section card">
          <h2>History (last 5)</h2>
          {history.length === 0 ? (
            <p className="muted">Upload a CSV to see history.</p>
          ) : (
            <ul className="history-list">
              {history.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className={`history-item ${selected?.id === item.id ? 'active' : ''}`}
                    onClick={() => setSelected(item)}
                  >
                    {item.name} — {item.total_count} rows
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {selected && (
          <>
            <section className="summary-section card">
              <h2>Summary — {selected.name}</h2>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="label">Total count</span>
                  <span className="value">{selected.total_count}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Avg Flowrate</span>
                  <span className="value">{selected.avg_flowrate != null ? selected.avg_flowrate : '—'}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Avg Pressure</span>
                  <span className="value">{selected.avg_pressure != null ? selected.avg_pressure : '—'}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Avg Temperature</span>
                  <span className="value">{selected.avg_temperature != null ? selected.avg_temperature : '—'}</span>
                </div>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ marginTop: '1rem' }}
                onClick={handleDownloadPDF}
                disabled={pdfLoading}
              >
                {pdfLoading ? 'Downloading…' : 'Download PDF report'}
              </button>
            </section>

            <section className="charts-section">
              {typeDistributionChart && (
                <div className="card chart-card">
                  <h3>Equipment type distribution</h3>
                  <div className="chart-wrap doughnut">
                    <Doughnut data={typeDistributionChart} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
                  </div>
                </div>
              )}
              {numericChart && (
                <div className="card chart-card">
                  <h3>Flowrate / Pressure / Temperature (sample)</h3>
                  <div className="chart-wrap bar">
                    <Bar
                      data={numericChart}
                      options={{
                        responsive: true,
                        scales: { y: { beginAtZero: true } },
                        plugins: { legend: { position: 'top' } },
                      }}
                    />
                  </div>
                </div>
              )}
            </section>

            <section className="table-section card">
              <h2>Data table</h2>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {selected.raw_rows?.[0] &&
                        Object.keys(selected.raw_rows[0]).map((k) => (
                          <th key={k}>{k}</th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(selected.raw_rows || []).map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((v, j) => (
                          <td key={j}>{v != null ? String(v) : '—'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
