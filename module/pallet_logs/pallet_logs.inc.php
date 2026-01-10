<!-- CSS DataTables -->
<link rel="stylesheet" href="plugins/datatables-bs4/css/dataTables.bootstrap4.min.css">
<link rel="stylesheet" href="plugins/datatables-responsive/css/responsive.bootstrap4.min.css">
<link rel="stylesheet" href="plugins/datatables-buttons/css/buttons.bootstrap4.min.css">

<style>
.dataTables_length, .form-control-sm{  font-size:0.95rem; }/* 40px/16=2.5em */
.table, .dataTable tr td{  padding:0.35rem 0.50rem;  margin:0;}
.btn-sm{ padding:0.10rem 0.40rem 0.20rem 0.40rem; margin:0.0rem 0.0rem;}
.dt-buttons button{font-size:0.85rem; /* 40px/16=2.5em */}
.dropdown-menu{  /*left:-70px;*/}
.dropdown-menu a.dropdown-item{  font-size:0.85rem; /* 40px/16=2.5em */ }
input::placeholder { font-size: 0.80rem; font-family: Sarabun;  /* 40px/16=2.5em */ }
</style>

<!-- Default box -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><i class="fas fa-file-alt"></i> System Logs</h3>
        </div>
        <div class="card-body">

        <table id="example1" class="table table-bordered table-hover dataTable dtr-inline">
          <thead>
          <tr class="bg-light">
            <th width="50" class="sorting_disabled">No</th>
            <th width="50">Photo <!--tb_image.id_img--></th>
            <th>Pallet Name<!--tb_pallet.name--></th>
            <th>Accuracy<!--tb_pallet.accuracy--></th>
            <th>Detected at<!--tb_pallet.first_detected_at--></th>
            <th>Last Detected<!--tb_pallet.last_detected_at--></th>
            <th>Duration<!--tb_pallet.duration--></th>
            <th>Total Alert<!--notify_count--></th>
          </tr>
          </thead>
          <tbody>
          </tbody>
        </table>

        </div><!-- /.card-body -->

      </div>
      <!-- /.card -->

<!-- Ekko Lightbox -->
  <link rel="stylesheet" href="plugins/ekko-lightbox/ekko-lightbox.css">
  <!-- Ekko Lightbox -->
<script src="plugins/ekko-lightbox/ekko-lightbox.min.js"></script>

<!-- Bootstrap 4 -->
<script src="plugins/bootstrap/js/bootstrap.bundle.min.js"></script>
<!-- DataTables  & Plugins -->
<script src="plugins/datatables/jquery.dataTables.js"></script>
<script src="plugins/datatables-bs4/js/dataTables.bootstrap4.min.js"></script>
<script src="plugins/datatables-responsive/js/dataTables.responsive.min.js"></script>
<script src="plugins/datatables-responsive/js/responsive.bootstrap4.min.js"></script>
<script src="plugins/datatables-buttons/js/dataTables.buttons.min.js"></script>
<script src="plugins/datatables-buttons/js/buttons.bootstrap4.min.js"></script>
<script src="plugins/jszip/jszip.min.js"></script>
<script src="plugins/pdfmake/pdfmake.min.js"></script>
<script src="plugins/pdfmake/vfs_fonts.js"></script>
<script src="plugins/datatables-buttons/js/buttons.html5.min.js"></script>
<script src="plugins/datatables-buttons/js/buttons.print.min.js"></script>
<script src="plugins/datatables-buttons/js/buttons.colVis.min.js"></script>

<script type="text/javascript"> 

  $(function () {
    $(document).on('click', '[data-toggle="lightbox"]', function(event) {
      event.preventDefault();
      $(this).ekkoLightbox({
        alwaysShowClose: true,
        backdrop: 'static' // ป้องกันปิด lightbox เมื่อคลิกพื้นที่ดำ

      });
    });

  });

  $(document).on('click', '.mf-img-ico img.lightbox-trigger', function() {
    var imgSrc = $(this).attr('src');
    $('#lightboxImage').attr('src', imgSrc);
    $('#lightboxModal').modal({
      backdrop: 'static', // ป้องกันปิดเมื่อคลิกพื้นดำ
      keyboard: true      // ปิดได้เมื่อกด esc
    });
  });

  $(document).on("change", "#slt_value_colname_3", function (event) { //change click blur แล้วแต่เลือกใช้กับ element 
    if ($('#slt_value_colname_3').val() == "") {
        swal("ผิดพลาด!", "กรุณาเลือกค่าที่ต้องการ", "error");
        return false;
    }
        setTimeout(function () {
            $('#example1').DataTable().ajax.reload();
        }, 500);
  });

    $('#example1').DataTable({
      "processing": true,
      "serverSide": true,
      "order": [0,'desc'], //ถ้าโหลดครั้งแรกจะให้เรียงตามคอลัมน์ไหนก็ใส่เลขคอลัมน์ 0,'desc'
      "aoColumnDefs": [
        { "bSortable": false, "aTargets": [0, 1, 2, 3, 4, 5, 6, 7] }, //คอลัมน์ที่จะไม่ให้ฟังก์ชั่นเรียง
        { "bSearchable": false, "aTargets": [ 0, 1, 2, 3, 4, 5, 6, 7] } //คอลัมน์ที่ต้องการไม่ให้เสริท
      ], 
      ajax: {
        beforeSend: function () {
          //จะให้ทำอะไรก่อนส่งค่าไปหรือไม่
        },
        url: 'module/pallet_logs/datatable_processing.php',
        type: 'POST',
        //data : {"action":"get"},//"slt_search":slt_search
        "data": function (data) { //##ส่งแบบที่ 2 ส่งค่าตาม event Click
            data.action = "get"
            data.slt_value_colname_3 = $('#slt_value_colname_3').val();
            //data.ใส่ค่าที่ 2 = ค่าที่ 2;
          },        
        async: false,
        cache: false,
        error: function (xhr, error, code) {
          console.log(xhr, code);
        },
      },
      "paging": true,
      "lengthChange": true, //ออฟชั่นแสดงผลต่อหน้า
      "pagingType": "simple_numbers",
      "pageLength": 100,
      "searching": true,
      "ordering": true,
      "info": true,
      "autoWidth": false,
      "responsive": true,
      //"buttons": ["csv", "excel", "pdf", "colvis"]
    //}).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');
    });

$(document).ready(function () {
    
  var table = $('#example1').DataTable();
  //var info = table.page.info();

  $('input[type=search]').attr('placeholder', 'Search...');


  $('#example1_length select').css({'width':'70px'});

  
  });

</script>