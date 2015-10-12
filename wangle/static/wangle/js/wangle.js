/* Additional JavaScript for wangle. */

/*Show provider and region if platform is Cnext*/

$(document).on('change','.input #id_cloudid', function()
		{
				platform = $('#id_cloudid option:selected').attr("data-platform");
				if (platform == "Cnext")
					{
					$(".input #id_provider").closest(".control-group").show();
					$(".input #id_region").closest(".control-group").show();
					$(".input #id_providers").closest(".control-group").show();
					$(".input #id_regions").closest(".control-group").show();
					}
				else
					{
					$(".input #id_provider").closest(".control-group").hide();
					$(".input #id_region").closest(".control-group").hide();
					$(".input #id_providers").closest(".control-group").hide();
					$(".input #id_regions").closest(".control-group").hide();					
					}
					
		}
);

$(document).on('change','.input #id_cloudids', function()
		{
				platform = $('#id_cloudids option:selected').attr("data-platform");
				if (platform == "Cnext")
					{
					$(".input #id_provider").closest(".control-group").show();
					$(".input #id_region").closest(".control-group").show();
					$(".input #id_providers").closest(".control-group").show();
					$(".input #id_regions").closest(".control-group").show();
					}
				else
					{
					$(".input #id_provider").closest(".control-group").hide();
					$(".input #id_region").closest(".control-group").hide();
					$(".input #id_providers").closest(".control-group").hide();
					$(".input #id_regions").closest(".control-group").hide();					
					}
					
		}
);

/*Js for region filtering according to provider selection */

$(document).on('change','.input #id_provider', function()
		{
			insta_provider = $('#id_provider option:selected').attr("data-provider").toLowerCase();
			$("#id_region").closest(".control-group").hide();
			$("#id_region").val([]);
			$(".input #id_region").closest(".control-group").show();
            $(".input #id_region").children().hide();
            $(".input #id_region").children('option[data-provider="'+ insta_provider+'"]').css('display','block');
		}
);

/*Js for region filtering according to provider selection */

$(document).on('change','.input #id_providers', function()
		{
			insta_provider = $('#id_providers option:selected').attr("data-provider").toLowerCase();
			$("#id_regions").closest(".control-group").hide();
			$("#id_regions").val([]);
			$(".input #id_regions").closest(".control-group").show();
            $(".input #id_regions").children().hide();
            $(".input #id_regions").children('option[data-provider="'+ insta_provider+'"]').css('display','block');
		}
);

/* show checkbox selected on selecting the cloud */

$(document).on('change','.input #id_cloudids', function(){
	if ($('#.input #id_cloudids option:selected').text() == "Select Cloud")
		{
		$("#id_regions").closest(".control-group").hide();
		$("#id_providers").closest(".control-group").hide();
		}

	else if ($('#.input #id_cloudids option:selected').attr("data-platform") != "Cnext")
		{
			$("#id_regions").closest(".control-group").hide();
			$("#id_providers").closest(".control-group").hide();
			a  = $('#.input #id_cloudids option:selected').attr("data-allowed")		
			b = $('.input li').each(function(i, li) {
		      var $product = $(li);  
			});
			b.show()
	        console.log(a)
	        a1 =  a.replace(/[^a-zA-Z0-9]/g, " ");
	        console.log(a1)
	        b = $('.input li').each(function(i, li) {
	                  var $product = $(li);  
	                });
	        console.log(b)
	        console.log(b.length)
	        for (i = 0;i<b.length;i++)
	                {
	                        var z = '#id_allowed_' + i;
	                        console.log(z)
	                        console.log(a1.indexOf(b[i].textContent) > 0)
	                        console.log(b[i].textContent)
	                        if(a1.indexOf(b[i].textContent) > 0)
	                        {
	                                $(z).prop('checked', true);                
	                        }
	                        else
	                        {
	                                $(z).prop('checked', false);      
	                        }
	                }
		}
	else
	{
		b = $('.input li').each(function(i, li) {
		      var $product = $(li);  
			});
			b.hide()
		$("#id_regions").closest(".control-group").show();
		$("#id_providers").closest(".control-group").show();
	}
			
});


/* show the selected checkbox depend on the region selection */

$(document).on('change','.input #id_regions', function(){
	if ($('#.input #id_regions option:selected').text() == "Select Region")
		{
			b = $('.input li').each(function(i, li) {
		      var $product = $(li);  
			});
			b.hide()
		}
	else
	{
			a  = $('#.input #id_regions option:selected').attr("data-allowed")		
			b = $('.input li').each(function(i, li) {
		      var $product = $(li);  
			});
			b.show()
	        console.log(a)
	        a1 =  a.replace(/[^a-zA-Z0-9]/g, " ");
	        console.log(a1)
	        b = $('.input li').each(function(i, li) {
	                  var $product = $(li);  
	                });
	        console.log(b)
	        console.log(b.length)
	        for (i = 0;i<b.length;i++)
	                {
	                        var z = '#id_allowed_' + i;
	                        console.log(z)
	                        console.log(a1.indexOf(b[i].textContent) > 0)
	                        console.log(b[i].textContent)
	                        if(a1.indexOf(b[i].textContent) > 0)
	                        {
	                                $(z).prop('checked', true);                
	                        }
	                        else
	                        {
	                                $(z).prop('checked', false);      
	                        }
	                }
	}
});


/* show the selected access on selecting the role */

$(document).on('change','.input #id_roleid', function(){
	if ($('#.input #id_roleid option:selected').text() == "Select Role")
	{
		b = $('.input li').each(function(i, li) {
	      var $product = $(li);  
		});
		b.hide()
	}
	else
	{
	  a  = $('#.input #id_roleid option:selected').attr("data-access");
	  a1 =  a.replace(/[^a-zA-Z0-9]/g, " ");
	  b = $('.input li').each(function(i, li) {
	       var $product = $(li);  
	       });
	  b.show()
	  for (i = 0;i<b.length;i++)
	     {
	             var z = '#id_access_' + i;
	             if(a1.indexOf(b[i].textContent) > 0)
	             {
	                     $(z).prop('checked', true);
	             }
	             else
	             {
	                     $(z).prop('checked', false);
	             }
	     }
	}
});

/* on selecting the all option select all the below access */

$(document).on('click','.input #id_access_0', function(){ 
    a = $('#id_access_0').val()
    b = $('.input li').each(function(i, li) {
    var $product = $(li);   	               
    });                 
    for(i=1;i<b.length;i++)                 
    {                          
	    var z = '#id_access_' + i;             
	    console.log(z)            
	    console.log($('#id_access_0').is(':checked'))
	    if ( $('#id_access_0').is(':checked') == true)
	    	$(z).prop('checked', true);                   
	    else            
	        $(z).prop('checked', false);      	      
    }    
  });
/* on selecting the all option select all the below allowed action */

$(document).on('click','.input #id_allowed_0', function(){ 
    a = $('#id_allowed_0').val()
    b = $('.input li').each(function(i, li) {
    var $product = $(li);   	               
    });                 
    for(i=1;i<b.length;i++)                 
    {                          
	    var z = '#id_allowed_' + i;             
	    console.log(z)            
	    console.log($('#id_allowed_0').is(':checked'))
	    if ( $('#id_allowed_0').is(':checked') == true)
	    	$(z).prop('checked', true);                   
	    else            
	        $(z).prop('checked', false);      	      
    }    
  });



$(document).on('click', 'input[type=submit][value=Create]', function(){
	platform = $('#id_cloudid option:selected').attr("data-platform");
	
	
	if(platform == "Cnext")
		{   
			if (($('#id_provider option:selected').attr("data-provider")) && $('#id_region option:selected').attr("data-name"))
		     {	
				return true;
		     }
			else
			{
			    alert("Please Select Provider and Region");
                return false;
			}
		}
	else{
		   return true;
		}
	
});

$(document).on('click', 'input[type=submit][value=SAVE]', function(){
	platform = $('#id_cloudids option:selected').attr("data-platform");
	
	
	if(platform == "Cnext")
		{   
			if (($('#id_providers option:selected').attr("data-provider")) && ($('#id_regions option:selected').attr("data-name")))
		     {	
				return true;
		     }
			else
			{
			    alert("Please Select Provider and Region");
                return false;
			}
		}
	else{
		   return true;
		}
	
});

horizon.modals.addModalInitFunction(function (modal) {
	  $(modal).find("#id_roleid").change();
	  $(modal).find("#id_cloudids").change();
	  $(modal).find("#id_cloudid").change();	  
	});

/* javascript to control remove all role for the user */
$(document).on('click', 'input[type=submit][value=REMOVE]', function(){
	a = $('.input li').each(function(i, li) {
    var $product = $(li);   	               
    });
	var total=0;
	for(i=0;i<a.length;i++){
		if($('#id_roles_' + i).is(':checked')){
			total =total +1;
		}
	}
	if(total > a.length-1){
		alert("User should have atleast one role.")
		return false;
		}
});
