const checkoutService = require('../services/checkoutService');

async function checkout(req, res, next) {
    try {
        const result = await checkoutService.checkout(req.body);
        res.status(200).json(result);
    } catch (err) {
        next(err);
    }
}

module.exports = { checkout };
