(function () {
    // utils
    function show(elem) {
        elem.classList.remove('hidden');
    }

    function hide(elem) {
        elem.classList.add('hidden');
    }

    function auth(token) {
        fetch('/api/me', {
            headers: { 'Token': token }
        }).then(res => res.json()).then(res => {
            if (res.success) {
                show(document.querySelector('#manage-panel'));
                document.getElementById('team-id').innerText = res.data.id;
                document.getElementById('team-name').innerText = res.data.name;
                document.getElementById('team-token').innerText = token;

                document.getElementById('instance-url').innerText = `http://${location.hostname}:${30000 + res.data.id}/`;
                document.getElementById('last-recreate').innerText = res.data.lastRestart ? new Date(res.data.lastRestart).toLocaleString() : "Never";
                document.getElementById('last-update').innerText = res.data.lastPatch ? new Date(res.data.lastPatch).toLocaleString() : 'Never';

                document.getElementById('submit-flag-api').innerText = `curl '${location.origin}/api/flag' -H 'Content-type: application/json' -H 'Token: ${token}' --data '{"id": <team-id>, "flag": "EOF{deadbeef}"}'`;
                fetch('/waf/' + res.data.id).then(res => res.text()).then(res => {
                    document.querySelector('textarea[name="waf"]').value = res;
                })

                window.token = token;
            } else {
                localStorage.removeItem('token');
                alert(res.message);
                window.location.reload();
            }
        });
    }

    // ui
    document.querySelector('#auth-panel button').addEventListener('click', () => {
        const ctfdToken = document.querySelector('#ctfd-token').value;
        fetch('/api/get_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: ctfdToken })
        }).then(res => res.json()).then(res => {
            if (res.success) {
                localStorage.setItem('token', res.data.token);
                window.location.reload();
            } else {
                alert(res.message);
            }
        });
    });

    document.getElementById('restart-instance').addEventListener('click', () => {
        fetch('/api/restart', {
            headers: { 'Token': window.token, 'Content-Type': 'application/json' },
            method: 'POST',
        }).then(res => res.json()).then(res => {
            alert(res.message);
        });
    });

    document.getElementById('submit-flag').addEventListener('submit', e => {
        e.preventDefault();
        const form = e.target;
        const data = new FormData(form);
        fetch('/api/flag', {
            headers: { 'Token': window.token, 'Content-Type': 'application/json' },
            method: 'POST',
            body: JSON.stringify({
                id: data.get('team'),
                flag: data.get('flag')
            })
        }).then(res => res.json()).then(res => {
            alert(res.message);
        });
    });

    document.getElementById('update-waf').addEventListener('submit', e => {
        e.preventDefault();
        const form = e.target;
        const data = new FormData(form);
        fetch('/api/waf/update', {
            headers: { 'Token': window.token, 'Content-Type': 'application/json' },
            method: 'POST',
            body: JSON.stringify({ waf: data.get('waf') })
        }).then(res => res.json()).then(res => {
            alert(res.message);
        });
    });

    // load
    window.onload = () => {
        const token = localStorage.getItem('token');
        if (token) {
            auth(token);
        } else {
            show(document.querySelector('#auth-panel'));
        }
    };
})();