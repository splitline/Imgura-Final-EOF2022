<?php
include "waf.php";

require './vendor/autoload.php';
require './lib/Framework.php';

use Imgura\Core\{App, Request, Response};
use Hidehalo\Nanoid\Client;

$config = defined('APP_CONFIG') ? json_decode(file_get_contents(APP_CONFIG), true) : [];

// Main logic starts here
$app = new App($config);

$app->get('/', function (Request $request, Response $response) use ($app) {
    if (!isset($request->session->user)) {
        return $response->redirect('/login');
    }
    $user_id = $request->session->user['id'];
    $user = $app->db->select('users', ['id', 'name'], ['id' => $user_id]);
    if (!$user) {
        return $response->redirect('/login');
    }

    $images = $app->db->select('image', '*', ['user_id' => $user_id], true);

    $response->render('index.html', ['user' => $user, 'images' => $images]);
});

// image related

$app->get('/upload', function (Request $request, Response $response) use ($app) {
    if (!isset($request->session->user)) {
        return $response->redirect('/login?redirect=/upload');
    }
    $user_id = $request->session->user['id'];
    $user = $app->db->select('users', ['id', 'name'], ['id' => $user_id]);

    $response->render('upload.html', ['user' => $user]);
});

$app->post('/upload', function (Request $request, Response $response) use ($app) {
    if (!isset($request->session->user)) {
        return $response->redirect('/login');
    }
    $user_id = $request->session->user['id'];
    if (trim($request->form['url']) !== '') {
        $url = $request->form['url'];
        if (parse_url($url, PHP_URL_SCHEME) === null) {
            $url = 'http://' . $url;
        }
        $image = file_get_contents($url);
        if ($image === false) {
            return $response->redirect('/upload');
        }
        $ext = 'jpg';
        $http_response_header = array_merge(...array_map(function ($header) {
            [$key, $value] = explode(': ', $header, 2);
            return [$key => $value];
        }, $http_response_header));
        if (strpos($http_response_header['Content-Type'], 'image/') !== false) {
            $ext = substr($http_response_header['Content-Type'], 6);
        } else {
            [$_, $_, $type] = getimagesizefromstring($image);
            if ($type !== null)
                $ext = image_type_to_extension($type, false);
        }

        $image_nanoid = (new Client())->generateId(8, Client::MODE_DYNAMIC);
        $filename = "uploads/$image_nanoid.$ext";
        file_put_contents($filename, $image);
        $app->db->insert('image', [
            'user_id' => $user_id,
            'nanoid' => $image_nanoid,
            'path' => $filename,
        ]);
        $response->redirect('/view/' . $image_nanoid);
    } elseif ($request->files['image'] !== null) {
        $image = $request->files['image'];
        $image_name = $image['name'];
        $image_ext = strtolower(pathinfo($image_name, PATHINFO_EXTENSION));
        if (!in_array($image_ext, ['jpg', 'jpeg', 'png', 'gif'])) {
            return $response->redirect('/upload?error=invalid');
        }
        $image_nanoid = (new Client())->generateId(8, Client::MODE_DYNAMIC);
        $image_path = "uploads/$image_nanoid.$image_ext";

        if (!move_uploaded_file($image['tmp_name'], $image_path)) {
            return $response->redirect('/upload?error=unknown');
        }

        $app->db->insert('image', [
            'user_id' => $user_id,
            'nanoid' => $image_nanoid,
            'path' => $image_path,
        ]);
        $response->redirect('/view/' . $image_nanoid);
    }

    $response->redirect('/view/' . $image_nanoid);
});

$app->get('/view/:image_id', function (Request $request, Response $response) use ($app) {
    $image_id = $request->arg('image_id');
    $image = $app->db->select('image', '*', ['nanoid' => $image_id]);
    if (!$image) {
        return $response->redirect('/');
    }
    $response->render('view.html', ['image' => $image, 'user' => $request->session->user ?? null]);
});

$app->get('/download/:image_id', function (Request $request, Response $response) use ($app) {
    $image_id = $request->arg('image_id');
    $image = $app->db->select('image', '*', ['nanoid' => $image_id]);
    if (!$image) {
        return $response->redirect('/');
    }
    $response->sendFile($image['path'], true);
});

$app->post('/api/image_info', function (Request $request, Response $response) use ($app) {
    $json = $request->body();
    $image_file = $json['image'];
    $image_info = getimagesize($image_file);
    $response->json([
        'width' => $image_info[0],
        'height' => $image_info[1],
        'mime' => $image_info['mime'],
        'size' => filesize($image_file),
    ]);
});

// account

$app->get('/login', function (Request $req, Response $res) {
    $context = [
        'error' => $req->query['error'] ?? null,
        'redirect' => $req->query['redirect'] ?? '/',
    ];
    $res->render('login.html', $context);
});


$app->post('/login', function (Request $req, Response $res) use ($app) {
    $form = $req->body();
    $username = $form['username'];
    $password = sha1($form['password']);
    $redirect = $req->query['redirect'] ?? '/';

    if (!preg_match("/^[a-z][a-z0-9_]{4,20}$/i", $username))
        return $res->redirect("/login?error=1&redirect=$redirect");

    $user = $app->db->select('users', '*', ['name' => $username]);
    if (empty($user)) {
        $user['name'] = $username;
        $user['id'] = $app->db->insert('users', ['name' => $username, 'password' => $password]);
    } else if ($user['password'] !== $password) {
        return $res->redirect("/login?error=2&redirect=$redirect");
    }
    $req->session->user = ['id' => $user['id'], 'name' => $user['name']];
    $res->redirect($redirect);
});

$app->get('/logout', function (Request $req, Response $res) {
    $req->session->destroy();
    $res->redirect('/');
});

// admin

$app->get('/admin', function (Request $req, Response $res) use ($app) {
    if (!isset($req->session->user)) {
        return $res->redirect('/login?redirect=/admin');
    }
    $user_id = $req->session->user['id'];
    $user = $app->db->select('users', ['id', 'name', 'admin'], ['id' => $user_id]);
    if (!$user['admin']) {
        return $res->redirect('/');
    }
    $users = $app->db->select('users', ['id', 'name', 'admin'], [], true);
    $stats = [
        'image' => $app->db->queryOne('SELECT COUNT(*) as count FROM image')['count'],
        'user' => $app->db->queryOne('SELECT COUNT(*) as count FROM users')['count'],
    ];
    return $res->render('admin.html', ['user' => $user, 'users' => $users, 'stats' => $stats]);
});

$app->post('/admin/give-admin', function (Request $req, Response $res) use ($app) {
    if (!isset($req->session->user)) {
        return $res->redirect('/login?redirect=/admin');
    }
    $user_id = $req->session->user['id'];
    $user = $app->db->select('users', ['id', 'name', 'admin'], ['id' => $user_id]);
    if (!$user['admin']) {
        return $res->redirect('/');
    }
    $user_id = $req->form['user_id'];
    $app->db->update('users', ['admin' => 1], ['id' => $user_id]);
    return $res->redirect('/admin');
});

$app->post('/admin/backup', function (Request $req, Response $res) use ($app) {
    if (!isset($req->session->user)) {
        return $res->redirect('/login?redirect=/admin');
    }
    $user_id = $req->session->user['id'];
    $user = $app->db->select('users', ['id', 'name', 'admin'], ['id' => $user_id]);
    if (!$user['admin']) {
        return $res->redirect('/');
    }

    $backup_user_id = $app->db->quote($req->form['user_id']);
    $backup_user = $app->db->select('users', ['id', 'name'], "id = $backup_user_id");
    if (empty($backup_user)) {
        return $res->redirect('/admin');
    }
    $images = $app->db->select('image', ['path'], "user_id = $backup_user_id", true);
    $backup_path = sprintf('backup/%s-%s.zip', $backup_user['name'], date('Y-m-d'));
    $command = sprintf('zip -j %s %s', $backup_path, implode(' ', array_column($images, 'path')));
    exec($command);
    $res->output("
    Backup created: $backup_path, Redirecting...
    <script>
        setTimeout(function() {
            window.location.href = '/$backup_path';
        }, 1000);
    </script>
    ");
});

$app->run();
