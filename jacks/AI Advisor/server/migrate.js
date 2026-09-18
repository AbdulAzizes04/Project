const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');

const datasetsDir = path.resolve(__dirname, '..', 'datasets');
const dbFile = path.join(__dirname, 'data', 'db.json');
const dbData = JSON.parse(fs.readFileSync(dbFile, 'utf8'));

async function runMigration() {
  try {
    await mongoose.connect('mongodb://localhost:27017/ai_advisor');
    console.log('Connected to MongoDB');
    const db = mongoose.connection.db;

    const userMap = new Map(); // oldId -> new ObjectId
    const datasetMap = new Map(); // oldId -> new ObjectId

    // 1. Migrate users
    for (const u of dbData.users) {
      const existing = await db.collection('users').findOne({ email: u.email.trim().toLowerCase() });
      let newUserId;
      if (existing) {
        newUserId = existing._id;
        console.log('User already exists in Mongo:', u.email, newUserId.toString());
      } else {
        newUserId = new mongoose.Types.ObjectId();
        await db.collection('users').insertOne({
          _id: newUserId,
          username: u.username.trim(),
          email: u.email.trim().toLowerCase(),
          password: u.password,
          role: u.role || 'user',
          createdAt: u.createdAt ? new Date(u.createdAt) : new Date()
        });
        console.log('Migrated user to Mongo:', u.username.trim(), u.email.trim().toLowerCase(), '->', newUserId.toString());
      }
      userMap.set(u._id, newUserId);
    }

    // 2. Migrate datasets
    for (const d of dbData.datasets) {
      const newOwnerId = userMap.get(d.uploadedBy);
      const existing = await db.collection('datasets').findOne({ filename: d.filename });
      let newDatasetId;
      const actualFilePath = path.join(datasetsDir, d.filename);

      if (existing) {
        newDatasetId = existing._id;
        await db.collection('datasets').updateOne(
          { _id: newDatasetId },
          { $set: { filepath: actualFilePath } }
        );
        console.log('Dataset already in Mongo, updated path:', d.name, newDatasetId.toString());
      } else {
        newDatasetId = new mongoose.Types.ObjectId();
        await db.collection('datasets').insertOne({
          _id: newDatasetId,
          name: d.name,
          filename: d.filename,
          filepath: actualFilePath,
          rowCount: d.rowCount || 0,
          columnCount: d.columnCount || 0,
          columns: d.columns || [],
          summary: d.summary || {},
          uploadedBy: newOwnerId,
          status: d.status || 'active',
          createdAt: d.createdAt ? new Date(d.createdAt) : new Date()
        });
        console.log('Migrated dataset to Mongo:', d.name, '->', newDatasetId.toString());
      }
      datasetMap.set(d._id, newDatasetId);

      // Also update filepath in dbData
      d.filepath = actualFilePath;
    }

    // 3. Migrate chat history
    for (const c of (dbData.chats || [])) {
      const newDatasetId = datasetMap.get(c.datasetId);
      const newUserId = userMap.get(c.userId);
      if (newDatasetId && newUserId) {
        const existing = await db.collection('chathistories').findOne({ datasetId: newDatasetId, userId: newUserId });
        if (!existing) {
          await db.collection('chathistories').insertOne({
            _id: new mongoose.Types.ObjectId(),
            datasetId: newDatasetId,
            userId: newUserId,
            messages: c.messages || [],
            updatedAt: c.updatedAt ? new Date(c.updatedAt) : new Date()
          });
          console.log('Migrated chat history for dataset:', c.datasetId);
        }
      }
    }

    // Update db.json with corrected filepaths
    fs.writeFileSync(dbFile, JSON.stringify(dbData, null, 2));
    console.log('Updated db.json filepaths successfully');

    const finalUserCount = await db.collection('users').countDocuments();
    const finalDatasetCount = await db.collection('datasets').countDocuments();
    console.log('FINAL COUNTS: users =', finalUserCount, ', datasets =', finalDatasetCount);

    return { success: true, users: finalUserCount, datasets: finalDatasetCount };
  } catch (err) {
    console.error('Migration failed:', err);
    throw err;
  }
}

if (require.main === module) {
  runMigration().then(() => process.exit(0)).catch(() => process.exit(1));
}

module.exports = runMigration;
