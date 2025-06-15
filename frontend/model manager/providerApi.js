// providerApi.js
// Express API for provider control
const express = require('express');
const ProviderController = require('./providerController');
const router = express.Router();

const providerController = new ProviderController();

// Start provider
router.post('/:provider/start', async (req, res) => {
  try {
    const { provider } = req.params;
    const { modelPath } = req.body;
    const result = await providerController.startProvider(provider, modelPath);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Stop provider
router.post('/:provider/stop', async (req, res) => {
  try {
    const { provider } = req.params;
    const result = await providerController.stopProvider(provider);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Status provider
router.get('/:provider/status', async (req, res) => {
  try {
    const { provider } = req.params;
    const result = await providerController.getProviderStatus(provider);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get log
router.get('/:provider/log', async (req, res) => {
  try {
    const { provider } = req.params;
    const result = await providerController.getProviderLog(provider);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

module.exports = router;
