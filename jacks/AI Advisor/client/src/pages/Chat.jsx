import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line, CartesianGrid } from 'recharts';
import { Send, Sparkles, Database, FileText, BarChart3, HelpCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Chat = ({ activeDataset }) => {
  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [openInspectors, setOpenInspectors] = useState({});

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (activeDataset) {
      fetchChatHistory();
    }
  }, [activeDataset]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChatHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/datasets/${activeDataset._id}/chat`);
      if (res.data && res.data.messages) {
        // Expand the saved database messages to include a mock spec/result if needed
        setMessages(res.data.messages.map(m => ({
          role: m.role,
          content: m.content,
          id: m._id
        })));
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to fetch chat history:', err);
    }
  };

  const handleSend = async (textToSend) => {
    const text = textToSend || inputMsg;
    if (!text.trim()) return;

    if (!textToSend) setInputMsg('');

    // Add user message locally
    const userMsgId = Math.random().toString(36).substring(2, 9);
    const newMessages = [...messages, { id: userMsgId, role: 'user', content: text }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/datasets/${activeDataset._id}/chat`, { message: text });
      
      // Add assistant message with query results
      const assistantMsgId = Math.random().toString(36).substring(2, 9);
      setMessages(prev => [
        ...prev,
        {
          id: assistantMsgId,
          role: 'assistant',
          content: res.data.answer,
          querySpec: res.data.querySpec,
          queryResults: res.data.queryResults
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsgId = Math.random().toString(36).substring(2, 9);
      setMessages(prev => [
        ...prev,
        {
          id: errorMsgId,
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your query. Please make sure the column names match and try again.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleInspector = (msgId) => {
    setOpenInspectors(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  // Helper to render inline Recharts based on query spec and outputs
  const renderInlineVisual = (querySpec, queryResults) => {
    if (!querySpec || !queryResults || !Array.isArray(queryResults) || queryResults.length === 0) return null;

    const action = querySpec.action;
    const targetCol = querySpec.target_col;
    
    // Group By chart: Bar Chart
    if (action === 'groupby' && querySpec.groupby_col) {
      const gbCol = querySpec.groupby_col;
      const chartData = queryResults.slice(0, 6).map(row => ({
        name: row[gbCol] || 'Unknown',
        value: Number(row[targetCol]) || 0
      }));

      return (
        <div className="mt-4 p-3 bg-slate-900/50 border border-slate-800 rounded-xl max-w-full">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Inline Analysis Graph: Bar Chart</p>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ left: -20, bottom: -10 }}>
                <XAxis dataKey="name" stroke="#64748B" fontSize={8} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={8} tickLine={false} />
                <Tooltip formatter={(val) => [Number(val).toLocaleString(), targetCol]} />
                <Bar dataKey="value" fill="#6366F1" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    // Trend chart: Line Chart
    if (action === 'trend' && querySpec.date_col) {
      const dateCol = querySpec.date_col;
      const chartData = queryResults.map(row => ({
        name: row[dateCol] || 'N/A',
        value: Number(row[targetCol]) || 0
      }));

      return (
        <div className="mt-4 p-3 bg-slate-900/50 border border-slate-800 rounded-xl max-w-full">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Inline Analysis Graph: Trend Line</p>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ left: -20, bottom: -10 }}>
                <XAxis dataKey="name" stroke="#64748B" fontSize={8} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={8} tickLine={false} />
                <Tooltip formatter={(val) => [Number(val).toLocaleString(), targetCol]} />
                <Line type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    // Standard raw output table
    return (
      <div className="mt-4 p-3 bg-slate-900/50 border border-slate-800 rounded-xl max-w-full overflow-x-auto">
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Raw Aggregates Data Table</p>
        <table className="w-full text-left border-collapse text-[10px]">
          <thead>
            <tr className="border-b border-slate-800">
              {Object.keys(queryResults[0]).map(key => (
                <th key={key} className="pb-1 font-bold text-slate-400 uppercase">{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {queryResults.slice(0, 5).map((row, i) => (
              <tr key={i} className="border-b border-slate-900">
                {Object.values(row).map((val, idx) => (
                  <td key={idx} className="py-1.5 text-slate-300">
                    {typeof val === 'number' ? val.toLocaleString() : String(val)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Suggestion queries to help the user start
  const suggestions = [
    { label: 'Highest Selling Category', query: 'Which category generated the highest sales?' },
    { label: 'Time-Series Trend', query: 'Show monthly sales trend over time.' },
    { label: 'Correlation Study', query: 'What is the correlation between variables?' },
    { label: 'General Stats Profile', query: 'Give me a statistical summary of the target column.' }
  ];

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-120px)]">
      {/* Header */}
      <div className="shrink-0">
        <h1 className="text-2xl font-bold tracking-tight dark:text-white text-slate-800 flex items-center gap-2">
          AI Analytics Advisor
          <Sparkles className="w-5 h-5 text-indigo-400" />
        </h1>
        <p className="text-sm dark:text-slate-400 text-slate-500">
          Query your datasets in conversational English. The AI agent executes structured code to reply.
        </p>
      </div>

      {!activeDataset ? (
        <div className="glass-card p-12 text-center flex-1 flex flex-col items-center justify-center min-h-[300px]">
          <Database className="w-14 h-14 text-slate-500 mb-4 animate-pulse" />
          <h3 className="text-lg font-bold dark:text-slate-200 text-slate-700">Chat Offline</h3>
          <p className="text-sm dark:text-slate-400 text-slate-500 max-w-sm mt-1">
            Upload a dataset or select an active dataset in the Dataset Workspace tab to load AI advisory chat functions.
          </p>
        </div>
      ) : (
        <div className="flex-1 flex gap-6 min-h-0">
          {/* Chat Window */}
          <div className="flex-1 glass-card p-6 flex flex-col min-h-0 bg-slate-850/60">
            {/* Messages box */}
            <div className="flex-1 overflow-y-auto pr-1 space-y-4 mb-4 min-h-0">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto p-4 space-y-4">
                  <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-full flex items-center justify-center animate-bounce">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold dark:text-slate-200 text-slate-700">Ask Anything About {activeDataset.name}</h4>
                    <p className="text-xs dark:text-slate-400 text-slate-500 mt-1">
                      You can ask questions such as: "What is our highest performing region?", "Plot monthly sales", or "Are sales correlated with profit?"
                    </p>
                  </div>
                  {/* Suggestion Chips */}
                  <div className="flex flex-wrap gap-2 justify-center pt-2">
                    {suggestions.map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(s.query)}
                        className="text-[10px] bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 border dark:border-slate-800 border-slate-200 rounded-full px-3 py-1.5 font-semibold text-slate-600 dark:text-slate-300 transition-colors"
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-4 text-xs ${
                      m.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : 'dark:bg-slate-900 bg-slate-50 border dark:border-slate-800 border-slate-200 dark:text-slate-200 text-slate-800 rounded-bl-none'
                    }`}
                  >
                    {/* Message Text (Simple newlines, markdown titles parsed simply) */}
                    <div className="space-y-1.5 leading-relaxed whitespace-pre-wrap">
                      {m.content}
                    </div>

                    {/* Inline code and chart if assistant ran queries */}
                    {m.role === 'assistant' && m.querySpec && (
                      <div className="mt-4 border-t dark:border-slate-800 border-slate-200 pt-3">
                        <button
                          onClick={() => toggleInspector(m.id)}
                          className="flex items-center gap-1 text-[9px] font-bold text-indigo-400 uppercase tracking-wider hover:text-indigo-300 transition-colors focus:outline-none"
                        >
                          {openInspectors[m.id] ? (
                            <>
                              <ChevronUp className="w-3.5 h-3.5" /> Close Query Inspector
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-3.5 h-3.5" /> Open Query Inspector
                            </>
                          )}
                        </button>

                        {/* Inspector JSON details */}
                        {openInspectors[m.id] && (
                          <div className="mt-2 p-2.5 bg-slate-950 text-[9px] font-mono text-emerald-400 rounded-lg overflow-x-auto border border-slate-900 max-h-40">
                            <span className="text-slate-500">// Generated query plan</span>
                            <pre className="mt-1">{JSON.stringify(m.querySpec, null, 2)}</pre>
                          </div>
                        )}

                        {/* Visual aggregates chart */}
                        {renderInlineVisual(m.querySpec, m.queryResults)}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="dark:bg-slate-900 bg-slate-50 border dark:border-slate-800 border-slate-200 rounded-2xl rounded-bl-none p-4 flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />
                    <span className="text-xs text-slate-400">Advisor is consulting dataset...</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="shrink-0 flex gap-2"
            >
              <input
                type="text"
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                placeholder={`Ask a question about "${activeDataset.name}"...`}
                className="flex-1 bg-slate-100 dark:bg-slate-900 border dark:border-slate-800 border-slate-200 text-slate-700 dark:text-slate-100 rounded-xl px-4 py-3 text-xs placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
              <button
                type="submit"
                disabled={loading || !inputMsg.trim()}
                className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl p-3 shrink-0 flex items-center justify-center disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-indigo-600/10"
              >
                <Send className="w-4.5 h-4.5" />
              </button>
            </form>
          </div>

          {/* Reference Column sidebar */}
          <div className="hidden lg:block w-64 shrink-0 glass-card p-6 overflow-y-auto">
            <h3 className="text-xs font-bold tracking-wider dark:text-slate-300 text-slate-700 uppercase mb-4 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-indigo-500" />
              Column Reference
            </h3>
            <div className="space-y-2">
              {activeDataset.columns.map((c, i) => (
                <div key={i} className="p-2.5 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <p className="text-[11px] font-semibold dark:text-slate-200 text-slate-700 truncate">{c.name}</p>
                  <div className="flex items-center justify-between mt-1 text-[9px] text-slate-500">
                    <span className="capitalize">{c.type}</span>
                    <span>{c.uniqueCount} uniques</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
