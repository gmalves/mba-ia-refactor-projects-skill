const crypto = require('crypto');

const KEY_LENGTH = 64;

// Hash moderno (scrypt) com salt por senha, no formato "salt:hash".
function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${hash}`;
}

// Comparação em tempo constante (para uso futuro de autenticação).
function verifyPassword(password, stored) {
    const [salt, hash] = stored.split(':');
    const candidate = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    const a = Buffer.from(hash);
    const b = Buffer.from(candidate);
    if (a.length !== b.length) return false;
    return crypto.timingSafeEqual(a, b);
}

module.exports = { hashPassword, verifyPassword };
