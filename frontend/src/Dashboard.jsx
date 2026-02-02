import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { authService } from './api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

/* Register Chart.js components */
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Dashboard() {
  const navigate = useNavigate();

  /* Upload state */
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  /* Summary state */
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState('');

  /* History state */
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState('');

  /* Animation state */
  const [isLoaded, setIsLoaded] = useState(false);
  const hasAnimated = useRef(false);

  /* Fetch summary - wrapped in useCallback */
  const fetchSummary = useCallback(async () => {
    setSummaryLoading(true);
    setSummaryError('');

    try {
      const res = await api.get('/api/summary/');
      setSummary(res.data);
    } catch {
      setSummary(null);
      setSummaryError('Failed to fetch summary data.');
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  /* Fetch history - wrapped in useCallback */
  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError('');

    try {
      const res = await api.get('/api/history/');
      setHistory(res.data.datasets || []);
    } catch {
      setHistory([]);
      setHistoryError('Failed to fetch history.');
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  /* Listen for auth:logout event from axios interceptor */
  useEffect(() => {
    const handleLogout = () => {
      navigate('/login');
    };

    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, [navigate]);

  /* Load summary & history on page load */
  useEffect(() => {
    fetchSummary();
    fetchHistory();
    
    /* Trigger fade-in animations after mount */
    if (!hasAnimated.current) {
      setTimeout(() => setIsLoaded(true), 100);
      hasAnimated.current = true;
    }
  }, [fetchSummary, fetchHistory]);

  /* Handle logout */
  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  /* File select */
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setUploadMessage('');
    setUploadError('');
  };

  /* Upload CSV */
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a CSV file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setIsUploading(true);
    setUploadError('');
    setUploadMessage('');

    try {
      const res = await api.post('/api/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setUploadMessage(res.data.message || 'CSV uploaded successfully!');
      setSelectedFile(null);
      document.getElementById('file-input').value = '';

      /* Refresh dashboard */
      fetchSummary();
      fetchHistory();

    } catch (err) {
      setUploadError(err.response?.data?.error || 'Upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="app-container">
      <header className={`app-header ${isLoaded ? 'fade-in' : ''}`}>
        <div className="header-content">
          <div>
            <h1>🧪 Chemical Equipment Visualizer</h1>
            <p>Upload CSV files and visualize equipment data</p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </header>

      <main className="main-content">

        {/* Upload */}
        <section className={`section upload-section ${isLoaded ? 'fade-slide-in' : ''}`} style={{ animationDelay: '0.1s' }}>
          <h2>📤 Upload CSV File</h2>

          <div className="upload-wrapper">
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                className="file-input"
                accept=".csv"
                onChange={handleFileChange}
              />
            </div>

            <button
              className="upload-btn"
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? '⏳ Uploading...' : '🚀 Upload CSV'}
            </button>
          </div>

          {selectedFile && <p className="file-selected">{selectedFile.name}</p>}
          {uploadMessage && <p className="success-message">{uploadMessage}</p>}
          {uploadError && <p className="error-message">{uploadError}</p>}

          <p className="hint">
            Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
          </p>
        </section>

        {/* Summary */}
        <section className={`section summary-section ${isLoaded ? 'fade-slide-in' : ''}`} style={{ animationDelay: '0.2s' }}>
          <h2>📊 Summary Dashboard</h2>

          {summaryLoading && <p className="loading-state">Loading summary...</p>}
          {summaryError && <p className="error-message">{summaryError}</p>}

          {summary && (
            <div className="summary-cards">
              <div className="card" style={{ animationDelay: '0.25s' }}>
                <h3>Total Records</h3>
                <p className="card-value">{summary.total_rows}</p>
              </div>
              <div className="card" style={{ animationDelay: '0.3s' }}>
                <h3>Avg Flowrate</h3>
                <p className="card-value">{summary.averages.flowrate}</p>
              </div>
              <div className="card" style={{ animationDelay: '0.35s' }}>
                <h3>Avg Pressure</h3>
                <p className="card-value">{summary.averages.pressure}</p>
              </div>
              <div className="card" style={{ animationDelay: '0.4s' }}>
                <h3>Avg Temperature</h3>
                <p className="card-value">{summary.averages.temperature}</p>
              </div>
            </div>
          )}
        </section>

        {/* Charts */}
        {summary && (
          <section className={`section charts-section ${isLoaded ? 'fade-slide-in' : ''}`} style={{ animationDelay: '0.3s' }}>
            <h2>📈 Data Visualization</h2>

            <div className="charts-grid">
              <div className="chart-wrapper">
                <h3>Average Values Comparison</h3>
                <div className="chart-canvas-container">
                  <Bar 
                    data={{
                      ...summary.averages_chart,
                      datasets: summary.averages_chart.datasets.map(ds => ({
                        ...ds,
                        backgroundColor: ['#a5b4fc', '#93c5fd', '#86efac'],
                        borderColor: ['#818cf8', '#60a5fa', '#4ade80'],
                        borderWidth: 1,
                        borderRadius: 8,
                        barThickness: 48
                      }))
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      devicePixelRatio: 2,
                      layout: {
                        padding: { top: 10, bottom: 10 }
                      },
                      plugins: {
                        legend: { display: false },
                        tooltip: {
                          backgroundColor: 'rgba(55, 65, 81, 0.95)',
                          titleFont: { size: 13, weight: '500' },
                          bodyFont: { size: 12 },
                          padding: 12,
                          cornerRadius: 8,
                          displayColors: true,
                          boxPadding: 6
                        }
                      },
                      scales: {
                        y: { 
                          beginAtZero: true,
                          grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
                          ticks: { font: { size: 11 }, color: '#9ca3af', padding: 8 }
                        },
                        x: {
                          grid: { display: false },
                          ticks: { font: { size: 11, weight: '500' }, color: '#6b7280', padding: 8 }
                        }
                      }
                    }} 
                  />
                </div>
              </div>

              <div className="chart-wrapper">
                <h3>Equipment Type Distribution</h3>
                <div className="chart-canvas-container chart-pie-container">
                  <Pie 
                    data={{
                      ...summary.equipment_types_chart,
                      datasets: summary.equipment_types_chart.datasets.map(ds => ({
                        ...ds,
                        backgroundColor: ['#a5b4fc', '#93c5fd', '#86efac', '#fcd34d', '#fca5a5', '#c4b5fd'],
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        hoverOffset: 6
                      }))
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      devicePixelRatio: 2,
                      layout: {
                        padding: { top: 10, bottom: 20 }
                      },
                      plugins: {
                        legend: { 
                          position: 'bottom',
                          labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 11, weight: '500' },
                            color: '#6b7280'
                          }
                        },
                        tooltip: {
                          backgroundColor: 'rgba(55, 65, 81, 0.95)',
                          titleFont: { size: 13, weight: '500' },
                          bodyFont: { size: 12 },
                          padding: 12,
                          cornerRadius: 8
                        }
                      }
                    }} 
                  />
                </div>
              </div>
            </div>
          </section>
        )}

        {/* History */}
        <section className={`section history-section ${isLoaded ? 'fade-slide-in' : ''}`} style={{ animationDelay: '0.4s' }}>
          <h2>📁 Upload History</h2>

          {historyLoading && <p className="loading-state">Loading history...</p>}
          {historyError && <p className="error-message">{historyError}</p>}

          {!historyLoading && history.length > 0 && (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>File Name</th>
                    <th>Uploaded At</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, i) => (
                    <tr key={i}>
                      <td>{i + 1}</td>
                      <td>{h.file_name.split('\\').pop()}</td>
                      <td>{h.uploaded_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!historyLoading && history.length === 0 && (
            <p className="no-data">No uploads yet. Upload a CSV file to get started.</p>
          )}
        </section>
      </main>

      <footer className={`app-footer ${isLoaded ? 'fade-in' : ''}`}>
        Chemical Equipment Visualizer © 2026
      </footer>
    </div>
  );
}

export default Dashboard;
