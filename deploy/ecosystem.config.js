module.exports = {
  apps: [
    {
      name: "portfolio-api",
      cwd: "/srv/portfolio-tracker/current/api",
      script: ".venv/bin/uvicorn",
      args: "app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers",
      interpreter: "none",
      max_memory_restart: "400M",
      out_file: "/var/log/portfolio/api.out.log",
      error_file: "/var/log/portfolio/api.err.log",
      time: true,
    },
    {
      name: "portfolio-web",
      cwd: "/srv/portfolio-tracker/current/web",
      script: ".next/standalone/server.js",
      env: { NODE_ENV: "production", PORT: "3000", HOSTNAME: "127.0.0.1", API_URL: "http://127.0.0.1:8000" },
      max_memory_restart: "300M",
      out_file: "/var/log/portfolio/web.out.log",
      error_file: "/var/log/portfolio/web.err.log",
      time: true,
    },
  ],
};
