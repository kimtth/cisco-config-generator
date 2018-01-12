$(document).on("click", ".removeRow",
	function () {
		// $(this).closest("addinput").remove();
		$(this).parent().remove();
	}
);

$(document).on("click", ".addRow",
	function () {
		var tr = "<span class=\"addinput\" >"
		tr += $(this).parent().parent().find("span.addinput").html();
		tr +=
			'<span class="removeRow" style="font-size:10px;"> <img src="images/list-remove.png"></span>';
		tr += '</span>'
		$(this).parent().parent().append(tr);
	}
);

$(document).on("click", "#clear_event",
	function () {
		$("#generated_config").text("");
        clear_buff();
	}
);

var clear_buff = function(){
    $.ajax({
        url: "/config_clear",
        data: "",
        cache: false,
        processData: false,
        contentType: false,
        type: 'GET',
        success: function (rtn_data) {
            console.log("clean_completed summit");
        },
        error : function (rtn_data){
            console.log("error");
        }
     });
}

$(document).on("click", "#run_event",
	function () {
		//var text_config = config_template;
		clear_buff();
		ajaxReadConfig("config_form");
	}
);

//sending form data with post by ajax
var ajaxReadConfig = function(object_id){
	var my_form = $("#" + object_id);

    $.ajax({
        url: "/config_cisco_basic_route",
        data: my_form.serialize(),
        cache: false,
        processData: false,
        contentType: false,
        type: 'POST',
        success: function (rtn_data) {
			$("#generated_config").text(rtn_data);
            console.log("completed summit");
        },
		error : function (rtn_data){
			console.log(rtn_data)
			console.log("error");
		}
    });
}

var readTextFile = function(file)
{
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                alert(allText);
            }
        }
    }
    rawFile.send(null);
}