<?php

namespace Imgura\Core;

use \Twig\Loader\FilesystemLoader;
use \Twig\Environment;
use \Twig\Error\LoaderError;

require_once './lib/Session.php';
require_once './lib/Request.php';
require_once './lib/Response.php';
require_once './lib/Logger.php';
require_once './lib/Database.php';

class App
{
    public $db = null;
    public $twig = null;
    public $session = null;
    private $logger = null;

    // configuration
    public $config = [
        'template.dir' => './templates',
        'session.secret' => 'default-secret-meow!!!',

        'db.host' => 'database',
        'db.name' => 'imgura',
        'db.user' => 'root',
        'db.pass' => 'p4ssw0rd',
    ];

    // special handlers
    private $errorHandler = [
        404 => null,
        500 => null,
    ];

    private $routes = array(
        'GET' => array(), 'POST' => array(),
        'PUT' => array(), 'DELETE' => array()
    );

    public function __construct($config = [])
    {
        if (is_array($config))
            $this->config = array_merge($this->config, $config);

        $this->logger = new Logger();
        $loader = new \Twig\Loader\FilesystemLoader($this->config['template.dir']);
        $this->renderer = new \Twig\Environment($loader);

        $this->db = new Database(
            $this->config['db.host'],
            $this->config['db.name'],
            $this->config['db.user'],
            $this->config['db.pass']
        );
        $this->session = new Session($this->config['session.secret']);
    }

    public function run()
    {
        $path_parts = explode('/', strtolower(trim($this->uri(), '/')));
        $requestMethod = $this->requestMethod();
        $routes = array();
        if (isset($this->routes[$requestMethod])) {
            $routes = $this->routes[$requestMethod];
        }

        $res = new Response($this);
        $args = array();

        do {
            $requestPath = '/' . implode('/', $path_parts);

            if (isset($routes[$requestPath])) {
                $callback = $routes[$requestPath]['callback'];
                $keys = $routes[$requestPath]['keys'];
                if (count($args) !== count($keys)) {
                    $res->status(404);
                    return;
                }
                $args = array_combine($keys, $args);
                if (is_callable($callback)) {
                    try {
                        $req = new Request($this, $args);
                        $callback($req, $res);
                        $this->session->save();
                        return;
                    } catch (\Exception $e) {
                        $res->status(500);
                        $this->logger->log($e->getMessage());
                        return;
                    }
                }
            }
        } while(($args[] = array_pop($path_parts)) !== null);

        // not found at last
        $res->status(404);
    }

    public function __call($name, $arguments)
    {
        if (in_array($name, ['get', 'post', 'put', 'delete', 'patch']) && count($arguments) === 2) {
            $method = strtoupper($name);
            $path = $arguments[0];
            $callback = $arguments[1];

            // retrieve argument routes (e.g. /:id/:name)
            $path_parts = explode('/', strtolower(trim($path, '/')));
            $keys = array();
            while (count($path_parts) > 0) {
                $key = array_pop($path_parts);
                if (strpos($key, ':') === 0) {
                    $key = substr($key, 1);
                    $keys[] = $key;
                    continue;
                } else {
                    $path_parts[] = $key;
                    break;
                }
            }

            // add route
            $path = '/' . implode('/', $path_parts);
            $this->routes[$method][$path] = array(
                'callback' => $callback,
                'keys' => $keys
            );
        } else {
            throw new \Exception("Method $name not found");
        }
    }

    public function uri()
    {
        $uri = $_SERVER['REQUEST_URI'] ?? '/';
        return strtok($uri, '?');
    }

    public function requestMethod()
    {
        $method = $_SERVER['REQUEST_METHOD'];
        if ($method === 'POST' && isset($_POST['_method'])) {
            $pseudoMethod = strtoupper($_POST['_method']);
            if ($pseudoMethod === 'PUT' || $pseudoMethod === 'DELETE') {
                $method = $pseudoMethod;
            }
        }
        return $method;
    }

    public function handleStatus($statusCode, Response $res)
    {
        $callback = null;
        if (isset($this->errorHandler[$statusCode])) {
            $callback = $this->errorHandler[$statusCode];
        }

        if (is_callable($callback)) {
            $req = new Request($this);
            try {
                $callback($req, $res);
            } catch (\Exception $e) {
                $this->logger->log($e->getMessage());
            }
        }
    }
}
