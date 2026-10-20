const { run } = require('../database');

function create(action) {
    return run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
}

module.exports = { create };
