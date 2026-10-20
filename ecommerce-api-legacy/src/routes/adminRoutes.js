const express = require('express');
const reportController = require('../controllers/reportController');
const { requireAdmin } = require('../middlewares/auth');

const router = express.Router();

router.get('/financial-report', requireAdmin, reportController.financialReport);

module.exports = router;
