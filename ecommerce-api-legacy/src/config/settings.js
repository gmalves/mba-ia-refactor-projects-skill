// Configuração central da aplicação — única fonte de configuração.
// Valores sensíveis vêm de variáveis de ambiente, com defaults seguros para dev.
module.exports = {
    port: Number(process.env.PORT || 3000),
    adminToken: process.env.ADMIN_TOKEN || 'dev-admin-token',
};
