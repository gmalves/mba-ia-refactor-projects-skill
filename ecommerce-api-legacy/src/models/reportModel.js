const { all } = require('../database');

// Uma única consulta com JOINs substitui as queries N+1 do relatório.
function financialReportRows() {
    return all(`
        SELECT c.id AS course_id, c.title AS course_title,
               e.id AS enrollment_id, u.name AS student,
               p.amount AS amount, p.status AS status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id, e.id
    `);
}

module.exports = { financialReportRows };
