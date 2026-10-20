const { adminToken } = require('../config/settings');

// Proteção mínima de endpoints sensíveis via token de admin (header X-Admin-Token).
function requireAdmin(req, res, next) {
    const token = req.headers['x-admin-token'];
    if (!token || token !== adminToken) {
        return res.status(401).send('Não autorizado');
    }
    next();
}

module.exports = { requireAdmin };
