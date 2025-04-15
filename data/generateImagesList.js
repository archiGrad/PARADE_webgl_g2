const fs = require('fs');
const path = require('path');

const directoryPath = path.join(__dirname, 'data');
const outputFilePath = path.join(__dirname, 'data/images.json');

fs.readdir(directoryPath, (err, files) => {
  if (err) {
    console.error('Error reading directory:', err);
    return;
  }

  const imageFiles = files.filter(file => file.endsWith('.png'));
  const jsonData = JSON.stringify({ images: imageFiles }, null, 2);

  fs.writeFile(outputFilePath, jsonData, (err) => {
    if (err) {
      console.error('Error writing file:', err);
      return;
    }
    console.log('images.json generated successfully!');
  });
});
