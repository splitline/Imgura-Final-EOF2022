<?php
namespace Imgura\Core;

class Session
{
    public const COOKIE_MAX_LENGTH = 4096;
    protected $secret;
    protected $values = array();
    protected $dirty = false;
    protected $started = false;
    protected $cookieName = 'session';

    public function __construct($secret)
    {
        $this->started = true;
        $this->secret = $secret;
        
        $this->restore();
    }

    public function __set($name, $value)
    {
        $this->dirty = true;
        $this->values[$name] = $value;
    }

    public function __get($name)
    {
        if (isset($this->values[$name])) {
            return $this->values[$name];
        }
        return null;
    }

    public function __isset($name)
    {
        return isset($this->values[$name]);
    }

    public function __unset($name)
    {
        if (isset($this->values[$name])) {
            $this->dirty = true;
            unset($this->values[$name]);
        }
    }

    public function restore() {
        if (isset($_COOKIE[$this->cookieName])) {
            $cookie = $_COOKIE[$this->cookieName];
            $parts = explode('.', $cookie);
            if (count($parts) === 2) {
                $hash = $parts[0];
                $data = unserialize(base64_decode($parts[1]));

                if ($this->verify($hash, $data)) {
                    $this->values = $data;
                }
            }
        }
    }

    public function save() {
        if ($this->dirty) {
            $data = $this->values;
            $hash = $this->hash($data);
            $cookie = $hash . '.' . base64_encode(serialize($data));
            if (strlen($cookie) > self::COOKIE_MAX_LENGTH) {
                throw new \Exception('Cookie is too long');
            }
            setcookie($this->cookieName, $cookie, 0, '/');
        }
    }

    public function destroy() {
        $this->values = array();
        $this->dirty = true;
        $this->save();
    }

    protected function hash($data) {
        return hash_hmac('sha1', serialize($data), $this->secret);
    }

    public function verify($data, $hash) {
        $hash = $this->hash($data);
        return hash_equals($hash, $hash);
    }
}
