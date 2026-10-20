const userModel = require('../models/userModel');

async function deleteUser(req, res, next) {
    try {
        // Foreign keys com ON DELETE CASCADE removem matrículas e pagamentos.
        await userModel.deleteById(Number(req.params.id));
        res.send('Usuário deletado');
    } catch (err) {
        next(err);
    }
}

module.exports = { deleteUser };
