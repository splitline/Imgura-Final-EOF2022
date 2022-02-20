# Imgura LLC

## Framework

```php
$app->get('/:id/:name', function(Request $req, Response $res) {
    // Request
    $req->args; // args from url: array('id' => '...', 'name' => '...')
    $req->ip(); // get client ip
    $req->body(); // auto parsed body base on Content-Type
    
    // Response
    $res->output('Hello, world!');
    $res->render('index.html', ['title' => 'Home']); // twig template
    $res->render('{{title}}', ['title' => 'Home']); // render string
    $res->redirect('/', 302);  // redirect
    $res->json(['foo' => 'bar']); // json response
    $res->sendFile('/path/to/file', $download = true); // send file
});

$app->['get', 'post', 'put', 'delete', 'patch'](...);
```

## Vulns.

### Exploitable
1. `$req->body()`: XXE, can trigger unserialize by phar://
2. `Session`: unserialize
3. `$res->redirect`: SSTI
4. admin command injection
5. upload webshell by url

### Minor bugs / not exploitable
1. `$req->ip()`: forged ip

### Gadget chain
1. Logger::__destruct() -> `file_put_contents`
2. Response::__destruct() -> Response::status() -> App::handleStatus() -> `$callback($req, $res)` (e.g. `passthru('GET /path/;{ls,-al}', $res)`)

- admin pass = 'VU5KmCL8l0CAFuJfb1s3dbwaPWq8Fm9akdRF4qJ34Q0'