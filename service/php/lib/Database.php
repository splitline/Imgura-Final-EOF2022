<?php

namespace Imgura\Core;

use \PDO;

class Database
{
    private $pdo;

    public function __construct($host, $dbname, $user, $pass)
    {
        $this->pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
        $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    public function quote($value)
    {
        return $this->pdo->quote($value);
    }

    public function select($table, $rows = '*', $where = [], $all = false)
    {
        $rows = is_array($rows) ? implode(',', $rows) : $rows;
        $sql = "SELECT $rows FROM $table";
        if (!empty($where)) {
            $sql .= ' WHERE ';
            if (is_array($where)) {
                $sql .= implode(' AND ', array_map(function ($key, $value) {
                    $value = $this->quote($value);
                    return "$key = $value";
                }, array_keys($where), array_values($where)));
            } else {
                $sql .= $where;
            }
        }
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        if ($all) {
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        } else {
            return $stmt->fetch(PDO::FETCH_ASSOC);
        }
    }

    public function insert($table, $data)
    {
        $keys = array_keys($data);
        $values = array_values($data);
        $sql = "INSERT INTO $table (" . implode(', ', $keys) . ") VALUES ('" . implode("', '", $values) . "')";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $this->pdo->lastInsertId();
    }

    public function update($table, $data, $where = [])
    {
        $sql = "UPDATE $table SET ";
        $sets = array();
        foreach ($data as $key => $value) {
            $sets[] = "$key = '$value'";
        }
        $sql .= implode(', ', $sets);
        if (!empty($where)) {
            $sql .= ' WHERE ';
            if (is_array($where)) {
                $sql .= implode(' AND ', array_map(function ($key, $value) {
                    $value = $this->quote($value);
                    return "$key = $value";
                }, array_keys($where), array_values($where)));
            } else {
                $sql .= $where;
            }
        }

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->rowCount();
    }

    public function delete($table, $where)
    {
        $sql = "DELETE FROM $table WHERE $where";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->rowCount();
    }

    public function query($sql)
    {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function queryOne($sql)
    {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}
