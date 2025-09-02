const sqlite3 = require('sqlite3').verbose();

// Create or connect to the database file
const db = new sqlite3.Database('./passwords.db', (err) => {
    if (err) {
        return console.error('Error opening database', err.message);
    }
    console.log('Connected to the SQLite database.');
    createTablesAndSeedData();
});

function createTablesAndSeedData() {
    // db.serialize ensures commands run one after another
    db.serialize(() => {
        console.log('Starting database setup...');
        // Drop tables if they exist to start fresh
        db.run(`DROP TABLE IF EXISTS Credentials`);
        db.run(`DROP TABLE IF EXISTS Devices`);
        console.log('Old tables dropped.');

        // Create the Devices table
        db.run(`CREATE TABLE Devices (
            DeviceID TEXT PRIMARY KEY,
            Location TEXT,
            IPAddress TEXT
        )`, (err) => {
            if (err) console.error("Error creating Devices table", err.message);
            else console.log('Devices table created.');
        });

        // Create the Credentials table with a link to the Devices table
        db.run(`CREATE TABLE Credentials (
            CredentialID INTEGER PRIMARY KEY AUTOINCREMENT,
            DeviceID TEXT,
            Type TEXT NOT NULL,
            Value TEXT NOT NULL,
            FOREIGN KEY (DeviceID) REFERENCES Devices (DeviceID)
        )`, (err) => {
            if (err) console.error("Error creating Credentials table", err.message);
            else console.log('Credentials table created.');
        });

        // --- Synthetic Data ---
        const devices = [
            { id: 'ATM-CLE-001', location: 'Downtown Cleveland', ip: '10.1.10.5' },
            { id: 'ATM-CHI-007', location: 'O\'Hare Airport', ip: '10.2.15.12' },
            { id: 'ATM-NYC-003', location: 'Times Square', ip: '10.3.5.25' }
        ];

        const credentials = [
            { deviceId: 'ATM-CLE-001', type: 'BitLocker', value: '111111-222222-333333-444444-555555-666666-777777-888888' },
            { deviceId: 'ATM-CLE-001', type: 'BIOS', value: 'b!0s-cle-@dm!n' },
            { deviceId: 'ATM-CHI-007', type: 'BitLocker', value: '888888-777777-666666-555555-444444-333333-222222-111111' },
            { deviceId: 'ATM-CHI-007', type: 'BIOS', value: 'Ch!c@g0-S3cure' },
            { deviceId: 'ATM-NYC-003', type: 'BitLocker', value: '555555-123456-777777-987654-333333-112233-445566-778899' },
            { deviceId: 'ATM-NYC-003', type: 'BIOS', value: 'N3wY0rk-P@ss' }
        ];

        // Prepare reusable statements for inserting data
        const deviceStmt = db.prepare("INSERT INTO Devices (DeviceID, Location, IPAddress) VALUES (?, ?, ?)");
        devices.forEach(device => {
            deviceStmt.run(device.id, device.location, device.ip);
        });
        deviceStmt.finalize();
        console.log(`${devices.length} devices inserted.`);

        const credStmt = db.prepare("INSERT INTO Credentials (DeviceID, Type, Value) VALUES (?, ?, ?)");
        credentials.forEach(cred => {
            credStmt.run(cred.deviceId, cred.type, cred.value);
        });
        credStmt.finalize();
        console.log(`${credentials.length} credentials inserted.`);

        // Close the database connection
        db.close((err) => {
            if (err) return console.error(err.message);
            console.log('Database setup complete and connection closed.');
        });
    });
}
