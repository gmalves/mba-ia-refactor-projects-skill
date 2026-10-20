const AppError = require('../utils/AppError');

function notFound(req, res) {
    res.status(404).send('Rota não encontrada');
}

// Handler central: erros esperados viram resposta com status/mensagem;
// erros inesperados viram 500 genérico (sem vazar stack ao cliente).
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.status).send(err.message);
    }
    console.error(err);
    res.status(500).send('Erro interno');
}

module.exports = { notFound, errorHandler };
