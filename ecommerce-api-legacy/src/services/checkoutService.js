const AppError = require('../utils/AppError');
const { withTransaction } = require('../database');
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const { hashPassword } = require('../utils/password');

const DEFAULT_PASSWORD = '123456';
const CARD_RE = /^\d{16}$/;
const EMAIL_RE = /^\S+@\S+\.\S+$/;

// Validação única e central de entrada (presença + tipo + formato).
function validate(body) {
    const { usr, eml, pwd, c_id, card } = body;

    if (!usr || !eml || !c_id || !card) throw new AppError(400, 'Bad Request');
    if (typeof card !== 'string' || !CARD_RE.test(card)) throw new AppError(400, 'Bad Request');
    if (typeof eml !== 'string' || !EMAIL_RE.test(eml)) throw new AppError(400, 'Bad Request');

    const courseId = Number(c_id);
    if (!Number.isInteger(courseId) || courseId <= 0) throw new AppError(400, 'Bad Request');

    return { name: usr, email: eml, password: pwd, courseId, card };
}

// Fluxo de checkout: valida -> resolve curso -> decide pagamento -> cria/usa
// usuário -> matricula/pagamento/auditoria em uma transação única.
async function checkout(body) {
    const { name, email, password, courseId, card } = validate(body);

    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new AppError(404, 'Curso não encontrado');

    const status = card.startsWith('4') ? 'PAID' : 'DENIED';
    if (status === 'DENIED') throw new AppError(400, 'Pagamento recusado');

    const user = await userModel.findByEmail(email);
    const userId = user ? user.id : await userModel.create(name, email, hashPassword(password || DEFAULT_PASSWORD));

    return withTransaction(async () => {
        const enrollmentId = await enrollmentModel.create(userId, courseId);
        await paymentModel.create(enrollmentId, course.price, status);
        await auditModel.create(`Checkout curso ${courseId} por ${userId}`);
        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    });
}

module.exports = { checkout };
