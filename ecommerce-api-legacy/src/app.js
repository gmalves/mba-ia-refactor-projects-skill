const express = require('express');
const { initDb } = require('./database');
const { port } = require('./config/settings');
const apiRoutes = require('./routes');
const { notFound, errorHandler } = require('./middlewares/errorHandler');

// Composition root: cria o app, injeta camadas e sobe o servidor.
async function createApp() {
    await initDb();

    const app = express();
    app.use(express.json());
    app.use('/api', apiRoutes);

    app.use(notFound);
    app.use(errorHandler);

    return app;
}

if (require.main === module) {
    createApp()
        .then(app => {
            app.listen(port, () => {
                console.log(`LMS API rodando na porta ${port}...`);
            });
        })
        .catch(err => {
            console.error('Falha ao iniciar a aplicação:', err);
            process.exit(1);
        });
}

module.exports = createApp;
