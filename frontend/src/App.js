import React, { useState, useRef, useEffect, useCallback } from 'react';
import Dashboard from './components/Dashboard';

const API_BASE = 'http://127.0.0.1:8000';

// Helper to extract JSON from ```json ... ``` markdown
const extractJsonFromMarkdown = (mdString) => {
  const match = mdString.match(/```json\s*([\s\S]*?)```/);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch (e) {
    console.error('JSON parse error:', e);
    return null;
  }
};

// Configuration for coaching sections
const coachingConfig = {
  main_message:    { label: 'Summary',         icon: '📋', bg: 'bg-purple-100', text: 'text-purple-800' },
  specific_tips:   { label: 'Specific Tips',   icon: '💡', bg: 'bg-blue-50',   text: 'text-blue-800'   },
  time_management: { label: 'Time Management', icon: '⏰', bg: 'bg-green-50',  text: 'text-green-800'  },
  focus_strategies:{ label: 'Focus Strategies',icon: '🎯', bg: 'bg-yellow-50', text: 'text-yellow-800' },
  motivation:      { label: 'Motivation',      icon: '🚀', bg: 'bg-pink-50',   text: 'text-pink-800'   },
  next_week_goals: { label: 'Next Week Goals', icon: '📝', bg: 'bg-indigo-50', text: 'text-indigo-800' },
};

// Configuration for insights sections
const insightsConfig = {
  key_patterns:    { label: 'Key Patterns',    icon: '🔑', bg: 'bg-yellow-50', text: 'text-yellow-800' },
  anomalies:       { label: 'Anomalies',       icon: '⚠️', bg: 'bg-red-50',    text: 'text-red-800'   },
  trends:          { label: 'Trends',          icon: '📈', bg: 'bg-green-50',  text: 'text-green-800' },
  recommendations: { label: 'Recommendations', icon: '✅', bg: 'bg-blue-50',   text: 'text-blue-800'   },
};

// Configuration for voice insights sections
const voiceInsightsConfig = {
  productivity_indicators: { label: 'Productivity Indicators', icon: '✨', bg: 'bg-yellow-50', text: 'text-yellow-800' },
  time_mentions:           { label: 'Time Mentions',            icon: '⏳', bg: 'bg-blue-50',   text: 'text-blue-800'   },
  emotional_keywords:      { label: 'Emotional Keywords',       icon: '💬', bg: 'bg-pink-50',  text: 'text-pink-800'   },
  suggested_category:      { label: 'Suggested Category',       icon: '🗂️', bg: 'bg-green-50',  text: 'text-green-800'  },
};

const TimeCopApp = () => {
  const [userId, setUserId] = useState('user_001');
  const [activeTab, setActiveTab] = useState('analyze');
  const [userInput, setUserInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [voiceResult, setVoiceResult] = useState(null);
  const [memoryData, setMemoryData] = useState(null);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Initialize media recorder
  useEffect(() => {
    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then(stream => {
          const mediaRecorder = new MediaRecorder(stream);
          mediaRecorderRef.current = mediaRecorder;
          mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunksRef.current.push(e.data);
          };
          mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            audioChunksRef.current = [];
            await processVoiceInput(blob);
          };
        })
        .catch(err => {
          console.error('Microphone error', err);
          setError('Microphone access denied. Voice logging unavailable.');
        });
    }
  }, []);

  const startRecording = () => {
    if (mediaRecorderRef.current?.state === 'inactive') {
      audioChunksRef.current = [];
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError('');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');
      formData.append('user_id', userId);

      const res = await fetch(`${API_BASE}/voice-log`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setVoiceResult(await res.json());
      setError('');
    } catch (e) {
      setError(`Voice processing failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeProductivity = async () => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('user_input', userInput || 'How was my productivity this week?');
      formData.append('user_id', userId);

      const res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Parse the markdown JSON fields
      const parsedCoaching = data.coaching?.coaching
        ? extractJsonFromMarkdown(data.coaching.coaching)
        : null;
      const parsedInsights = data.insights?.insights
        ? extractJsonFromMarkdown(data.insights.insights)
        : null;

      setAnalysisResult({ ...data, parsedCoaching, parsedInsights });
      setError('');
    } catch (e) {
      setError(`Analysis failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const queryMemory = async (query = '') => {
    setIsLoading(true);
    try {
      const url = new URL(`${API_BASE}/memory/${userId}`);
      if (query) url.searchParams.append('query', query);
      url.searchParams.append('limit', '10');

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setMemoryData(await res.json());
      setError('');
    } catch (e) {
      setError(`Memory query failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Render the Insights section
  const renderInsightsSection = (insights) => {
    if (!insights || typeof insights !== 'object') {
      return <p className="italic text-gray-500">No insights available.</p>;
    }
    return (
      <div className="space-y-6">
        {Object.entries(insightsConfig).map(([key, cfg]) => {
          const content = insights[key];
          if (!content) return null;
          return (
            <div key={key} className={`${cfg.bg} p-6 rounded-lg`}>
              <h5 className={`flex items-center gap-2 font-semibold ${cfg.text}`}>
                <span>{cfg.icon}</span> {cfg.label}
              </h5>
              <div className="mt-2 text-gray-700">
                {Array.isArray(content) ? (
                  <ul className="list-disc pl-5 space-y-2">
                    {content.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                ) : typeof content === 'object' ? (
                  <ul className="list-disc pl-5 space-y-2">
                    {Object.entries(content).map(([subKey, subVal]) => (
                      <li key={subKey}>
                        <strong>{subKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {subVal}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>{content}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Render the Coaching section
  const renderCoachingSection = (coaching) => {
    if (!coaching || typeof coaching !== 'object') {
      return <p className="italic text-gray-500">Your personal coach will provide feedback here.</p>;
    }
    return (
      <div className="space-y-6">
        {Object.entries(coachingConfig).map(([key, cfg]) => {
          const content = coaching[key];
          if (!content) return null;
          return (
            <div key={key} className={`${cfg.bg} p-6 rounded-lg`}>
              <h5 className={`flex items-center gap-2 font-semibold ${cfg.text}`}>
                <span>{cfg.icon}</span> {cfg.label}
              </h5>
              <div className="mt-2 text-gray-700">
                {Array.isArray(content) ? (
                  <ul className="list-disc pl-5 space-y-2">
                    {content.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                ) : (
                  <p>{content}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Renders the voice insights (voice tab)
  const renderVoiceInsightsSection = (insights) => {
    if (!insights || typeof insights !== 'object') {
      return <p className="italic text-gray-500">No voice insights available.</p>;
    }
    return (
      <div className="space-y-6">
        {Object.entries(voiceInsightsConfig).map(([key, cfg]) => {
          const content = insights[key];
          if (!content) return null;
          return (
            <div key={key} className={`${cfg.bg} p-6 rounded-lg`}>
              <h5 className={`flex items-center gap-2 font-semibold ${cfg.text}`}>
                <span>{cfg.icon}</span> {cfg.label}
              </h5>
              <div className="mt-2 text-gray-700">
                {Array.isArray(content) ? (
                  <ul className="list-disc pl-5 space-y-2">
                    {content.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                ) : (
                  <p>{content}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Handlers
  const handleInputChange      = useCallback(e => setUserInput(e.target.value), []);
  const handleKeyPress         = useCallback(e => e.key === 'Enter' && analyzeProductivity(), []);
  const handleMemoryKeyPress   = useCallback(e => e.key === 'Enter' && queryMemory(e.target.value), []);
  const handleUserIdChange     = useCallback(e => setUserId(e.target.value), []);

  // UI components
  const TabButton = ({ id, icon, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center gap-3 px-6 py-3 rounded-lg transition-all duration-200 ${
        isActive
          ? 'bg-blue-600 text-white shadow-lg transform scale-105'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      <span className="text-xl">{icon}</span>
      <span className="font-medium">{label}</span>
    </button>
  );

  const DataCard = ({ title, children, icon, color = "blue" }) => (
    <div className={`bg-white rounded-xl shadow-lg border-l-4 border-${color}-500 p-6 mb-6`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 bg-${color}-100 rounded-lg`}>
          <span className={`text-2xl text-${color}-600`}>{icon}</span>
        </div>
        <h3 className="text-xl font-bold text-gray-800">{title}</h3>
      </div>
      {children}
    </div>
  );

  // Tab contents
  const renderAnalysisTab = () => (
    <div className="space-y-6">
      <DataCard title="Productivity Analysis" icon="📊" color="blue">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ask TimeCop about your productivity:
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={userInput}
                onChange={handleInputChange}
                placeholder="How was my week? What should I improve?"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                onKeyPress={handleKeyPress}
                autoComplete="off"
                spellCheck="false"
              />
              <button
                onClick={analyzeProductivity}
                disabled={isLoading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                <span>📤</span> {isLoading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </div>

          {analysisResult && (
            <>
              {analysisResult.parsedInsights && (
                <div className="bg-white p-6 rounded-lg mb-6">
                  <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span>💡</span> Insights
                  </h4>
                  {renderInsightsSection(analysisResult.parsedInsights)}
                </div>
              )}

              <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg">
                <h4 className="font-semibold text-purple-800 mb-4 flex items-center gap-2">
                  <span>💬</span> TimeCop Coaching
                </h4>
                <div className="text-gray-800">
                  {renderCoachingSection(analysisResult.parsedCoaching)}
                </div>
              </div>
            </>
          )}
        </div>
      </DataCard>
    </div>
  );

  const renderVoiceTab = () => (
    <div className="space-y-6">
      <DataCard title="Voice Logging" icon="🎤" color="green">
        <div className="space-y-4">
          <div className="text-center">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`px-8 py-4 rounded-full text-white font-semibold flex items-center gap-3 mx-auto transition-all duration-200 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : 'bg-green-500 hover:bg-green-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isRecording ? (
                <>
                  <span>⏹️</span> Stop Recording
                </>
              ) : (
                <>
                  <span>▶️</span> Start Voice Log
                </>
              )}
            </button>
            {isRecording && (
              <p className="text-sm text-gray-600 mt-3 animate-bounce">
                🎤 Recording... Speak about your current activity or how you're feeling
              </p>
            )}
          </div>

          {voiceResult && (
            <>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-800 mb-3">Voice Log Result</h4>
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-gray-700">Transcription:</span>
                    <p className="text-gray-600 mt-1">{voiceResult.transcription}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Activity:</span>
                    <p className="text-gray-600 mt-1">{voiceResult.tags.activity_type}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Mood:</span>
                    <p className="text-gray-600 mt-1">{voiceResult.tags.mood}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Duration:</span>
                    <p className="text-gray-600 mt-1">{voiceResult.tags.duration}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Energy Level:</span>
                    <p className="text-gray-600 mt-1">{voiceResult.tags.energy_level}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Confidence:</span>
                    <p className="text-gray-600 mt-1">
                      {(voiceResult.tags.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  {voiceResult.stored_in_memory && (
                    <div className="text-green-600 text-sm flex items-center gap-2">
                      <span>🧠</span> Stored in long-term memory
                    </div>
                  )}
                </div>
              </div>

              {voiceResult.insight_summary && (
                <div className="bg-white p-6 rounded-lg mt-4">
                  <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span>💡</span> Voice Insights
                  </h4>
                  <p className="text-gray-700">
                    {voiceResult.insight_summary}
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </DataCard>
    </div>
  );

  const renderMemoryTab = () => (
    <div className="space-y-6">
      <DataCard title="Memory & Trends" icon="🧠" color="purple">
        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Search your productivity history..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              onKeyPress={handleMemoryKeyPress}
              autoComplete="off"
              spellCheck="false"
            />
            <button
              onClick={() => queryMemory()}
              disabled={isLoading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              <span>🔍</span> Query Memory
            </button>
          </div>

          {memoryData && (
            <div className="space-y-4">
              {memoryData.trends && (
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-purple-800 mb-2 flex items-center gap-2">
                    <span>📈</span> Productivity Trends
                  </h4>
                  <div className="text-sm text-purple-700">
                    {typeof memoryData.trends === 'string' ? (
                      <p>{memoryData.trends}</p>
                    ) : (
                      <ul className="list-disc pl-5 text-sm space-y-1">
                        {Object.entries(memoryData.trends || {}).map(([key, val]) => (
                          <li key={key}>
                            <strong className="capitalize">{key.replace(/_/g, ' ')}:</strong> {val}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-800 mb-3">Recent Memory Entries</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  <div className="space-y-4 max-h-[400px] overflow-y-auto">
                    {memoryData.items && memoryData.items.length > 0 ? (
                      memoryData.items.map((item, index) => (
                        console.log(memoryData.items),
                        <div key={index} className="bg-white p-4 rounded-lg shadow border">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-semibold text-purple-700">
                              🕒 {new Date(item.timestamp).toLocaleString()} — {item.type}
                            </span>
                          </div>
                          <p className="text-gray-800 mb-2">
                            <strong>🧠 Summary:</strong> {item.llm_summary}
                          </p>
                          <details className="text-sm text-gray-600">
                            <summary className="cursor-pointer text-blue-600">Show Raw Log</summary>
                            <pre className="mt-2 whitespace-pre-wrap">{item.raw_input}</pre>
                          </details>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 italic">No memory entries found</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </DataCard>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
                <span className="text-white text-3xl">⏰</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  TimeCop
                </h1>
                <p className="text-gray-600">Multi-Agent Productivity System</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-gray-600">👤</span>
                <input
                  type="text"
                  value={userId}
                  onChange={handleUserIdChange}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                  placeholder="User ID"
                  autoComplete="off"
                  spellCheck="false"
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex gap-4 overflow-x-auto">
            <TabButton
              id="analyze"
              icon="📊"
              label="Analyze"
              isActive={activeTab === 'analyze'}
              onClick={setActiveTab}
            />
            <TabButton
              id="voice"
              icon="🎤"
              label="Voice Log"
              isActive={activeTab === 'voice'}
              onClick={setActiveTab}
            />
            <TabButton
              id="memory"
              icon="🧠"
              label="Memory"
              isActive={activeTab === 'memory'}
              onClick={setActiveTab}
            />
            <TabButton
             id="dashboard"
             icon="📊"
             label="Dashboard"
             isActive={activeTab === 'dashboard'}
             onClick={setActiveTab}
            />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">Error:</p>
            <p>{error}</p>
          </div>
        )}
        {isLoading && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6 flex items-center gap-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
            <span>Processing your request...</span>
          </div>
        )}
        {activeTab === 'analyze' && renderAnalysisTab()}
        {activeTab === 'voice'   && renderVoiceTab()}
        {activeTab === 'memory'  && renderMemoryTab()}
        {activeTab === 'dashboard' && <Dashboard userId={userId} />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <span>🤖</span>
                Active Agents
              </h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>• UserProxy Agent</p>
                <p>• Voice Log Agent</p>
                <p>• Data Fetcher Agent</p>
                <p>• Time Analyzer Agent</p>
              </div>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <span>🔗</span>
                Data Sources
              </h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>• GitHub Activity</p>
                <p>• Google Calendar</p>
                <p>• Gmail Logs</p>
                <p>• Voice Input</p>
              </div>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <span>🎯</span>
                Insights & Coach
              </h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>• Pattern Recognition</p>
                <p>• Personalized Coaching</p>
                <p>• Long-term Memory</p>
                <p>• Trend Analysis</p>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default TimeCopApp;