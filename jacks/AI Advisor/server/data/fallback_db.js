const fs = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'db.json');

// Initialize empty DB if it doesn't exist
if (!fs.existsSync(DB_FILE)) {
  fs.writeFileSync(DB_FILE, JSON.stringify({
    users: [],
    datasets: [],
    models: [],
    chats: []
  }, null, 2));
}

function readData() {
  try {
    const data = fs.readFileSync(DB_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    return { users: [], datasets: [], models: [], chats: [] };
  }
}

function writeData(data) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Failed to write to fallback DB:', err);
  }
}

const fallbackDb = {
  // Users
  users: {
    find: async (query) => {
      const db = readData();
      return db.users.filter(u => {
        for (let key in query) {
          if (u[key] !== query[key]) return false;
        }
        return true;
      });
    },
    findOne: async (query) => {
      const db = readData();
      return db.users.find(u => {
        for (let key in query) {
          if (u[key] !== query[key]) return false;
        }
        return true;
      });
    },
    findById: async (id) => {
      const db = readData();
      return db.users.find(u => u._id === id.toString());
    },
    create: async (userData) => {
      const db = readData();
      const newUser = {
        _id: Math.random().toString(36).substring(2, 9),
        ...userData,
        createdAt: new Date().toISOString()
      };
      db.users.push(newUser);
      writeData(db);
      return newUser;
    }
  },

  // Datasets
  datasets: {
    find: async (query) => {
      const db = readData();
      return db.datasets.filter(d => {
        for (let key in query) {
          if (query[key] && query[key].toString) {
            if (d[key] !== query[key].toString()) return false;
          } else if (d[key] !== query[key]) {
            return false;
          }
        }
        return true;
      });
    },
    findById: async (id) => {
      const db = readData();
      return db.datasets.find(d => d._id === id.toString());
    },
    findByIdAndUpdate: async (id, update) => {
      const db = readData();
      const idx = db.datasets.findIndex(d => d._id === id.toString());
      if (idx !== -1) {
        db.datasets[idx] = { ...db.datasets[idx], ...update };
        writeData(db);
        return db.datasets[idx];
      }
      return null;
    },
    findByIdAndDelete: async (id) => {
      const db = readData();
      const idx = db.datasets.findIndex(d => d._id === id.toString());
      if (idx !== -1) {
        const deleted = db.datasets.splice(idx, 1)[0];
        writeData(db);
        return deleted;
      }
      return null;
    },
    create: async (datasetData) => {
      const db = readData();
      const newDataset = {
        _id: Math.random().toString(36).substring(2, 9),
        ...datasetData,
        status: datasetData.status || 'processing',
        columns: datasetData.columns || [],
        summary: datasetData.summary || {},
        createdAt: new Date().toISOString()
      };
      db.datasets.push(newDataset);
      writeData(db);
      return newDataset;
    }
  },

  // ML Models
  models: {
    find: async (query) => {
      const db = readData();
      return db.models.filter(m => {
        for (let key in query) {
          if (query[key] && query[key].toString) {
            if (m[key] !== query[key].toString()) return false;
          } else if (m[key] !== query[key]) {
            return false;
          }
        }
        return true;
      });
    },
    findById: async (id) => {
      const db = readData();
      return db.models.find(m => m._id === id.toString());
    },
    create: async (modelData) => {
      const db = readData();
      const newModel = {
        _id: Math.random().toString(36).substring(2, 9),
        ...modelData,
        createdAt: new Date().toISOString()
      };
      db.models.push(newModel);
      writeData(db);
      return newModel;
    }
  },

  // Chat Histories
  chats: {
    findOne: async (query) => {
      const db = readData();
      return db.chats.find(c => {
        for (let key in query) {
          if (query[key] && query[key].toString) {
            if (c[key] !== query[key].toString()) return false;
          } else if (c[key] !== query[key]) {
            return false;
          }
        }
        return true;
      });
    },
    create: async (chatData) => {
      const db = readData();
      const newChat = {
        _id: Math.random().toString(36).substring(2, 9),
        ...chatData,
        messages: chatData.messages || [],
        updatedAt: new Date().toISOString()
      };
      db.chats.push(newChat);
      writeData(db);
      return newChat;
    },
    findOneAndUpdate: async (query, update) => {
      const db = readData();
      const chat = db.chats.find(c => {
        for (let key in query) {
          if (query[key] && query[key].toString) {
            if (c[key] !== query[key].toString()) return false;
          } else if (c[key] !== query[key]) {
            return false;
          }
        }
        return true;
      });

      if (chat) {
        if (update.$push && update.$push.messages) {
          chat.messages.push(update.$push.messages);
        }
        chat.updatedAt = new Date().toISOString();
        writeData(db);
        return chat;
      } else {
        // Create new
        const newChat = {
          _id: Math.random().toString(36).substring(2, 9),
          datasetId: query.datasetId.toString(),
          userId: query.userId.toString(),
          messages: update.$push && update.$push.messages ? [update.$push.messages] : [],
          updatedAt: new Date().toISOString()
        };
        db.chats.push(newChat);
        writeData(db);
        return newChat;
      }
    }
  }
};

module.exports = fallbackDb;
