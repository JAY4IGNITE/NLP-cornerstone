const fs = require('fs');
const path = require('path');
const srcDir = './src';
const compDir = './src/components';

let appContent = fs.readFileSync(path.join(srcDir, 'App.tsx'), 'utf8');
appContent = appContent.replace(/import\s+\{\s*Aurora\s*\}\s+from\s+[\"']\.\/reactbits\/Aurora[\"'];?/, "import Aurora from './reactbits/Aurora';");
appContent = appContent.replace(/\s*config=\{\{[\s\S]*?\}\}\s*initialOpacity=\{0\}\s*animateOpacity\s*scale=\{0\.\d+\}\s*animateScale/g, '');
fs.writeFileSync(path.join(srcDir, 'App.tsx'), appContent);

const files = fs.readdirSync(compDir).filter(f => f.endsWith('.tsx'));
files.forEach(f => {
  const fp = path.join(compDir, f);
  let content = fs.readFileSync(fp, 'utf8');
  content = content.replace(/\s*config=\{\{[\s\S]*?\}\}\s*initialOpacity=\{0\}\s*animateOpacity\s*scale=\{0\.\d+\}\s*animateScale/g, '');
  fs.writeFileSync(fp, content);
});
console.log('Fixed props and imports!');
