# Imgura Final

## Framework Cheat Sheet

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

## Rule & Vulnerablities

[Slide](./imgura-final.pdf)
