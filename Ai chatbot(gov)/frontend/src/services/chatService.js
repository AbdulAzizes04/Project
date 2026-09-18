import api from './api';

export const chatService = {
  startSession: async () => {
    const res = await api.post('/chat/start');
    return res.data;
  },

  sendMessage: async (sessionId, message, imageUrl = null) => {
    const res = await api.post('/chat/message', {
      session_id: sessionId,
      message,
      image_url: imageUrl,
    });
    return res.data;
  },

  analyzeSession: async (sessionId) => {
    const res = await api.post('/chat/analyze', {
      session_id: sessionId,
    });
    return res.data;
  },

  submitSession: async (sessionId) => {
    const res = await api.post('/chat/submit', {
      session_id: sessionId,
    });
    return res.data;
  },
};
