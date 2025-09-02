const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
const port = 4000;

// Connect to the SQLite database file
const db = new sqlite3.Database('./passwords.db', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
        console.error('Error opening database', err.message);
    } else {
        console.log('Successfully connected to the SQLite database.');
    }
});

app.use(cors()); // Enable Cross-Origin Resource Sharing

// Define the main API endpoint
app.get('/credentials', (req, res) => {
    const { deviceId, credentialType } = req.query;

    console.log(`[INFO] Received request for deviceId: ${deviceId}, type: ${credentialType}`);

    // Basic validation
    if (!deviceId || !credentialType) {
        console.log('[WARN] Bad request: Missing deviceId or credentialType');
        return res.status(400).json({ error: 'Missing required query parameters: deviceId, credentialType' });
    }

    // Securely query the database using parameterized queries to prevent SQL injection
    const sql = `SELECT Value FROM Credentials WHERE DeviceID = ? AND Type = ?`;

    db.get(sql, [deviceId, credentialType], (err, row) => {
        if (err) {
            console.error('[ERROR] Database query error:', err.message);
            return res.status(500).json({ error: 'Internal server error' });
        }
        if (row) {
            console.log(`[SUCCESS] Found credential for ${deviceId}`);
            res.json({
                deviceId: deviceId,
                type: credentialType,
                value: row.Value
            });
        } else {
            console.log(`[INFO] No credential found for ${deviceId}`);
            res.status(404).json({ error: 'Credential not found' });
        }
    });
});

app.listen(port, () => {
    console.log(`Credential service listening on port ${port}`);
});
