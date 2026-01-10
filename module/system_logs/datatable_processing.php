<?PHP
session_start();
require_once '../../include/class_crud.inc.php';
require_once '../../include/function.inc.php';
$obj = new CRUD();

/*
/*$_POST['length'] คือ จำนวนต่อหน้า
$_POST["draw"] คือ ??? ประมาณว่าเลขหน้า
$_POST["search"]["value"]
$_POST['order']['0']['column'] คือ เสริทข้อมูลโดยใช้ลำดับคอลัมน์ในตารางดาต้าเบส
$_POST['order']['0']['dir'] คือ ASC DESC
$_POST['start']
$_POST['length']
*/

/* table tb_system_logs
id_log
log_level (INFO, WARNING, ERROR)
message
created_at
*/


$_POST['order']['0']['column'] = $_POST['order']['0']['column']+1;

$search = $_POST["search"]["value"];
$query_search = "";
if(!empty($search[0])){
    $query_search = " WHERE (message LIKE '%".$search."%' OR message LIKE '%".$search."%' )";
}

$search_bycol = '';
if(isset($_POST['slt_value_colname_3']) && $_POST['slt_value_colname_3']!=NULL){
    $search_bycol = ($query_search!=NULL ? " AND (log_level=".$_POST['slt_value_colname_3'].")" : " WHERE log_level='".$_POST['slt_value_colname_3']."' ") ;
}

if($_POST["start"]==0){
    $length=$_POST['length'];
}else{
    $length=$_POST['length'];
}
$start = ($_POST["start"]-1)*$_POST['length'];

empty($_POST['order']['0']['column']) ? $_POST['order']['0']['column']=0 : $_POST['order']['0']['column'];
//empty($_POST['order']['0']['dir']) ? $_POST['order']['0']['dir']='desc' : $_POST['order']['0']['dir']='';

$colunm_sort = array( //ใช้เรียงข้อมูล
    0=> "tb_system_logs.id_log",
    1=> "tb_system_logs.id_log",
    2=> "tb_system_logs.log_level",
    3=> "tb_system_logs.message",
    4=> "tb_system_logs.created_at",
);

$orderBY = $colunm_sort[$_POST['order']['0']['column']];

$arrData = array();	
$numRow = $obj->getCount("SELECT count(id_log) AS total_row FROM tb_system_logs ".$query_search.$search_bycol."");    //ถ้าจำนวน Row ทั้งหมด
$fetchRow = $obj->fetchRows("SELECT * FROM tb_system_logs ".$query_search.$search_bycol." ORDER BY ".$orderBY." ".$_POST['order']['0']['dir']." LIMIT ".$_POST['start'].", ".$length." ");

if (count($fetchRow)>0) {
    $No = ($numRow-$_POST['start']);
    foreach($fetchRow as $key=>$value){
        $dataRow = array();
        $dataRow[] = $No.'.';
        switch ($fetchRow[$key]['log_level']) {
            case 'INFO':
                $log_level_text = '<span class="badge badge-info">INFO</span>';
                break;
            case 'WARNING':
                $log_level_text = '<span class="badge badge-warning">WARNING</span>';
                break;
            case 'ERROR':
                $log_level_text = '<span class="badge badge-danger">ERROR</span>';
                break;            
            default:
                $log_level_text = '<span class="badge badge-secondary">-</span>';
                break;
        }
        $dataRow[] = ($fetchRow[$key]['log_level']=='' ? '-' : $log_level_text);
        $dataRow[] = ($fetchRow[$key]['created_at']=='' ? '-' : $fetchRow[$key]['created_at']);

        if (mb_strlen($fetchRow[$key]['message'], 'UTF-8') > 100) {
            // ตัดเหลือ 65 ตัวอักษร พร้อมตามด้วย "..."
            //$question_text = mb_substr($fetchRow[$key]['question'], 0, 65, 'UTF-8') . "...";
            $message_text = '<span class="show-detail" data-reply-id="'.$fetchRow[$key]['id_log'].':|:'.str_replace(' ', '', $fetchRow[$key]['created_at']).'" data-title="<strong>By: </strong>'.htmlspecialchars($value['created_at']).' <strong>at time:</strong> '.$fetchRow[$key]['created_at'].'" data-full="'.htmlspecialchars(str_replace(array("\r\n", "\n", "\r"), '<br />', $fetchRow[$key]['message']), ENT_QUOTES, 'UTF-8').'">'.mb_substr($fetchRow[$key]['message'], 0, 200, 'UTF-8').'...</span>';
        }else{
            $message_text = '<span class="show-detail" data-reply-id="'.$fetchRow[$key]['id_log'].':|:'.str_replace(' ', '', $fetchRow[$key]['created_at']).'" data-title="<strong>By: </strong>'.htmlspecialchars($value['created_at']).' <strong>at time:</strong> '.$fetchRow[$key]['created_at'].'" data-full="'.htmlspecialchars(str_replace(array("\r\n", "\n", "\r"), '<br />', $fetchRow[$key]['message']), ENT_QUOTES, 'UTF-8').'">'.mb_substr($fetchRow[$key]['message'], 0, 200, 'UTF-8').'</span>';
        }
        $dataRow[] = $message_text;
        //$dataRow[] = ($fetchRow[$key]['message']=='' ? '-' : $fetchRow[$key]['message'].' : id_log= '.$fetchRow[$key]['id_log']);
        $arrData[] = $dataRow;
        $No--;
    }
} else {
    $arrData = null;
}

$output = array(
    "draw"				=>	intval($_POST["draw"]),
    "recordsTotal"  	=>  intval($numRow),
    "recordsFiltered" 	=> 	intval($numRow),
    "data"    			=> 	$arrData
);
echo json_encode($output);
exit();

/*------------------------------------------------------------------*/
/*------------------------------------------------------------------*/
?>