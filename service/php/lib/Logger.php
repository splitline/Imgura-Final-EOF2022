<?php

namespace Imgura\Core;

class Logger
{
    private $log_file;
    private $logs = [];

    public function __construct($log_file = './logs/app.log')
    {
        $this->log_file = $log_file;
    }

    public function log($message)
    {
        $this->logs[] = sprintf("[%s] %s\n", date('Y-m-d H:i:s'), $message);
    }

    public function write()
    {
        file_put_contents($this->log_file, implode("\n", $this->logs), FILE_APPEND);
    }

    public function clear()
    {
        $this->logs = [];
    }

    public function __destruct()
    {
        $this->write();
    }
}
