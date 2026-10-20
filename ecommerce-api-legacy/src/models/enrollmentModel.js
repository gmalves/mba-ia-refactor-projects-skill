const { run } = require('../database');

function create(userId, courseId) {
    return run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId])
        .then(result => result.lastID);
}

module.exports = { create };
