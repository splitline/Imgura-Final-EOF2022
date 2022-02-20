<?php

namespace Imgura\Core;

class Request
{
    public $method;
    public $path;
    public $headers;
    public $cookies;
    public $session;

    public $query;
    public $form;
    public $params;
    public $files;
    public $args;

    private $body;


    public function __construct(App &$app, array $args = [])
    {
        $this->method = $_SERVER['REQUEST_METHOD'];
        $this->path = $app->uri();
        $this->headers = getallheaders();
        $this->session = $app->session;

        $this->query = &$_GET;
        $this->form = &$_POST;
        $this->params = &$_REQUEST;
        $this->files = &$_FILES;
        $this->args = &$args;
        $this->cookies = &$_COOKIE;

        $this->body = file_get_contents('php://input');
    }

    public function __set($name, $value)
    {
        $this->params[$name] = $value;
    }

    public function __get($name)
    {
        return $this->param($name);
    }

    public function __isset($name)
    {
        return isset($this->params[$name]);
    }

    public function ip()
    {
        return $_SERVER['HTTP_CLIENT_IP'] ?? $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? null;
    }

    public function body($raw = false)
    {
        if (!isset($this->headers['Content-Type']) || $raw)
            return $this->body;

        $content_type = $this->headers['Content-Type'];

        if ($content_type === 'application/json') {
            return json_decode($this->body, true);
        } elseif ($content_type === 'application/x-www-form-urlencoded') {
            parse_str($this->body, $data);
            return $data;
        } elseif ($content_type === 'application/xml') {
            return simplexml_load_string($this->body, 'SimpleXMLElement', LIBXML_NOENT);
        } else {
            return $this->body;
        }
    }

    public function param($name, $multiple = false)
    {
        if (isset($this->params[$name])) {
            if ($multiple === is_array($this->params[$name])) {
                return $this->params[$name];
            }
        }
        return null;
    }

    public function arg($key)
    {
        if (isset($this->args[$key])) {
            return $this->args[$key];
        }
        return null;
    }

    public function cookie($name)
    {
        if (isset($this->cookies[$name])) {
            return $this->cookies[$name];
        }
        return null;
    }

    public function __toString()
    {
        return  $this->method . ' ' . $this->path;
    }
}
