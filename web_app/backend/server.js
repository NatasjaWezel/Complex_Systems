'use strict';

// Imports
var url = require('url');
const express = require('express');
const cors = require('cors');
const http = require('http');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const compression = require('compression');
const spawn = require("child_process").spawn;
const exec = require("child_process").exec;

const app = express();
app.use(cors());
app.use(compression());

// var dir = path.join(__dirname, 'dist/frontend');
// app.use(express.static(dir));

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

        const cmd = 'gource --seconds-per-day 5 --hide dirnames, filenames ./vid/code.log -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 web_output/gource.mp4';
        exec(cmd, (err, stdout, stderr) => {
            if (err) {
              console.error(`exec error: ${err}`);
              return;
            }
            res.json({
                output: 'success',
                gource: {'url': 'gource.mp4', 'type': 'video/mp4'}
            });
            console.log('Created video');
            res.end();
        });
    })
});


app.get('/file/*', (req, res) => {
    res = addHeaders(res);
    let file = '';
    if (Object.keys(req.query).length > 0) {
        file = req.url.substring(
            6, // Skip /file/ 
            req.url.lastIndexOf("?")
        );
    } else {
        file = req.url.substr(6);
    }
    const type = req.query.type;

    var s = fs.createReadStream('./web_output/' + file);
    s.on('open', function () {
        res.set('Content-Type', type);
        s.pipe(res);
    });
    s.on('error', function () {
        res.set('Content-Type', 'text/plain');
        res.status(404).end('Not found');
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
        server.setTimeout(1000*60*5);
        console.log('Listening on port %s', port);
        console.log('Ctrl + C to close the server.');
    })
}

module.exports = app;