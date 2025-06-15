// Test the LM Studio models parsing logic

const mockBackendResponse = {
  models: [
    "mistralai/magistral-small",
    "microsoft/phi-4-reasoning-plus", 
    "deepseek/deepseek-r1-0528-qwen3-8b",
    "microsoft/phi-4-mini-reasoning"
  ],
  provider: "lmstudio",
  count: 4
};

function estimateModelSize(modelId) {
  // Simple estimation logic
  if (modelId.includes('small') || modelId.includes('mini')) return '3GB';
  if (modelId.includes('large')) return '14GB';
  if (modelId.includes('8b')) return '8GB';
  return '7GB';
}

// Test the transformation
const models = mockBackendResponse.models.map((modelId) => ({
  id: modelId,
  name: modelId,
  provider: 'lmstudio',
  size: estimateModelSize(modelId),
  format: 'GGUF',
  status: 'available',
  port: 1234,
  parameters: {
    temperature: 0.7,
    maxTokens: 2048,
    topP: 0.9
  }
}));

console.log('✅ Transformed models:', JSON.stringify(models, null, 2));
console.log(`✅ Total models: ${models.length}`);

// Test with fetch call to real backend
async function testRealBackend() {
  try {
    const response = await fetch('http://127.0.0.1:8004/providers/lmstudio/models');
    const data = await response.json();
    console.log('🔍 Real backend response:', data);
    
    if (data.models && Array.isArray(data.models)) {
      console.log(`✅ Real backend has ${data.models.length} models`);
      console.log('📋 First 3 models:', data.models.slice(0, 3));
    }
  } catch (error) {
    console.error('❌ Error testing real backend:', error);
  }
}

testRealBackend();
