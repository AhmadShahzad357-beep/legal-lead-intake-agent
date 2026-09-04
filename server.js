/* Node.js frontend server. It serves the form and keeps WEBHOOK_SECRET private. */
const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, "frontend", "public");
const FRONTEND_PORT = Number(process.env.FRONTEND_PORT || 3000);
const BACKEND_PORT = Number(process.env.BACKEND_PORT || 5000);
const BACKEND_URL = process.env.BACKEND_URL || `http://127.0.0.1:${BACKEND_PORT}`;

function envValue(key) {
  if (process.env[key]) return process.env[key];
  const envPath = path.join(ROOT, ".env");
  if (!fs.existsSync(envPath)) return "";
  const line = fs.readFileSync(envPath, "utf8").split(/\r?\n/)
    .find((item) => item.trim().startsWith(`${key}=`));
  return line ? line.slice(line.indexOf("=") + 1).trim() : "";
}

const WEBHOOK_SECRET = envValue("WEBHOOK_SECRET");

function sendJson(response, status, body) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  response.end(JSON.stringify(body));
}

function serveStatic(request, response) {
  const requested = request.url === "/" ? "/index.html" : request.url.split("?")[0];
  const filePath = path.normalize(path.join(PUBLIC, requested));
  if (!filePath.startsWith(PUBLIC) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    response.writeHead(404); response.end("Not found"); return;
  }
  const contentTypes = { ".html": "text/html", ".css": "text/css", ".js": "application/javascript" };
  response.writeHead(200, { "Content-Type": `${contentTypes[path.extname(filePath)] || "application/octet-stream"}; charset=utf-8` });
  fs.createReadStream(filePath).pipe(response);
}

async function forwardLead(request, response) {
  let raw = "";
  request.on("data", (chunk) => {
    raw += chunk;
    if (raw.length > 50_000) request.destroy();
  });
  request.on("end", async () => {
    try {
      const payload = JSON.parse(raw || "{}");
      const url = new URL("/webhook/lead", BACKEND_URL);
      if (WEBHOOK_SECRET) url.searchParams.set("secret", WEBHOOK_SECRET);
      const upstream = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await upstream.text();
      response.writeHead(upstream.status, { "Content-Type": "application/json; charset=utf-8" });
      response.end(body);
    } catch (error) {
      sendJson(response, 502, { error: "Unable to submit your inquiry. Please call the office directly." });
    }
  });
}

const server = http.createServer((request, response) => {
  if (request.method === "POST" && request.url === "/api/intake") return forwardLead(request, response);
  if (request.method === "GET") return serveStatic(request, response);
  sendJson(response, 405, { error: "Method not allowed" });
});

const python = process.env.PYTHON || "python";
const flask = spawn(python, ["app.py"], { cwd: ROOT, stdio: "inherit" });
flask.on("error", () => console.error("Python backend could not start. Confirm Python is installed."));
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => { flask.kill(); server.close(() => process.exit(0)); });
}
server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`Port ${FRONTEND_PORT} is already in use. Stop the other app or run with a different port.`);
    console.error(`PowerShell: $env:FRONTEND_PORT=3001; npm start`);
  } else {
    console.error("Frontend server failed to start:", error.message);
  }
  flask.kill();
  process.exit(1);
});

server.listen(FRONTEND_PORT, () => {
  console.log(`Lead intake website: http://localhost:${FRONTEND_PORT}`);
  console.log(`Flask API: ${BACKEND_URL}`);
});
