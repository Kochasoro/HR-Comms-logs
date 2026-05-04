const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let flaskProcess;
let mainWindow;

/* =========================
CREATE WINDOW
========================= */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        autoHideMenuBar: true,
        show: false // wait until ready
    });

    waitForServer(() => {
        mainWindow.loadURL("http://127.0.0.1:5000");
        mainWindow.show();
    });
}

/* =========================
WAIT FOR FLASK SERVER
========================= */
function waitForServer(callback, retries = 20) {
    const req = http.get("http://127.0.0.1:5000", () => {
        callback();
    });

    req.on("error", () => {
        if (retries > 0) {
            setTimeout(() => waitForServer(callback, retries - 1), 500);
        } else {
            console.error("❌ Flask failed to start");
        }
    });

    req.end();
}

/* =========================
START FLASK BACKEND
========================= */
function startFlask() {
    let flaskPath;

    if (app.isPackaged) {
        flaskPath = path.join(process.resourcesPath, "backend", "run_desktop.exe");
    } else {
        flaskPath = path.join(__dirname, "backend", "run_desktop.exe");
    }

    flaskProcess = spawn(flaskPath, [], {
        detached: false,
        stdio: "ignore"
    });

    flaskProcess.on("error", (err) => {
        console.error("❌ Failed to start Flask:", err);
    });
}

/* =========================
APP READY
========================= */
app.whenReady().then(() => {
    startFlask();
    createWindow();
});

/* =========================
CLOSE HANDLING
========================= */
app.on("window-all-closed", () => {
    if (flaskProcess) flaskProcess.kill();
    if (process.platform !== "darwin") app.quit();
});