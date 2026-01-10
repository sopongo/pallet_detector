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


/* table tb_pallet

tb_image.id_img
tb_image.image_name
id_pallet
ref_id_img
pallet_name
accuracy
pallet_date_in
first_detected_at
last_detected_at
is_active
in_over
status
over_time
detector_count
notify_count
*/


$_POST['order']['0']['column'] = $_POST['order']['0']['column']+1;

$search = $_POST["search"]["value"];
$query_search = "";
if(!empty($search[0])){
    $query_search = " WHERE (pallet_name LIKE '%".$search."%' OR pallet_name LIKE '%".$search."%' )";
}

$search_bycol = '';
if(isset($_POST['slt_value_colname_3']) && $_POST['slt_value_colname_3']!=NULL){
    $search_bycol = ($query_search!=NULL ? " AND (status=".$_POST['slt_value_colname_3'].")" : " WHERE status='".$_POST['slt_value_colname_3']."' ") ;
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
    0=> "tb_pallet.id_pallet",
    1=> "tb_pallet.id_pallet",
    2=> "tb_pallet.log_level",
    3=> "tb_pallet.message",
    4=> "tb_pallet.created_at",
);

$orderBY = $colunm_sort[$_POST['order']['0']['column']];

$arrData = array();	
$numRow = $obj->getCount("SELECT count(id_pallet) AS total_row FROM tb_pallet ".$query_search.$search_bycol."");    //ถ้าจำนวน Row ทั้งหมด
$fetchRow = $obj->fetchRows("SELECT 
    tb_pallet.id_pallet,
    tb_pallet.ref_id_img,
    tb_pallet.pallet_name,
    tb_pallet.accuracy,
    tb_pallet.pallet_date_in,
    tb_pallet.first_detected_at,
    tb_pallet.last_detected_at,
    tb_pallet.is_active,
    tb_pallet.in_over,
    tb_pallet.over_time,
    
    -- 1. Overtime Duration: ถ้าเกินเวลาแล้ว (over_time มีค่า) ให้คำนวณส่วนต่าง
    IF(tb_pallet.over_time IS NOT NULL, 
       SEC_TO_TIME(TIMESTAMPDIFF(SECOND, tb_pallet.over_time, tb_pallet.last_detected_at)), 
       '00:00:00') AS overtime_duration,

    -- 2. Intime Duration: ถ้ายังไม่เกินเวลา (over_time เป็น NULL) ให้คำนวณเวลาที่ใช้ไปจนถึงปัจจุบัน
    IF(tb_pallet.over_time IS NULL AND tb_pallet.is_active = 0, 
       SEC_TO_TIME(TIMESTAMPDIFF(SECOND, tb_pallet.pallet_date_in, tb_pallet.last_detected_at)), 
       '00:00:00') AS intime_duration,
    tb_pallet.detector_count,
    tb_image.id_img,
    tb_image.image_date,
    tb_image.image_name,
    tb_pallet.notify_count 
FROM tb_pallet 
LEFT JOIN tb_image ON (tb_image.id_img = tb_pallet.ref_id_img) ".$query_search.$search_bycol." ORDER BY ".$orderBY." ".$_POST['order']['0']['dir']." LIMIT ".$_POST['start'].", ".$length." ");

if (count($fetchRow)>0) {
    $No = ($numRow-$_POST['start']);
    foreach($fetchRow as $key=>$value){
        $dataRow = array();
        $dataRow[] = $No.'.';
        $fullpath_img = 'upload_image/'.(substr($fetchRow[$key]['image_date'],0,10).'/').$fetchRow[$key]['image_name'];

        !file_exists('../../'.$fullpath_img) ? $fullpath_img = '<img src="dist/img/boxed-bg.png" class="img-fluid mb-2" alt="Image" style="width:50px; height: auto;">' : $fullpath_img = '<a href="'.$fullpath_img.'" data-toggle="lightbox" data-gallery="gallery" data-title="'.$fetchRow[$key]['pallet_name'].'"><img src="'.$fullpath_img.'" class="img-fluid mb-2" alt="Image" style="width:50px; height: auto;"></a>'; //ถ้าไม่มีรูปให้ใช้โฟลเดอร์ images แทน   
        $fullpath_img = str_replace(".jpg", "_detected.jpg", $fullpath_img); 

        $dataRow[] = $fullpath_img;
        $dataRow[] = ($fetchRow[$key]['pallet_name']=='' ? '-' : $fetchRow[$key]['pallet_name']);
        $dataRow[] = ($fetchRow[$key]['accuracy']=='' ? '-' : $fetchRow[$key]['accuracy']);
        $dataRow[] = ($fetchRow[$key]['pallet_date_in']=='' ? '-' : $fetchRow[$key]['pallet_date_in']);
        $dataRow[] = ($fetchRow[$key]['last_detected_at']=='' ? '-' : $fetchRow[$key]['last_detected_at']);
        $dataRow[] = ($fetchRow[$key]['is_active'] == 1) ? 'Wait' : (($fetchRow[$key]['overtime_duration'] == '00:00:00') 
        ? '<span class="text-success">'.$fetchRow[$key]['intime_duration'].'</span>' 
        : '<span class="text-danger">'.$fetchRow[$key]['overtime_duration'].'</span>');
        $dataRow[] = ($fetchRow[$key]['notify_count']=='' ? '-' : $fetchRow[$key]['notify_count']);
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