// Test for size parsing function to ensure sorting works correctly
// This demonstrates the parseSize function fixes for sort by size

const testParseSize = (sizeStr) => {
  if (!sizeStr) return 0;
  
  // Handle different size formats: "3.5 GB", "1.59GB", "4.87 GB", "gguf", etc.
  const cleanStr = sizeStr.toString().toLowerCase().trim();
  
  // Extract number from the string
  const match = cleanStr.match(/([0-9.]+)\s*(gb|mb|kb)?/);
  if (!match) return 0;
  
  const value = parseFloat(match[1]);
  const unit = match[2] || 'gb'; // Default to GB if no unit specified
  
  // Convert to GB for consistent comparison
  switch (unit) {
    case 'kb':
      return value / (1024 * 1024);
    case 'mb':
      return value / 1024;
    case 'gb':
    default:
      return value;
  }
};

// Test cases that would appear in the Model Manager
const testCases = [
  { input: "1.59 GB", expected: 1.59 },
  { input: "3.56 GB", expected: 3.56 },
  { input: "4.87 GB", expected: 4.87 },
  { input: "13.35 GB", expected: 13.35 },
  { input: "3.11 GB", expected: 3.11 },
  { input: "1.88 GB", expected: 1.88 },
  { input: "62.81 GB", expected: 62.81 },
  { input: "13.35 GB", expected: 13.35 },
  { input: "3.83 GB", expected: 3.83 },
  { input: "1.49 GB", expected: 1.49 },
  { input: "8.43 GB", expected: 8.43 },
  { input: "4.67 GB", expected: 4.67 },
  { input: "1.5 GB", expected: 1.5 },
  { input: "2.87 GB", expected: 2.87 },
  { input: "gguf", expected: 0 }, // Edge case
  { input: "1024 MB", expected: 1 },
  { input: "512MB", expected: 0.5 }
];

console.log("Testing parseSize function:");
testCases.forEach(({ input, expected }) => {
  const result = testParseSize(input);
  const passed = Math.abs(result - expected) < 0.01;
  console.log(`${input} -> ${result} GB (expected: ${expected}) ${passed ? '✅' : '❌'}`);
});

// Test sorting behavior
const testModels = [
  { name: "Model A", size: "13.35 GB" },
  { name: "Model B", size: "1.59 GB" },
  { name: "Model C", size: "4.87 GB" },
  { name: "Model D", size: "3.56 GB" }
];

const sortedAsc = [...testModels].sort((a, b) => testParseSize(a.size) - testParseSize(b.size));
const sortedDesc = [...testModels].sort((a, b) => testParseSize(b.size) - testParseSize(a.size));

console.log("\nSorting test (ascending):");
sortedAsc.forEach(model => console.log(`${model.name}: ${model.size} (${testParseSize(model.size)} GB)`));

console.log("\nSorting test (descending):");
sortedDesc.forEach(model => console.log(`${model.name}: ${model.size} (${testParseSize(model.size)} GB)`));

// export { testParseSize };
