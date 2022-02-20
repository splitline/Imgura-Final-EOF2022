<?php

// Content of the waf can be modified by the owner.
$waf = file_get_contents('/etc/waf.php');

(function () use ($waf) {
    if (!$waf) return;

    try {
        token_get_all($waf, TOKEN_PARSE);
    } catch (\Exception $e) {
        // waf is not valid
        return;
    }
    header('X-Super-Waf: 1');
    include_once '/etc/waf.php';
})();
