const express = require('express');
const userController = require('../controllers/userController');
const { requireAdmin } = require('../middlewares/auth');

const router = express.Router();

router.delete('/:id', requireAdmin, userController.deleteUser);

module.exports = router;
