// Erro de aplicação com status HTTP — usado para sinalizar falhas esperadas
// (validação, não encontrado, pagamento recusado) ao handler central de erros.
class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.name = 'AppError';
        this.status = status;
    }
}

module.exports = AppError;
