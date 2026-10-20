const { get } = require('../database');

function findActiveById(id) {
    return get('SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1', [id]);
}

module.exports = { findActiveById };
