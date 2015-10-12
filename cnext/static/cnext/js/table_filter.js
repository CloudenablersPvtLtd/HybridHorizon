//horizon.datatables.set_table_query_filter_pro = function (parent) {
//  $(parent).find('table').each(function (index, elm) {
////    var input = $($(elm).find('div.table_search input')),
////        table_selector;
//	var input = $('#pro_filter')
//    console.log(input);
//    if (input.length > 0) {
//      // Disable server-side searcing if we have client-side searching since
//      // (for now) the client-side is actually superior. Server-side filtering
//      // remains as a noscript fallback.
//      // TODO(gabriel): figure out an overall strategy for making server-side
//      // filtering the preferred functional method.
//      input.on('keypress', function (evt) {
//        if (evt.keyCode === 13) {
//          return false;
//        }
//      });
//      input.next('button.btn-search').on('click keypress', function (evt) {
//        return false;
//      });
//
//      // Enable the client-side searching.
//      table_selector = 'table#' + $(elm).attr('id');
//      console.log(table_selector)
//      input.quicksearch(table_selector + ' tbody tr ', {
//        'delay': 300,
//        'loader': 'span.loading',
//        'bind': 'keyup click',
//        'show': this.show,
//        'hide': this.hide,
//        onBefore: function () {
//          var table = $(table_selector);
//          horizon.datatables.remove_no_results_row(table);
//        },
//        onAfter: function () {
//          var template, table, colspan, params;
//          table = $(table_selector);
//          horizon.datatables.update_footer_count(table);
//          horizon.datatables.add_no_results_row(table);
//          horizon.datatables.fix_row_striping(table);
//        },
//        prepareQuery: function (val) {
//          return new RegExp(val, "i");
//        },
//        testQuery: function (query, txt, _row) {
//          return query.test($(_row).find('td:not(.hidden):not(.actions_column)').text());
//        }
//      });
//    }
//  });
//};
//horizon.datatables.set_table_query_filter_reg = function (parent) {
//	  $(parent).find('table').each(function (index, elm) {
////	    var input = $($(elm).find('div.table_search input')),
////	        table_selector;
//		var input = $('#reg_filter')
//	    console.log(input);
//	    if (input.length > 0) {
//	      // Disable server-side searcing if we have client-side searching since
//	      // (for now) the client-side is actually superior. Server-side filtering
//	      // remains as a noscript fallback.
//	      // TODO(gabriel): figure out an overall strategy for making server-side
//	      // filtering the preferred functional method.
//	      input.on('keypress', function (evt) {
//	        if (evt.keyCode === 13) {
//	          return false;
//	        }
//	      });
//	      input.next('button.btn-search').on('click keypress', function (evt) {
//	        return false;
//	      });
//
//	      // Enable the client-side searching.
//	      table_selector = 'table#' + $(elm).attr('id');
//	      console.log(table_selector)
//	      input.quicksearch(table_selector + ' tbody tr ', {
//	        'delay': 300,
//	        'loader': 'span.loading',
//	        'bind': 'keyup click',
//	        'show': this.show,
//	        'hide': this.hide,
//	        onBefore: function () {
//	          var table = $(table_selector);
//	          horizon.datatables.remove_no_results_row(table);
//	        },
//	        onAfter: function () {
//	          var template, table, colspan, params;
//	          table = $(table_selector);
//	          horizon.datatables.update_footer_count(table);
//	          horizon.datatables.add_no_results_row(table);
//	          horizon.datatables.fix_row_striping(table);
//	        },
//	        prepareQuery: function (val) {
//	          return new RegExp(val, "i");
//	        },
//	        testQuery: function (query, txt, _row) {
//	          return query.test($(_row).find('td:not(.hidden):not(.actions_column)').text());
//	        }
//	      });
//	    }
//	  });
//	};
//	
//horizon.datatables.set_table_query_filter_pro($('body'));
//horizon.datatables.set_table_query_filter_reg($('body'));
//
//horizon.modals.addModalInitFunction(horizon.datatables.set_table_query_filter_pro);
//horizon.modals.addModalInitFunction(horizon.datatables.set_table_query_filter_reg);



//window.location="http://127.0.0.1/cnext/images/" + filter_pro + "/" + filter_reg

$(document).on('change','.provider-region #pro_filter', function()
		{
	            $("#reg_filter").val([]);
				filter_pro = $('#pro_filter option:selected').attr("data_provider").toLowerCase();
				if(filter_pro == "all")
					{
					$("#reg_filter").closest(".control-group").show();
					$("#reg_filter").children().show();
					}
				else{
					
				$("#reg_filter").closest(".control-group").show();
                $("#reg_filter").children().hide();
                $("#reg_filter").children('option[data_provider="'+ filter_pro +'"]').css('display','block');
				}
                comp_id = $('.table_wrapper').find('table')[0].id;
                row_length = $("#"+comp_id).find('tr').length;
			    for (var i=2;i<row_length;i++)
			    	{
			    	    if(filter_pro == "all")
			    	    {
			    	    	$("#"+$("#"+comp_id).find('tr')[i].id).show();
			    	    }
			    	    else if ($("#"+$("#"+comp_id).find('tr')[i].id).attr("data-provider") == filter_pro)
			    		{
			    			$("#"+$("#"+comp_id).find('tr')[i].id).show();
			    		}
			    		else
			    		{
			    			$("#"+$("#"+comp_id).find('tr')[i].id).hide();
			    		}
			    	}
			    table_selector = 'table#' + comp_id;
			    var table = $(table_selector);
			    horizon.datatables.update_footer_count(table);
		                 
		}
		
);


$(document).on('change','.provider-region #reg_filter', function()
{   
	
	filter_pro = $('#reg_filter option:selected').attr("data_provider").toLowerCase();
    filter_reg = $('#reg_filter option:selected').val().toLowerCase(); 
    comp_id = $('.table_wrapper').find('table')[0].id
    row_length = $("#"+comp_id).find('tr').length;
    for (var i=2;i<row_length;i++)
    	{
    	    if(filter_pro == "all" && filter_reg == "all" )
            {
    	    	$("#"+$("#"+comp_id).find('tr')[i].id).show();
            }
    	    else if ($("#"+$("#"+comp_id).find('tr')[i].id).attr("data-provider") == filter_pro && $("#"+$("#"+comp_id).find('tr')[i].id).attr("data-region") == filter_reg)
    		{
    			$("#"+$("#"+comp_id).find('tr')[i].id).show();
    		}
    		else
    		{
    			$("#"+$("#"+comp_id).find('tr')[i].id).hide();
    		}
    	}
    table_selector = 'table#' + comp_id;
    var table = $(table_selector);
    horizon.datatables.update_footer_count(table);
}
);

$( document ).ready(function() {
	$("#pro_filter").val(["ALL"]);
	$("#reg_filter").val(["ALL"]);
	});




