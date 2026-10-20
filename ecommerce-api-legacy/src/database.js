const sqlite3 = require('sqlite3').verbose();
const { hashPassword } = require('./utils/password');

let db = null;

// Inicializa o banco em memória: DDL + seeds. Com foreign keys e cascade,
// para manter a integridade referencial ao excluir registros.
async function initDb() {
    if (db) return db;
    db = new sqlite3.Database(':memory:');

    await run('PRAGMA foreign_keys = ON');
    await run('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, pass TEXT NOT NULL)');
    await run('CREATE TABLE courses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL)');
    await run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (course_id) REFERENCES courses(id))');
    await run('CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE)');
    await run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, created_at DATETIME)');

    await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
    await run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
    await run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");

    return db;
}

function getDb() {
    if (!db) throw new Error('Database not initialized');
    return db;
}

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().run(sql, params, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().get(sql, params, (err, row) => {
            if (err) return reject(err);
            resolve(row);
        });
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

// Executa `work` em uma transação atômica (commit único / rollback no erro).
async function withTransaction(work) {
    await run('BEGIN');
    try {
        const result = await work();
        await run('COMMIT');
        return result;
    } catch (err) {
        await run('ROLLBACK');
        throw err;
    }
}

module.exports = { initDb, getDb, run, get, all, withTransaction };
