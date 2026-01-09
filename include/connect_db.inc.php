<?PHP
//session_start();
require_once 'class_crud.inc.php';  

class Database
{
    private $dbName_eser = 'db_pallet_detector';
        
    ##localhost 
    private $dbServer = 'localhost';  private $dbUser = 'root'; private $dbPassword = '1234'; private $port='3306'; private $dbName = 'db_pallet_detector' ;

    ##server
    //private $dbServer = 'jaiangelbot.cc.pcs-plp.com'; private $dbUser = 'itpcs'; private $dbPassword = 'Pcs@1234'; private $port='3306'; private $dbName = 'jaibot'; //ON SERVER;
    
    protected $conn; //protected public
    public function __construct()
    {
        try {
            $dsn = "mysql:host={$this->dbServer}; port={$this->port}; dbname={$this->dbName}; charset=utf8";
            $options = array(PDO::ATTR_PERSISTENT, PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->conn = new PDO($dsn, $this->dbUser, $this->dbPassword, $options);
            //echo "<br />Connection Complete: ";
        } catch (PDOException $e) {
            echo "Connection Error: " . $e->getMessage();
        }
    }
}

?>    
