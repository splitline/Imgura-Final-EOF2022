<?php

namespace Imgura\Core;

class Response
{
    private $app = null;

    public $status = null;

    protected $headers = array();
    protected $cookies = array();
    // public $session = null;
    protected $body = '';

    public function __construct(App &$app)
    {
        ob_start();
        $this->app = $app;
    }

    public function __destruct()
    {
        if ($this->status !== null) {
            $this->status($this->status);
        }

        // send headers
        foreach ($this->headers as $name => $value) {
            if (is_int($name)) { // status message
                header($value);
            } else {
                header("$name: $value");
            }
        }

        // send cookies
        foreach ($this->cookies as $c) {
            setcookie(
                $c['name'],
                $c['value'],
                $c['expire'],
                $c['path'],
                $c['domain'],
                $c['secure'],
                $c['http_only']
            );
        }
        echo $this->body;
        if (ob_get_length())
            echo ob_get_clean();
    }


    public function output($text)
    {
        $this->body = $text;
    }

    public function json($data)
    {
        $this->headers['Content-Type'] = 'application/json';
        $this->output(json_encode($data));
    }


    public function render($template, $context = [])
    {

        try {
            $html = $this->app->renderer->render($template, $context);
        } catch (\Twig\Error\LoaderError $e) {
            $html = $this->app->renderer->createTemplate($template)->render($context);
        }

        $this->output($html);
    }

    public function redirect($url, $statusCode = 302, $isSecure = false)
    {
        if (substr($url, 0, 1) === '/') {
            $httpHost = $_SERVER['HTTP_HOST'];
            $url = ($isSecure ? 'https://' : 'http://') . $httpHost . $url;
        }
        while (ob_get_level() > 0) {
            ob_end_clean();
        }
        $this->status($statusCode);
        $this->header('Location', $url);
        $this->render('<html><head><meta http-equiv="refresh" content="0;url=' . $url . '"></head></html>');
    }

    public function contentType($type, $charset = null)
    {
        if (!is_null($charset)) {
            $type .= '; charset=' . $charset;
        }
        $this->header('Content-Type', $type);
    }

    public function status($code)
    {
        static $messages = array(
            // Informational 1xx
            100 => 'Continue',
            101 => 'Switching Protocols',
            // Success 2xx
            200 => 'OK',
            201 => 'Created',
            202 => 'Accepted',
            203 => 'Non-Authoritative Information',
            204 => 'No Content',
            205 => 'Reset Content',
            206 => 'Partial Content',
            // Redirection 3xx
            300 => 'Multiple Choices',
            301 => 'Moved Permanently',
            302 => 'Found',
            303 => 'See Other',
            304 => 'Not Modified',
            305 => 'Use Proxy',
            307 => 'Temporary Redirect',
            // Client Error 4xx
            400 => 'Bad Request',
            401 => 'Unauthorized',
            402 => 'Payment Required',
            403 => 'Forbidden',
            404 => 'Not Found',
            405 => 'Method Not Allowed',
            406 => 'Not Acceptable',
            407 => 'Proxy Authentication Required',
            408 => 'Request Timeout',
            409 => 'Conflict',
            410 => 'Gone',
            411 => 'Length Required',
            412 => 'Precondition Failed',
            413 => 'Request Entity Too Large',
            414 => 'Request-URI Too Long',
            415 => 'Unsupported Media Type',
            416 => 'Requested Range Not Satisfiable',
            417 => 'Expectation Failed',
            // Server Error 5xx
            500 => 'Internal Server Error',
            501 => 'Not Implemented',
            502 => 'Bad Gateway',
            503 => 'Service Unavailable',
            504 => 'Gateway Timeout',
            505 => 'HTTP Version Not Supported',
            509 => 'Bandwidth Limit Exceeded'
        );
        if (isset($messages[$code])) {
            $message = $messages[$code];
            $this->header("HTTP/1.1 $code $message");
        }
        if ($code == 404 || $code >= 500) {
            $this->app->handleStatus($code, $this);
        }
    }

    public function header($name, $value = null)
    {
        if (is_null($value)) {
            $this->headers[] = $name;
        } else {
            $this->headers[$name] = $value;
        }
    }

    public function cookie(
        $name,
        $value,
        $expire = null,
        $path = '/',
        $domain = '',
        $secure = false,
        $httpOnly = false
    ) {
        $this->cookies[] = array(
            'name'      => $name,
            'value'     => $value,
            'expire'    => $expire,
            'path'      => $path,
            'domain'    => $domain,
            'secure'    => $secure ? true : false,
            'http_only' => $httpOnly
        );
    }

    public function sendFile($path, $download=false)
    {
        $this->header('Content-Type', mime_content_type($path));
        $this->header('Content-Length', filesize($path));
        if ($download) {
            $this->header('Content-Disposition', 'attachment; filename="' . basename($path) . '"');
        }
        readfile($path);
    }

    public function __toString()
    {
        return $this->body;
    }
}
