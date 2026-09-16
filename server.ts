import express from "express";
import path from "path";
import http from "http";
import { spawn, ChildProcess } from "child_process";
import { createServer as createViteServer } from "vite";

const PORT = 3000;
const FASTAPI_PORT = 8001;
const FASTAPI_URL = `http://127.0.0.1:${FASTAPI_PORT}`;

let pyProcess: ChildProcess | null = null;

function startFastAPI(): Promise<void> {
  return new Promise((resolve) => {
    console.log(`[Server] Starting FastAPI backend on port ${FASTAPI_PORT}...`);
    pyProcess = spawn("python3", ["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", String(FASTAPI_PORT)], {
      stdio: "inherit",
      env: { ...process.env },
    });

    pyProcess.on("error", (err) => {
      console.error("[Server] Failed to start Python backend:", err);
    });

    pyProcess.on("exit", (code, signal) => {
      console.log(`[Server] Python backend exited with code ${code}, signal ${signal}`);
    });

    // Poll until FastAPI is responding
    let attempts = 0;
    const interval = setInterval(() => {
      attempts++;
      http
        .get(`${FASTAPI_URL}/api/health`, (res) => {
          if (res.statusCode === 200) {
            clearInterval(interval);
            console.log(`[Server] FastAPI backend is healthy on ${FASTAPI_URL}`);
            resolve();
          }
        })
        .on("error", () => {
          if (attempts >= 40) {
            clearInterval(interval);
            console.warn("[Server] FastAPI health check timed out, proceeding anyway...");
            resolve();
          }
        });
    }, 250);
  });
}

async function startServer() {
  await startFastAPI();

  const app = express();

  // Reverse proxy all /api/* requests to FastAPI backend
  app.use("/api", (req, res) => {
    const targetUrl = new URL(`/api${req.url}`, FASTAPI_URL);

    const proxyReq = http.request(
      targetUrl,
      {
        method: req.method,
        headers: {
          ...req.headers,
          host: `127.0.0.1:${FASTAPI_PORT}`,
        },
      },
      (proxyRes) => {
        res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
        proxyRes.pipe(res, { end: true });
      }
    );

    proxyReq.on("error", (err) => {
      console.error(`[Proxy Error] ${req.method} ${req.url}:`, err.message);
      if (!res.headersSent) {
        res.status(502).json({
          error: "Bad Gateway",
          message: "Unable to connect to FastAPI backend.",
          detail: err.message,
        });
      }
    });

    req.pipe(proxyReq, { end: true });
  });

  // Vite development middleware or production static serving
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  const server = app.listen(PORT, "0.0.0.0", () => {
    console.log(`[Server] Full-Stack App listening on http://0.0.0.0:${PORT}`);
  });

  // Graceful termination
  const cleanUp = () => {
    console.log("[Server] Shutting down...");
    if (pyProcess) {
      try {
        pyProcess.kill("SIGTERM");
      } catch (e) {
        // ignore
      }
    }
    server.close(() => process.exit(0));
  };

  process.on("SIGINT", cleanUp);
  process.on("SIGTERM", cleanUp);
}

startServer().catch((err) => {
  console.error("[Server] Fatal error on startup:", err);
  if (pyProcess) {
    pyProcess.kill();
  }
  process.exit(1);
});
