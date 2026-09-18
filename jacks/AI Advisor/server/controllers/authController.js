const User = require('../models/User');
const fallbackDb = require('../data/fallback_db');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const mongoose = require('mongoose');

// Helper to determine if we should use MongoDB
const isMongoConnected = () => {
  return mongoose.connection.readyState === 1;
};

// Helper to escape regex special characters
const escapeRegex = (str) => {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

exports.register = async (req, res) => {
  const username = (req.body.username || '').trim();
  const email = (req.body.email || '').trim().toLowerCase();
  const password = req.body.password;

  if (!username || !email || !password) {
    return res.status(400).json({ message: 'Please provide username, email, and password' });
  }

  try {
    // Check if user already exists (check both Mongo and fallback)
    let existingUser = null;
    if (isMongoConnected()) {
      existingUser = await User.findOne({
        $or: [
          { email: email },
          { username: { $regex: new RegExp(`^${escapeRegex(username)}$`, 'i') } }
        ]
      });
    }

    if (!existingUser) {
      const fbUsers = await fallbackDb.users.find({});
      existingUser = fbUsers.find(u => 
        (u.email && u.email.trim().toLowerCase() === email) ||
        (u.username && u.username.trim().toLowerCase() === username.toLowerCase())
      );
    }

    if (existingUser) {
      return res.status(400).json({ message: 'User already exists with this email or username' });
    }

    // Register User
    let user;
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    if (isMongoConnected()) {
      user = new User({ username, email, password });
      await user.save();
      // Also sync into fallback DB
      await fallbackDb.users.create({
        username,
        email,
        password: hashedPassword,
        role: 'user'
      });
    } else {
      user = await fallbackDb.users.create({
        username,
        email,
        password: hashedPassword,
        role: 'user'
      });
    }

    const userId = user._id ? user._id.toString() : user.id;

    // Create JWT token
    const payload = {
      user: {
        id: userId,
        role: user.role
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET || 'fallback_secret_key',
      { expiresIn: '24h' },
      (err, token) => {
        if (err) throw err;
        res.status(201).json({
          token,
          user: {
            id: userId,
            username: user.username,
            email: user.email,
            role: user.role
          }
        });
      }
    );
  } catch (err) {
    console.error('Registration error:', err.message);
    res.status(500).json({ message: 'Server error: ' + err.message });
  }
};

exports.login = async (req, res) => {
  const rawInput = (req.body.email || req.body.username || '').toString().trim();
  const password = (req.body.password || '').toString();

  if (!rawInput || !password) {
    return res.status(400).json({ message: 'Please provide both email/username and password' });
  }

  const inputLower = rawInput.toLowerCase();

  try {
    let user = null;
    let isMatch = false;

    // 1. Try finding in MongoDB if connected
    if (isMongoConnected()) {
      user = await User.findOne({
        $or: [
          { email: inputLower },
          { username: rawInput },
          { username: { $regex: new RegExp(`^${escapeRegex(rawInput)}$`, 'i') } },
          { email: { $regex: new RegExp(`^${escapeRegex(inputLower)}$`, 'i') } }
        ]
      });

      if (user) {
        isMatch = await user.comparePassword(password);
      }
    }

    // 2. If not found or password didn't match in Mongo, check fallback DB
    if (!user || !isMatch) {
      const fbUsers = await fallbackDb.users.find({});
      const fbUser = fbUsers.find(u => {
        const uEmail = (u.email || '').trim().toLowerCase();
        const uName = (u.username || '').trim().toLowerCase();
        return uEmail === inputLower || uName === inputLower || uName === rawInput.toLowerCase();
      });

      if (fbUser) {
        const fbMatch = await bcrypt.compare(password, fbUser.password);
        if (fbMatch) {
          isMatch = true;
          // If Mongo is connected, auto-migrate this user to Mongo so future queries succeed
          if (isMongoConnected() && !user) {
            const newId = new mongoose.Types.ObjectId();
            await mongoose.connection.db.collection('users').insertOne({
              _id: newId,
              username: fbUser.username.trim(),
              email: fbUser.email.trim().toLowerCase(),
              password: fbUser.password,
              role: fbUser.role || 'user',
              createdAt: fbUser.createdAt ? new Date(fbUser.createdAt) : new Date()
            });
            user = await User.findById(newId);
          } else if (!user) {
            user = fbUser;
          }
        }
      }
    }

    if (!user || !isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const userId = user._id ? user._id.toString() : user.id;

    // Create token
    const payload = {
      user: {
        id: userId,
        role: user.role
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET || 'fallback_secret_key',
      { expiresIn: '24h' },
      (err, token) => {
        if (err) throw err;
        res.json({
          token,
          user: {
            id: userId,
            username: user.username,
            email: user.email,
            role: user.role
          }
        });
      }
    );
  } catch (err) {
    console.error('Login error:', err.message);
    res.status(500).json({ message: 'Server error: ' + err.message });
  }
};

exports.getProfile = async (req, res) => {
  try {
    let user = null;
    const reqUserId = req.user.id;

    if (isMongoConnected() && mongoose.Types.ObjectId.isValid(reqUserId)) {
      user = await User.findById(reqUserId).select('-password');
    }

    if (!user) {
      user = await fallbackDb.users.findById(reqUserId);
    }

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    const userId = user._id ? user._id.toString() : user.id;

    res.json({
      id: userId,
      username: user.username,
      email: user.email,
      role: user.role
    });
  } catch (err) {
    console.error('Profile fetch error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};
