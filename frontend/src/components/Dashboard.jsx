import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const API_BASE = 'http://127.0.0.1:8000';

export default function Dashboard({ userId }) {
  const [data, setData] = useState({
    time_distribution: {},
    focus_trend: [],
    context_switches: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/dashboard/${userId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        setData(json);
        setError('');
      } catch (e) {
        setError(`Failed to load dashboard: ${e.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [userId]);

  // Transform distribution object into array
  const distData = Object.entries(data.time_distribution).map(
    ([category, value]) => ({ category, value })
  );

  return (
    <div className="space-y-8">
      {loading && <p>Loading dashboard…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && (
        <>
          {/* 1️⃣ Time Spent per Category */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">⏳ Time by Category</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={distData} margin={{ top: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" name="Hours" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 2️⃣ Focus Time Trend */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">📈 Deep Work Trend (7 days)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data.focus_trend} margin={{ top: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'hrs', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="deep_work_hours" stroke="#82ca9d" name="Deep Work" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 3️⃣ Context Switch Frequency */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">💥 Context Switches per Day</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.context_switches} margin={{ top: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="switches" fill="#ffc658" name="Switches" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}