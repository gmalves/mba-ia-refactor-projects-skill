const reportModel = require('../models/reportModel');

// Agrega as linhas do JOIN em um relatório por curso, preservando o formato
// original: { course, revenue, students: [{ student, paid }] }.
async function buildFinancialReport() {
    const rows = await reportModel.financialReportRows();

    const courses = new Map();
    for (const row of rows) {
        if (!courses.has(row.course_id)) {
            courses.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
        }

        const course = courses.get(row.course_id);
        if (row.enrollment_id == null) continue;

        const paid = row.amount != null ? row.amount : 0;
        course.students.push({ student: row.student || 'Unknown', paid });

        if (row.status === 'PAID' && row.amount != null) {
            course.revenue += row.amount;
        }
    }

    return Array.from(courses.values());
}

module.exports = { buildFinancialReport };
