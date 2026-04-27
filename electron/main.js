const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess;

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        autoHideMenuBar: true
    });

    win.loadURL("http://127.0.0.1:5000");
}

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
}

app.whenReady().then(() => {
    startFlask();

    setTimeout(createWindow, 3000);
});

app.on("window-all-closed", () => {
    if (flaskProcess) flaskProcess.kill();
    if (process.platform !== "darwin") app.quit();
});