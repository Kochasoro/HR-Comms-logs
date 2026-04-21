const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const http = require('http');

let flaskProcess;

function waitForFlask(callback) {
    const check = () => {
        http.get('http://127.0.0.1:5000', (res) => {
            callback(); // Flask is ready
        }).on('error', () => {
            setTimeout(check, 300); // retry
        });
    };

    check();
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        autoHideMenuBar: true
    });

    win.loadURL("http://127.0.0.1:5000");
}

app.whenReady().then(() => {

    // start Flask
    flaskProcess = spawn('python', ['../run_desktop.py']);

    // WAIT until Flask is actually running
    waitForFlask(() => {
        createWindow();
    });
});

app.on('window-all-closed', () => {
    if (flaskProcess) flaskProcess.kill();
    if (process.platform !== 'darwin') app.quit();
});