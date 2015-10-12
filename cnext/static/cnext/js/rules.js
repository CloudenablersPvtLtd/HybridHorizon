
$(document).on('change','#id_protocoldetail_details', function()
		{
				default_port = $('#id_protocoldetail_details option:selected').val();
			        $("#id_fromport_details").val([]);
                                
                                $("#id_fromport_details").children().hide();
                $("#id_fromport_details").children('option[data-protocoldetail="'+ default_port+'"]').css('display','block');
                
                                $("#id_toport_details").val([]);
                                
                                $("#id_toport_details").children().hide();
                $("#id_toport_details").children('option[data-protocoldetail="'+ default_port+'"]').css('display','block');          

                
                
		}
);



$(document).on('change','#id_protocoldetail_details',function(){
        populateSelect();
    });
    
function populateSelect(){
    c=$('#id_protocoldetail_details').val();
    $('#id_protocol_list').html('');
    
    if((c=='http')||(c=='ssh')||(c=='https')||(c=='ldap')||(c=='microsoftsql')||(c=='pop3')||(c=='pop3s')||(c=='imaps')||(c=='smtp')||(c=='smtps')){
            $('#id_protocol_list').append('<option>'+'tcp'+'</option>');
    } 
    else if((c=='rdp')||(c=='mysql')||(c=='imap')){
            $('#id_protocol_list').append('<option>'+'tcp'+'</option>');
            $('#id_protocol_list').append('<option>'+'udp'+'</option>');
    }
    else{
            $('#id_protocol_list').append('<option>'+'tcp'+'</option>');
            $('#id_protocol_list').append('<option>'+'udp'+'</option>');
            $('#id_protocol_list').append('<option>'+'icmp'+'</option>');
}
}