import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { resolve } from 'node:path';

const localPython = resolve(process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const python = existsSync(localPython) ? localPython : process.platform === 'win32' ? 'python' : 'python3';
const child = spawn(python, ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8001', '--reload'], { stdio: 'inherit' });
child.on('error', error => {
  console.error(`Could not start the academic backend: ${error.message}\nCreate .venv and install requirements.txt first. See README.md.`);
  process.exitCode = 1;
});
child.on('exit', code => { process.exitCode = code ?? 0; });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
