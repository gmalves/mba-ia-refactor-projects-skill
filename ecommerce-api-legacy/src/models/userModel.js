const { run, get } = require('../database');

function create(name, email, passHash) {
    return run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passHash])
        .then(result => result.lastID);
}

function findByEmail(email) {
    return get('SELECT id, name, email FROM users WHERE email = ?', [email]);
}

function deleteById(id) {
    return run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { create, findByEmail, deleteById };
