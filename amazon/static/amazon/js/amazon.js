/* Additional JavaScript for amazon. */

$(document).on('change','.workflow #id_source_types', function()
		{
          source_type = $('#id_source_types option:selected').val();
          if (source_type == "")
          {
        		  $("#id_owned_images_id").closest(".control-group").hide();
    	          $("#id_amazon_images_id").closest(".control-group").hide();
                  $('#flavor_name').text("");
                  $('#flavor_arch').text("");
                  $('#flavor_rdn').text("");
                  $('#flavor_platform').text("");
                  $('#flavor_kernelid').text("");
                  $('#flavor_state').text("");
                  $('#flavor_region').text("");
                  $('#flavor_virtualization_type').text("");
                  $('#flavor_root_device_type').text("");

          }
          else if (source_type == "owned_images_id")
          {
    		  $("#id_owned_images_id").closest(".control-group").show();
         	  $("#id_amazon_images_id").closest(".control-group").hide();
          }
		  else
		  {
			  $("#id_owned_images_id").closest(".control-group").hide();
	          $("#id_amazon_images_id").closest(".control-group").show();
	          
		  }
          
});

$('.workflow #id_source_types').change();
horizon.modals.addModalInitFunction(function (modal) {
  $(modal).find("#id_source_types").change();
});

$('.workflow #id_owned_images_id').change();
horizon.modals.addModalInitFunction(function (modal) {
  $(modal).find("#id_owned_images_id").change();
});

$('.workflow #id_amazon_images_id').change();
horizon.modals.addModalInitFunction(function (modal) {
  $(modal).find("#id_amazon_images_id").change();
});

$(document).on('change','.input #id_owned_images_id', function()
		{
		  image_id = $('#id_owned_images_id option:selected').val();
		  if (image_id == "")
			  {
			  	$("#id_instance_type").closest(".control-group").hide();
			  }
		  else
			  {
			  	$("#id_instance_type").closest(".control-group").show();
			  	$("#id_imagetype").val($('#id_owned_images_id option:selected').attr("data-architecture")+"_"+
			    		$('#id_owned_images_id option:selected').attr("data-virtualization_type")+"_"+
			    		$('#id_owned_images_id option:selected').attr("data-root_device_type"));
			  	imagetype = $('#id_imagetype').val();
				$("#id_instance_type").val([]);
                $("#id_instance_type").children().hide();
                $("#id_instance_type").children('option[data-imagetype="'+ imagetype +'"]').css('display','block');
			  }
		  $('#flavor_name').text($('#id_owned_images_id option:selected').attr("data-name"));
		  $('#flavor_arch').text($('#id_owned_images_id option:selected').attr("data-architecture"));
		  $('#flavor_rdn').text($('#id_owned_images_id option:selected').attr("data-root_device_name"));
		  $('#flavor_platform').text($('#id_owned_images_id option:selected').attr("data-platform"));
		  $('#flavor_kernelid').text($('#id_owned_images_id option:selected').attr("data-kernel_id"));
		  $('#flavor_state').text($('#id_owned_images_id option:selected').attr("data-state"));
		  $('#flavor_region').text($('#id_owned_images_id option:selected').attr("data-region"));
		  $('#flavor_virtualization_type').text($('#id_owned_images_id option:selected').attr("data-virtualization_type"));
		  $('#flavor_root_device_type').text($('#id_owned_images_id option:selected').attr("data-root_device_type"));
		}
);
$(document).on('change','.input #id_amazon_images_id', function()
		{
		  image_id = $('#id_amazon_images_id option:selected').val();
		  if (image_id == "")
			  {
			  	$("#id_instance_type").closest(".control-group").hide();
			  }
		  else
			  {
			  	$("#id_instance_type").closest(".control-group").show();
			  	$("#id_imagetype").val($('#id_amazon_images_id option:selected').attr("data-architecture")+"_"+
			    		$('#id_amazon_images_id option:selected').attr("data-virtualization_type")+"_"+
			    		$('#id_amazon_images_id option:selected').attr("data-root_device_type"));
			  	imagetype = $('#id_imagetype').val();
				$("#id_instance_type").val([]);
                $("#id_instance_type").children().hide();
                $("#id_instance_type").children('option[data-imagetype="'+ imagetype +'"]').css('display','block');
			  }
		  $('#flavor_name').text($('#id_amazon_images_id option:selected').attr("data-name"));
		  $('#flavor_arch').text($('#id_amazon_images_id option:selected').attr("data-architecture"));
		  $('#flavor_rdn').text($('#id_amazon_images_id option:selected').attr("data-root_device_name"));
		  $('#flavor_platform').text($('#id_amazon_images_id option:selected').attr("data-platform"));
		  $('#flavor_kernelid').text($('#id_amazon_images_id option:selected').attr("data-kernel_id"));
		  $('#flavor_state').text($('#id_amazon_images_id option:selected').attr("data-state"));
		  $('#flavor_region').text($('#id_amazon_images_id option:selected').attr("data-region"));
		  $('#flavor_virtualization_type').text($('#id_amazon_images_id option:selected').attr("data-virtualization_type"));
		  $('#flavor_root_device_type').text($('#id_amazon_images_id option:selected').attr("data-root_device_type"));
        }
);
//Volume type restriction and iops supported zone are restricted in below js
$(document).on('click', 'input[type=submit][value=Create]', function(){
	volume_type = $('#id_volume_type option:selected').val()
	var a = ['us-east-1a','us-east-1b'];
	if (volume_type == "io1")
		{
		if ( a.indexOf($('#id_availability_zone option:selected').val()) == -1 )
			{
				if ($('#id_iops').val() == "")
				{
				alert("Specify the IOPS Value");
			    return false;
				}
			}
		else
		{
			alert("The specified zone does not support 'io1' volume type.");
			return false;
		}
		}
});

$(document).on('change','.input #id_volume_type', function()
		{
			volume_type = $('#id_volume_type option:selected').val()
			if (volume_type == "io1")
				{
				$('#id_iops').show()
				$('label[for="id_iops"]').show();
				$('#id_size').prop('min','10');
				}
			else
				{
				$('#id_iops').hide()
				$('label[for="id_iops"]').hide();
				$('#id_size').prop('min','1');
				}
		}
);
$('.input #id_volume_type').change();
horizon.modals.addModalInitFunction(function (modal) {
  $(modal).find("#id_volume_type").change();
});

$(document).ready(function() {
	$("table").each(function () {
		var $table = $(this);
		if ($table.find('tbody tr').not('.empty').length > 10) {
			var $pager = $('<div id="pager" class="pager"></div>');
			 $('<img class="first" src="/static/dashboard/img/paging_first.png"></img>').appendTo($pager).addClass('clickable');
			 $('<img class="prev" src="/static/dashboard/img/paging_prev.png"></img>').appendTo($pager).addClass('clickable');
			 $('<input class="pagedisplay" type="text" readonly></input>').appendTo($pager)
			 $('<img class="next" src="/static/dashboard/img/paging_next.png"></img>').appendTo($pager).addClass('clickable');
			 $('<img class="last" src="/static/dashboard/img/paging_last.png"></img>').appendTo($pager).addClass('clickable');
			 $('<select class="pagesize"><option value=10 selected="selected">10</option>\
					 <option value=20>20</option>\
					 <option value=30>30</option>\
					 <option value=40>40</option>\
					 <option value=50>50</option></select>').appendTo($pager);
			 $pager.insertAfter($table);
			$table
			.tablesorter({widthFixed: true, widgets: ['zebra']})
			.tablesorterPager({container: $("#pager")});
		}
	});
});

$(document).ready(function() { 
    $("table") 
    .tablesorter({widthFixed: true, widgets: ['zebra']}) 
    .tablesorterPager({container: $("#pager")}); 
});


