import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatService } from '../services/chatService';
import { complaintService } from '../services/complaintService';
import { 
  Bot, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  ArrowRight, 
  MapPin, 
  Clock, 
  Building, 
  ShieldCheck,
  Camera,
  X,
  Image as ImageIcon,
  Paperclip,
  Check
} from 'lucide-react';
import { AIConfidenceBadge } from '../components/AIConfidenceBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const ChatbotGrievancePage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState({});
  const [analysis, setAnalysis] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submittedResult, setSubmittedResult] = useState(null);

  // Photo upload states
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [previewPhotoModal, setPreviewPhotoModal] = useState(null);
  const fileInputRef = useRef(null);

  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, uploadingPhoto]);

  const startNewChat = async () => {
    setLoading(true);
    setAnalysis(null);
    setSubmittedResult(null);
    try {
      const res = await chatService.startSession();
      if (res.success) {
        setSessionId(res.session_id);
        setMessages(res.session.messages || []);
        setSessionData(res.session.data || {});
      }
    } catch (err) {
      console.error('Failed to start chat session:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    startNewChat();
  }, []);

  const handleSendMessage = async (textToSend, explicitImageUrl = null) => {
    const text = (textToSend || input).trim();
    if ((!text && !explicitImageUrl) || !sessionId || loading) return;

    setInput('');
    // Optimistically add user message
    const userMsg = { 
      role: 'user', 
      content: text, 
      image_url: explicitImageUrl,
      timestamp: new Date().toISOString() 
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await chatService.sendMessage(sessionId, text, explicitImageUrl);
      if (res.success) {
        setMessages(res.session.messages);
        setSessionData(res.session.data);

        // Check if state is ANALYZING, trigger AI analysis automatically
        if (res.state === 'ANALYZING') {
          await triggerAnalysis(sessionId);
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          content: 'I encountered an issue processing that. Please try again.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !sessionId) return;

    // Reset input so same file can be re-selected if needed
    e.target.value = '';

    setUploadingPhoto(true);
    try {
      const uploadRes = await complaintService.uploadAttachment(file);
      if (uploadRes.success && uploadRes.file_url) {
        // Send message with image attached
        await handleSendMessage(`Attached grievance photo evidence: ${file.name}`, uploadRes.file_url);
      } else {
        alert('Could not upload photo. Please ensure it is a valid JPG/PNG under 10MB.');
      }
    } catch (err) {
      console.error('Photo upload failed:', err);
      alert('Photo upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploadingPhoto(false);
    }
  };

  const triggerAnalysis = async (sid) => {
    setLoading(true);
    try {
      const res = await chatService.analyzeSession(sid);
      if (res.success) {
        setMessages(res.session.messages);
        setAnalysis(res.analysis);
      }
    } catch (err) {
      console.error('Error in AI analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitGrievance = async () => {
    if (!sessionId || submitting) return;
    setSubmitting(true);
    try {
      const res = await chatService.submitSession(sessionId);
      if (res.success) {
        setSubmittedResult(res);
      }
    } catch (err) {
      console.error('Submission failed:', err);
      alert('Grievance submission failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  // Determine if the current bot question is about photo (Step 4)
  const isPhotoStep = messages.length > 0 && 
    messages[messages.length - 1].role === 'bot' && 
    (messages[messages.length - 1].content?.includes('Step 4') || 
     messages[messages.length - 1].content?.includes('picture of the issue'));

  return (
    <div className="main-content animate-fade-in" style={{ maxWidth: 1200 }}>
      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        accept="image/png, image/jpeg, image/jpg, image/webp" 
        style={{ display: 'none' }} 
        onChange={handlePhotoSelect} 
      />

      {/* Top Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.75rem',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 10 }}>
              <Bot size={26} color="var(--primary-600)" />
              Interactive Grievance Registration
            </h1>
            <span style={{
              background: 'var(--primary-50)',
              color: 'var(--primary-600)',
              border: '1px solid var(--primary-100)',
              borderRadius: 20,
              padding: '0.15rem 0.55rem',
              fontSize: '0.7rem',
              fontWeight: 700,
              textTransform: 'uppercase'
            }}>
              Citizen AI Intake
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', maxWidth: 740 }}>
            Submit civic complaints in conversational language with photo attachments. Our system extracts location, duration, and keywords, assigning appropriate municipal department jurisdiction.
          </p>
        </div>

        <button onClick={startNewChat} className="btn btn-secondary btn-sm" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <RefreshCw size={14} />
          Reset Chat Session
        </button>
      </div>

      {submittedResult ? (
        /* Success Screen */
        <div className="glass-card" style={{ maxWidth: 640, margin: '2rem auto', textAlign: 'center', padding: '3rem 2.5rem' }}>
          <div style={{
            width: 60,
            height: 60,
            borderRadius: '50%',
            background: '#ecfdf5',
            color: '#16a34a',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1.25rem',
            border: '2px solid #bbf7d0',
          }}>
            <CheckCircle2 size={32} />
          </div>

          <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Grievance Registered Successfully</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
            Your grievance has been logged into the municipal redressal pipeline with verified AI classification.
          </p>

          <div style={{
            background: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 12,
            padding: '1.25rem',
            marginBottom: '1.75rem',
            display: 'inline-block',
            minWidth: 300,
          }}>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.05em', marginBottom: 4 }}>
              OFFICIAL GRIEVANCE TRACKING NUMBER
            </div>
            <div style={{
              fontSize: '1.75rem',
              fontWeight: 800,
              fontFamily: 'var(--font-mono)',
              color: 'var(--primary-600)',
              letterSpacing: '0.05em',
            }}>
              {submittedResult.ticket_number}
            </div>
          </div>

          {sessionData?.image_url && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              fontSize: '0.82rem',
              color: '#10b981',
              marginBottom: '1.5rem',
            }}>
              <Check size={16} />
              <span>Incident photo evidence securely attached and dispatched to field crew</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate(`/track?ticket=${submittedResult.ticket_number}`)}
              className="btn btn-primary"
            >
              Track Live Status
              <ArrowRight size={16} />
            </button>
            <button
              onClick={() => navigate('/citizen')}
              className="btn btn-secondary"
            >
              Go to Dashboard
            </button>
            <button
              onClick={startNewChat}
              className="btn btn-secondary"
            >
              Lodge Another
            </button>
          </div>
        </div>
      ) : (
        /* Split view: Chat on Left, AI Diagnostics Preview on Right */
        <div style={{
          display: 'grid',
          gridTemplateColumns: analysis ? '1fr 420px' : '1fr',
          gap: '1.75rem',
          alignItems: 'start',
        }}>
          {/* Chat Window */}
          <div className="chat-window">
            <div className="chat-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 34,
                  height: 34,
                  borderRadius: 10,
                  background: 'var(--primary-50)',
                  border: '1px solid var(--primary-200)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--primary-600)',
                }}>
                  <Bot size={20} />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-primary)' }}>LokSeva Citizen AI Intake</div>
                  <div style={{ fontSize: '0.72rem', color: '#16a34a', display: 'flex', alignItems: 'center', gap: 5, fontWeight: 600 }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#16a34a', display: 'inline-block' }} />
                    Active Assisted Filing Session
                  </div>
                </div>
              </div>
              <Sparkles size={18} color="var(--primary-600)" />
            </div>

            <div className="chat-messages">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`chat-bubble ${m.role === 'bot' ? 'chat-bubble-bot' : 'chat-bubble-user'} animate-fade-in`}
                >
                  <p style={{ whiteSpace: 'pre-line' }}>{m.content}</p>

                  {/* Message Photo Preview */}
                  {m.image_url && (
                    <div style={{ marginTop: 10 }}>
                      <img 
                        src={m.image_url} 
                        alt="Attached grievance evidence" 
                        onClick={() => setPreviewPhotoModal(m.image_url)}
                        style={{ 
                          maxWidth: 240, 
                          maxHeight: 180, 
                          borderRadius: 10, 
                          objectFit: 'cover', 
                          cursor: 'pointer',
                          border: '1px solid var(--border-subtle)',
                          display: 'block',
                          boxShadow: 'var(--shadow-md)',
                        }} 
                      />
                      <span style={{ fontSize: '0.72rem', color: m.role === 'bot' ? 'var(--text-muted)' : 'rgba(255,255,255,0.85)', marginTop: 4, display: 'inline-block' }}>
                        Click photo to enlarge
                      </span>
                    </div>
                  )}

                  {/* Quick replies buttons */}
                  {m.quick_replies && (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.85rem' }}>
                      {m.quick_replies.map((reply, rIdx) => {
                        const isPhotoAction = reply.includes('Upload Photo') || reply.includes('Attach Photo');
                        return (
                          <button
                            key={rIdx}
                            onClick={() => {
                              if (isPhotoAction) {
                                fileInputRef.current?.click();
                              } else {
                                handleSendMessage(reply);
                              }
                            }}
                            style={{
                              background: '#ffffff',
                              border: isPhotoAction ? '1px solid var(--primary-500)' : '1px solid #cbd5e1',
                              color: isPhotoAction ? 'var(--primary-600)' : '#334155',
                              padding: '0.4rem 0.85rem',
                              borderRadius: 20,
                              fontSize: '0.82rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 6,
                              boxShadow: 'var(--shadow-sm)',
                              transition: 'all var(--transition-fast)',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = 'var(--primary-50)';
                              e.currentTarget.style.borderColor = 'var(--primary-500)';
                              e.currentTarget.style.color = 'var(--primary-600)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = '#ffffff';
                              e.currentTarget.style.borderColor = isPhotoAction ? 'var(--primary-500)' : '#cbd5e1';
                              e.currentTarget.style.color = isPhotoAction ? 'var(--primary-600)' : '#334155';
                            }}
                          >
                            {isPhotoAction && <Camera size={14} />}
                            {reply}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}

              {/* Dedicated Interactive Photo Upload Card during Photo Step */}
              {isPhotoStep && !sessionData?.image_url && (
                <div className="animate-fade-in" style={{
                  margin: '0.75rem 0',
                  padding: '1.25rem',
                  background: 'var(--bg-surface-secondary)',
                  border: '1px dashed #cbd5e1',
                  borderRadius: 14,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '0.75rem',
                  textAlign: 'center',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--primary-600)', fontWeight: 700, fontSize: '0.92rem' }}>
                    <Camera size={18} />
                    Attach Incident Photo Evidence
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', maxWidth: 420 }}>
                    Upload a real photo (e.g. leaking pipeline, pothole, or garbage pile). Attached photos are directly dispatched to field officers.
                  </p>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploadingPhoto || loading}
                      className="btn btn-primary btn-sm"
                      style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                    >
                      <Camera size={15} />
                      {uploadingPhoto ? 'Uploading Photo...' : 'Upload Incident Photo'}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSendMessage("Skip photo")}
                      disabled={uploadingPhoto || loading}
                      className="btn btn-secondary btn-sm"
                    >
                      Skip Photo Step
                    </button>
                  </div>
                </div>
              )}

              {uploadingPhoto && (
                <div className="chat-bubble chat-bubble-user" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Camera size={16} className="animate-pulse" />
                  <span style={{ fontSize: '0.85rem' }}>Uploading incident photo...</span>
                </div>
              )}

              {loading && (
                <div className="chat-bubble chat-bubble-bot" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sparkles size={16} color="var(--primary-600)" className="animate-spin" />
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>AI analyzing grievance context...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Bar with Photo Attachment Button */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="chat-input-bar"
            >
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading || uploadingPhoto || !!submittedResult}
                className="btn btn-secondary"
                style={{
                  padding: '0 0.85rem',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                title="Attach photo evidence"
              >
                <Camera size={18} color="var(--primary-600)" />
              </button>

              <input
                type="text"
                placeholder="Type your response or grievance detail here..."
                className="form-input"
                style={{ flex: 1, borderRadius: 10 }}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading || !!submittedResult}
              />

              <button
                type="submit"
                disabled={loading || !input.trim() || !!submittedResult}
                className="btn btn-primary"
                style={{ padding: '0 1.25rem', borderRadius: 10 }}
              >
                <Send size={16} />
              </button>
            </form>
          </div>

          {/* AI Analysis Preview Panel */}
          {analysis && (
            <div className="glass-card animate-fade-in" style={{ border: '1px solid var(--border-subtle)' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid var(--border-subtle)',
                paddingBottom: '1rem',
                marginBottom: '1.25rem',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sparkles size={18} color="var(--primary-600)" />
                  <h3 style={{ fontSize: '1.05rem', color: 'var(--text-primary)', fontWeight: 700 }}>AI Grievance Insights</h3>
                </div>
                <AIConfidenceBadge confidence={analysis.overall_confidence || analysis.classification?.confidence} />
              </div>

              {/* Duplicate Warning */}
              {analysis.duplicate?.is_duplicate && (
                <div style={{
                  background: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: 10,
                  padding: '0.85rem',
                  marginBottom: '1.25rem',
                  display: 'flex',
                  gap: 10,
                }}>
                  <AlertTriangle size={20} color="#dc2626" style={{ flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#991b1b' }}>
                      Potential Duplicate Detected
                    </div>
                    <p style={{ fontSize: '0.78rem', color: '#7f1d1d', marginTop: 2 }}>
                      A similar grievance has already been filed in your locality. Your report will be linked to speed up resolution.
                    </p>
                  </div>
                </div>
              )}

              {/* Extracted Details */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-subtle)', padding: '0.75rem 0.9rem', borderRadius: 10 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 2 }}>PREDICTED CATEGORY</div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
                    {analysis.classification?.category}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-subtle)', padding: '0.75rem 0.9rem', borderRadius: 10 }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 4 }}>PRIORITY LEVEL</div>
                    <PriorityBadge priority={analysis.priority?.priority} />
                  </div>

                  <div style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-subtle)', padding: '0.75rem 0.9rem', borderRadius: 10 }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 2 }}>DURATION</div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Clock size={12} />
                      {sessionData?.duration || 'Recent'}
                    </div>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-subtle)', padding: '0.75rem 0.9rem', borderRadius: 10 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 2 }}>ROUTED DEPARTMENT</div>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Building size={14} />
                    {analysis.recommended_department_name || 'Designated Municipal Ward'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-surface-secondary)', border: '1px solid var(--border-subtle)', padding: '0.75rem 0.9rem', borderRadius: 10 }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 2 }}>LOCATION</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <MapPin size={14} />
                    {sessionData?.location || 'Citizen Location'}
                  </div>
                </div>

                {/* Evidence Photo Preview in Panel */}
                {sessionData?.image_url && (
                  <div style={{ background: '#f0fdf4', padding: '0.75rem 0.9rem', borderRadius: 10, border: '1px solid #bbf7d0' }}>
                    <div style={{ fontSize: '0.72rem', color: '#15803d', fontWeight: 700, marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Camera size={13} />
                      INCIDENT PHOTO EVIDENCE ATTACHED
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <img 
                        src={sessionData.image_url} 
                        alt="Evidence thumbnail" 
                        onClick={() => setPreviewPhotoModal(sessionData.image_url)}
                        style={{
                          width: 54,
                          height: 54,
                          borderRadius: 8,
                          objectFit: 'cover',
                          cursor: 'pointer',
                          border: '1px solid #bbf7d0',
                        }}
                      />
                      <div>
                        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#15803d' }}>Photo Verified</div>
                        <button
                          type="button"
                          onClick={() => setPreviewPhotoModal(sessionData.image_url)}
                          style={{ background: 'none', border: 'none', color: '#16a34a', fontSize: '0.75rem', padding: 0, cursor: 'pointer', textDecoration: 'underline' }}
                        >
                          Click to enlarge
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Submit CTA */}
              <button
                onClick={handleSubmitGrievance}
                disabled={submitting}
                className="btn btn-primary"
                style={{ width: '100%', padding: '0.85rem' }}
              >
                <ShieldCheck size={18} />
                {submitting ? 'Registering Grievance...' : 'Submit Grievance Now'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Lightbox Modal for Chat Photo Preview */}
      {previewPhotoModal && (
        <div 
          onClick={() => setPreviewPhotoModal(null)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.85)',
            backdropFilter: 'blur(10px)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
          }}
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}
          >
            <img 
              src={previewPhotoModal} 
              alt="Grievance evidence full view" 
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                borderRadius: 14,
                boxShadow: '0 20px 50px rgba(0,0,0,0.8)',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
            />
            <button
              onClick={() => setPreviewPhotoModal(null)}
              style={{
                position: 'absolute',
                top: -16,
                right: -16,
                background: '#1e293b',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '50%',
                width: 36,
                height: 36,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatbotGrievancePage;
