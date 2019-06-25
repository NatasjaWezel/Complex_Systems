'use strict';

// Imports
var url = require('url');
const express = require('express');
const cors = require('cors');
const http = require('http');
const path = require('path');
const bodyParser = require('body-parser');
const compression = require('compression');
const spawn = require("child_process").spawn;
const exec = require("child_process").exec;

const app = express();
app.use(cors());

app.use(compression());

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));
// parse application/json
app.use(bodyParser.json());

function addHeaders(res) {
    res.header('Content-Type', 'application/json');
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    return res;
}

// Run python processes -> const pythonProcess = spawn('python',["path/to/script.py", arg1, arg2, ...]);
/** End points */
app.post('/run', (req, res) => {
    res = addHeaders(res);
    const vals = Object.values(req.body);
    res.status(200);
    const runCmd = ["../../model/run.py", req.body.its, 'False', 1, vals[0], vals[1], vals[2], vals[3], vals[4]];
    console.log(runCmd);
    const pythonProcess = spawn('python', runCmd);
    pythonProcess.stdout.setEncoding("utf8");
    pythonProcess.stdout.on('data', (data) => {
        console.log(data);

        const cmd = 'gource --hide dirnames, filenames code.log -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.mp4';
        exec(cmd, (err, stdout, stderr) => {
            if (err) {
              console.error(`exec error: ${err}`);
              return;
            }
            res.json({ output: 'success'});
            console.log('Created video');
            res.end();
        });
    })
});


app.get('/test', (req, res) => {
    console.log('Testing...');
    const cmd = 'gource --hide dirnames, filenames code.log -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.mp4';

    exec(cmd, (err, stdout, stderr) => {
        if (err) {
          console.error(`exec error: ${err}`);
          return;
        }
        console.log('done!');
        res.status(200);
        res.end();
    });
});



/**
 * Serve index.html and let Angular do routing for all other endpoints
 */ 
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist/frontend/index.html'));
});


// Basic error logger/handler
app.use(function (err, req, res, next) {
    res.status(500).send(err.message || 'Something broke!');
    next(err || new Error('Something broke!'));
});

if (module === require.main) {
    // Start server
    const server = app.listen(process.env.PORT || 8080, function () {
        const port = server.address().port;

        console.log('Listening on port %s', port);
        console.log('Ctrl + C to close the server.');
    })
}

module.exports = app;