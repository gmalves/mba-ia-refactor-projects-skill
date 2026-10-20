const { run } = require('../database');

function create(enrollmentId, amount, status) {
    return run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status])
        .then(result => result.lastID);
}

module.exports = { create };
