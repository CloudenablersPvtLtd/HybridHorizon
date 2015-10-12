/* Additional JavaScript for cnext. */

$(document).on('change','.workflow #id_cnext_images_id', function()
		{
                /*Function to Filter Provider list, based on selected image filter
                 *  First all providers are listed down in dropdown box
                 *  On change of cnext images, we will get provider of that image.
                 *  In dropdown box except that providers will be hided
                */
	            emptyFlavor();
                //$("#id_provider_list").children().css('display','none');
                $("#id_provider_list").closest(".control-group").hide();
                $("#id_provider_list").val([]);
                
                //hiding cpu,ram,localstorage dropdown if it is shown.
                $("#id_cpu_list").closest(".control-group").hide();
                $("#id_ram_list").closest(".control-group").hide();
                $("#id_localstorage_list").closest(".control-group").hide();
                
                image_provider = $('#id_cnext_images_id option:selected').attr("data-provider");
                image_region = $('#id_cnext_images_id option:selected').attr("data-region");
                $("#id_provider_list").closest(".control-group").show();
                $("#id_provider_list").children().hide();
                $("#id_provider_list").children('option[data-provider="'+ image_provider+'"][data-region="'+image_region+'"]').css('display','block');
                flav_imagecost = $('#id_cnext_images_id option:selected').attr("data-cost");
                $('#flavor_image_cost').text(flav_imagecost);
		}
);
/*
[data-ram="'+ ram+'"]
[data-cpucount="'+ cpuCount+'"]
[data-localstorage="'+ localStorage+'"]
*/


/*
$(document).on('change','.workflow #id_cnext_images_id', function()
		{
                data_provider = $('#id_cnext_images_id option:selected').attr("data-provider");
                region = $('#id_cnext_images_id option:selected').attr("data-region");
                cpuCount = $('#id_cnext_images_id option:selected').attr("data-cpucount");
                ram = $('#id_cnext_images_id option:selected').attr("data-ram");
                localStorage = $('#id_cnext_images_id option:selected').attr("data-localstorage");
                $("#id_provider_list").closest(".control-group").show();
                $("#id_provider_list").children().hide();
                $('#id_provider_list').children('option[data-provider="'+ data_provider+'"][data-region="'+region+'"][data-cpucount="'+ cpuCount+'"][data-ram="'+ ram+'"]').css('display','block');
		}
);
*/

/*

$(document).on('change','.workflow #id_provider_list', function()
                
		{
                //$('#id_cpu_list').children().css('display','none');
                $("#id_cpu_list").closest(".control-group").hide();
                $("#id_cpu_list").val([]);
                //$('#id_ram_list').children().css('display','none');
                $("#id_ram_list").closest(".control-group").hide();
                $("#id_ram_list").val([]);                
                //$('#id_localstorage_list').children().css('display','none');
                $("#id_localstorage_list").closest(".control-group").hide();
                $("#id_localstorage_list").val([]);
	        if( $('#id_provider_list option:selected').attr("value").split("/").slice(-1)[0] == "configurable")
	        	{
				$("#id_cpu_list").closest(".control-group").show();
//                                cpu_count = $("#id_provider_list option:selected").attr("data-cpucount").split("-");
//                                for(var c=cpu_count[0]; c<=cpu_count[1]; c++){
//                                $("#id_cpu_list").append($("<option/>", {value: c,text: c}));
//                                }
                                ram = $("#id_provider_list option:selected").attr("data-ram").split("-");
                                for(var c=ram[0]; c<=ram[1]; c++){
                                $("#id_ram_list").append($("<option/>", {value: c,text: c}));
                                }
                                local_storage = $("#id_provider_list option:selected").attr("data-localstorage").split(",");
                                count = $("#id_provider_list option:selected").attr("data-localstorage").split(",").length;
                                for(var i=0;i<count; i++){
                                $("#id_localstorage_list").append($("<option/>", {value:local_storage[i], text:local_storage[i]}));
                                }
                                $('#id_cpu_list').children().css('display','block');
                                $("#id_ram_list").closest(".control-group").show();
                                $('#id_ram_list').children().css('display','block');
                                $("#id_localstorage_list").closest(".control-group").show();
                                $('#id_localstorage_list').children().css('display','block');
	        	  
	        	}
		}
);*/



$(document).on('change','.workflow #id_provider_list', function()
        
		{
	            
                //$('#id_cpu_list').children().css('display','none');
                $("#id_cpu_list").closest(".control-group").hide();
                $("#id_cpu_list").val([]);
                //$('#id_ram_list').children().css('display','none');
                $("#id_ram_list").closest(".control-group").hide();
                $("#id_ram_list").val([]);                
                //$('#id_localstorage_list').children().css('display','none');
                $("#id_localstorage_list").closest(".control-group").hide();
                $("#id_localstorage_list").val([]);
                
                $("#id_keypair").children().show();
                
	        if( $('#id_provider_list option:selected').attr("value").split("/").slice(-1)[0] == "configurable")
	        	{
	        	    emptyFlavor();
	        	    inst_provider = $('#id_provider_list option:selected').attr("data-provider");
	                inst_region = $('#id_provider_list option:selected').attr("data-region");
	                $("#id_cpu_list").closest(".control-group").show();
	                $("#id_cpu_list").children().hide();
	                $("#id_cpu_list").children('option[data-provider="'+ inst_provider+'"][data-region="'+inst_region+'"]').css('display','block');
	                $("#id_ram_list").closest(".control-group").show();
	                $("#id_ram_list").children().hide();
	                $("#id_ram_list").children('option[data-provider="'+ inst_provider+'"][data-region="'+inst_region+'"]').css('display','block');
                    $("#id_localstorage_list").closest(".control-group").show();
	                $("#id_localstorage_list").children().hide();
	                $("#id_localstorage_list").children('option[data-provider="'+ inst_provider+'"][data-region="'+inst_region+'"]').css('display','block');
			
	        	}

                 else{
                	 updateFlavor();
	        }
		}
);


function emptyFlavor()
{

                $('#flavor_vcpus').text("");
	        	$('#flavor_name').text("");
	        	$('#flavor_ram').text("");
	        	$('#flavor_disk_total').text("");
                $('#flavor_disk').text("");
                $('#flavor_ephemeral').text("");
                $('#flavor_vm_cost').text("");
                $('#flavor_total_cost').text("");
}

function keypairFilter()
		{
				key_provider = $('#id_region option:selected').attr("data-provider").toLowerCase();
				key_region = $('#id_region option:selected').attr("data-name").toLowerCase();
				$("#id_keypair").val([]);
				$("#id_keypair").closest(".control-group").show();
               		        $("#id_keypair").children().hide();
                                $("#id_keypair").children('option[data-provider="'+ key_provider+'"][data-region="'+key_region+'"]').css('display','block');
                
		}

function updateFlavor()
{
        flav_name = $('#id_provider_list option:selected').text().split("(")[0];
        if ((flav_name == "Select Instance Type") || (flav_name == "") )
         {
             return false;
            } 
	flav_local_storage = $('#id_provider_list option:selected').attr("data-localstorage");
	flav_ram = $('#id_provider_list option:selected').attr("data-ram");
	flav_cpucount = $('#id_provider_list option:selected').attr("data-cpucount");
	flav_vmcost = $('#id_provider_list option:selected').attr("data-cost");
	$('#flavor_vcpus').text(flav_cpucount);
	$('#flavor_name').text(flav_name);
	$('#flavor_ram').text(flav_ram);
	$('#flavor_disk_total').text(flav_local_storage);
    $('#flavor_disk').text(flav_local_storage);
    $('#flavor_ephemeral').text("0");	
    $('#flavor_vm_cost').text(flav_vmcost);
    flav_total = parseFloat($('#id_cnext_images_id option:selected').attr("data-cost").split(" ")[0]) +parseFloat($('#id_provider_list option:selected').attr("data-cost").split(" ")[0]);
    suffix = "USD"
    $('#flavor_total_cost').text(flav_total+suffix);
}


//Provider and region filtering operation

$(document).on('change','.workflow #id_provider', function()
		{
	        
	        $('#flavor_image_cost').text("");
	        emptyFlavor();
	        $("#id_keypair").children().show();
	        if($("#id_provider").children().length != 1){
				$("#id_cnext_images_id").closest(".control-group").hide();
				$("#id_cnext_images_id").val([]);
				$("#id_region").closest(".control-group").hide();
				$("#id_region").val([]);
                                //$("#id_keypair").closest(".control-group").hide();
				$("#id_keypair").val([]);
				$("#id_provider_list").closest(".control-group").hide();
				$("#id_provider_list").val([]);
				$("#id_cpu_list").closest(".control-group").hide();
	            $("#id_cpu_list").val([]);
	                //$('#id_ram_list').children().css('display','none');
	            $("#id_ram_list").closest(".control-group").hide();
	            $("#id_ram_list").val([]);                
	                //$('#id_localstorage_list').children().css('display','none');
	            $("#id_localstorage_list").closest(".control-group").hide();
	            $("#id_localstorage_list").val([]);
	            
				insta_provider = $('#id_provider option:selected').attr("data-provider");
				if (insta_provider != undefined)
					{
					insta_provider = insta_provider.toLowerCase();
					}
				$("#id_region").closest(".control-group").show();
                $("#id_region").children().hide();
                $("#id_region").children('option[data-provider="'+ insta_provider+'"]').css('display','block');
	        }
	       
	        else{
	            $("#id_cpu_list").closest(".control-group").hide();
	            $("#id_cpu_list").val([]);
	                //$('#id_ram_list').children().css('display','none');
	            $("#id_ram_list").closest(".control-group").hide();
	            $("#id_ram_list").val([]);                
	                //$('#id_localstorage_list').children().css('display','none');
	            $("#id_localstorage_list").closest(".control-group").hide();
	            $("#id_localstorage_list").val([]);
                    $("#id_keypair").val([]);
	          
	            flav_imagecost = $('#id_cnext_images_id option:selected').attr("data-cost");
                $('#flavor_image_cost').text(flav_imagecost);

	        }
                
		}
);
$(document).on('change','.workflow #id_region', function()
		{
	 			$('#flavor_image_cost').text("");	
	 			emptyFlavor();
	 			$("#id_cnext_images_id").closest(".control-group").hide();
	 			$("#id_cnext_images_id").val([]);
	 			$("#id_provider_list").closest(".control-group").hide();
	 			$("#id_provider_list").val([]);
				reg_provider = $('#id_region option:selected').attr("data-provider").toLowerCase();
				reg_region = $('#id_region option:selected').attr("data-name").toLowerCase();
				$("#id_cnext_images_id").closest(".control-group").show();
                $("#id_cnext_images_id").children().hide();
                $("#id_cnext_images_id").children('option[data-provider="'+ reg_provider+'"][data-region="'+reg_region+'"]').css('display','block');
                keypairFilter();
                
		}
);


$('.workflow #id_provider').change();
horizon.modals.addModalInitFunction(function (modal) {
  $(modal).find("#id_provider").change();
});


$(document).on('change','#id_key_provider_list', function()
		{
				inskey_provider = $('#id_key_provider_list option:selected').val();
				$("#id_key_region_list").val([]);
                $("#id_key_region_list").children().hide();
                $("#id_key_region_list").children('option[data-provider="'+ inskey_provider+'"]').css('display','block');
                
                
		}
);

$(document).on('click', 'input[type=submit][value=Launch]', function(){
	key_selected = $('#id_keypair option:selected').attr("data-provider");
	
	sel_provider = $('#id_provider option:selected').attr("data-provider");
	provider_list = ["HPCloud", "GreenQloud", "CloudA", "eNoCloud"]
	
	if( (provider_list.indexOf(sel_provider) > -1) && (! key_selected))
		{   
		    alert("This provider requires keypair. \n Please select keypair in access and security tab");
			return false;
		}
	else{
		if(key_selected.toLowerCase() == sel_provider.toLowerCase())
			{
		return true;
			}
		else{
			alert("Please Select relevant keyapir for selected provider and region");
		}
	}
});


$(document).on('click', '.main_nav', function(){
    //$("body").fadeOut();
    //$("html").html("<img id='cloud-anim' src='/static/dashboard/img/cloud_anim2.gif'/>");
	$('body').append('<div class="modal-backdrop" style="opacity:0.8px;">'+
			'</div><div class="modal loadingss" style="height:100px;">' +
			'<div class="spinner"/>'+
			'<img id="cloud-anim" src="/static/dashboard/img/cloud_anim2.gif">'+
			'<p style="text-align:center">Loading</p></div>');
  });


$(document).on('click', '.sidebar .nav.nav-tabs', function(){
	$('body').append('<div class="modal-backdrop" style="opacity:0.8px;">'+
			'</div><div class="modal loadingss" style="height:100px;">' +
			'<div class="spinner"/>'+
			'<div id="cloud-anim"/>'+
			'<p style="text-align:center">Loading</p></div>');
  });