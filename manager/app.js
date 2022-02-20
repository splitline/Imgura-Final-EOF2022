const express = require('express');
const bodyParser = require('body-parser');

const fs = require('fs');
const child_process = require('child_process');

const axios = require('axios');

const TEAMS = require('./teams.json');
const TOKENS = require('./tokens.json');

const app = express();
const ctfdHost = process.env['CTFD_HOST'] || 'http://127.0.0.1:4000';

app.use(express.static('public'));
app.use(bodyParser.json());

app.use(function (req, res, next) {
    if (req.headers.token && !/^[0-9a-f]{32}$/.test(req.headers.token))
        return res.status(400).json({
            success: false,
            message: 'Weird token'
        });
    next();
});


app.get('/teams', (_, res) => {
    const teamIDs = Object.keys(TEAMS);
    const wafs = teamIDs.map(teamID => `
    <tr>
        <td>${teamID}</td>
        <td>${TEAMS[teamID].name}</td>
        <td>${30000 + parseInt(teamID)}</td>
        <td><a href="/waf/${teamID}">[WAF]</a></td>
    </tr>
    `).join('')
    res.send(`<!DOCTYPE html>
    <html><head><link rel="stylesheet" href="/style.css"></head>
    <body><h1>Teams</h1><table><thead><tr><th>Team ID</th><th>Team Name</th><th>Port</th><th>WAF</th></tr></thead>
    <tbody>${wafs}</tbody>
    </table></body></html>`);
});


app.get('/waf/:id', (req, res) => {
    const teamID = +req.params.id;
    const team = TEAMS[teamID];
    if (!team)
        return res.status(404).json({
            success: false,
            message: 'Team not found'
        });

    const wafContent = fs.readFileSync(`/service/files/waf_${teamID}.php`);
    res.type('txt').send(wafContent);
});


app.post('/api/get_token', (req, res) => {
    const token = req.body.token.toString();
    axios.get(`${ctfdHost}/api/v1/teams/me`, {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    }).then(({ data }) => {
	console.log(data)
        if (data.success !== true) {
            return res.status(401).json({
                success: false,
                message: 'Invalid token'
            });
        }

        res.json({
            success: true,
            message: 'Your token for this challenge is ' + TEAMS[data.data.id].token,
            data: TEAMS[data.data.id]
        }).send();
    }).catch(err =>{
	console.log(err.toString());
        res.json({
            success: false,
            message: 'Invalid token'
        }).send()
    }
    );
});

app.get('/api/me', (req, res) => {
    const teamId = TOKENS[req.headers.token];
    if (!teamId) {
        return res.status(401).json({
            success: false,
            message: 'Not authenticated'
        });
    }
    const teamName = TEAMS[teamId].name;
    const teamData = JSON.parse(fs.readFileSync(`./teams/team-${teamId}.json`));
    return res.json({
        success: true,
        message: 'Success',
        data: { ...teamData, name: teamName }
    }).send();
});

app.post('/api/restart', (req, res) => {
    const teamId = TOKENS[req.headers.token];
    if (!teamId) {
        return res.status(401).json({
            success: false,
            message: 'Not authenticated'
        });
    }

    const teamData = JSON.parse(fs.readFileSync(`./teams/team-${teamId}.json`));
    // rate limit 15 minutes
    const timeDiff = Date.now() - teamData.lastRestart
    if (timeDiff < 1000 * 60 * 15) {
        return res.status(429).json({
            success: false,
            message: `Rate limit exceeded. Please wait ${Math.ceil(15 - timeDiff / 1000 / 60)} minutes.`
        });
    }

    const port = 30000 + (+teamId);
    child_process.exec(`./start.sh ${teamId} ${port}`, (err) => {
        if (err) console.log(err);
    });

    teamData.lastRestart = Date.now();
    fs.writeFileSync(`./teams/team-${teamId}.json`, JSON.stringify(teamData, null, 2));
    return res.json({
        success: true,
        message: `Restarting your service at port ${port}...`
    });
});

app.post('/api/waf/update', (req, res) => {
    const teamId = TOKENS[req.headers.token];
    if (!teamId) {
        return res.status(401).json({
            success: false,
            message: 'Not authenticated'
        });
    }

    const waf = req.body.waf.toString();
    if (waf.length > 0xff)
        return res.status(400).json({
            success: false,
            message: 'WAF is too long (max 255 characters)'
        });


    const teamData = JSON.parse(fs.readFileSync(`./teams/team-${teamId}.json`));
    // rate limit: 30 seconds
    const timeDiff = Date.now() - teamData.lastPatch;
    if (timeDiff < 1000 * 30) {
        return res.status(429).json({
            success: false,
            message: `Rate limit exceeded. Please wait ${30 - timeDiff / 1000} seconds.`
        });
    }

    teamData.lastPatch = Date.now();
    fs.writeFileSync(`./teams/team-${teamId}.json`, JSON.stringify(teamData, null, 2));
    fs.writeFileSync(`/service/files/waf_${teamId}.php`, waf);
    return res.json({
        success: true,
        message: 'WAF updated'
    });
});

app.post("/api/flag", (req, res) => {
    const teamId = TOKENS[req.headers.token];
    if (!teamId) {
        return res.status(401).json({
            success: false,
            message: 'Not authenticated'
        });
    }
    const targetId = +req.body.id;
    const flag = req.body.flag.toString();
    if (teamId == targetId)
        return res.status(400).json({
            success: false,
            message: "You can't submit your own flag"
        });

    if (!TEAMS[targetId])
        return res.status(400).json({
            success: false,
            message: `Target team ${targetId} doesn't exist`
        });

    const targetFlag = fs.readFileSync(`/service/files/flag_${targetId}`).toString();
    console.log(`${teamId} submitted flag ${flag} for ${targetId}, correct flag is ${targetFlag}, ${flag.trim() === targetFlag.trim() ? 'correct' : 'incorrect'}`);
    if (flag.trim() === targetFlag.trim()) {
        const teamData = JSON.parse(fs.readFileSync(`./teams/team-${teamId}.json`));
        if (teamData.attacked.includes(targetId)) {
            return res.json({
                success: false,
                message: 'You already have this flag!'
            });
        }
        teamData.attacked.push(targetId);
        fs.writeFileSync(`./teams/team-${teamId}.json`, JSON.stringify(teamData, null, 2));
        return res.json({
            success: true,
            message: 'Flag accepted'
        });
    }
    return res.json({
        success: false,
        message: 'Flag incorrect'
    });
});




app.listen(8000, () => {
    console.log('Example app listening on 127.0.0.1:8000!');
});

