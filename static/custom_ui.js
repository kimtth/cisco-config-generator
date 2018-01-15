$( document ).ready(function() {
    $("input[name=enSSH][value=yes]").prop("checked", true);
    $("input[name=svpn][value=yes]").prop("checked", true);
    $("input[name=privateSSH][value=yes]").prop("checked", true);

     $("input[name=dnsServer][value=no]").prop("checked", true);
     $("input[name=svpnRadius][value=no]").prop("checked", true);

     $("input[name=fqdn_hostname]").val("router1.lan.local");
     $("input[name=admin_username]").val("admin");
     $("input[name=admin_password]").val("admin");

     $("input[name=wan_interface]").val("GigabitEthernet0/1");
     $("input[name=lan_interface]").val("GigabitEthernet0/0");

     $("input[name=svpnradius_ip]").val("192.168.1.1");
     $("input[name=svpnradius_name]").val("rrad1");
     $("input[name=svpnradius_serverkey]").val("xxxxxxx");

     $("input[name=guestvlan]").val("0");
     $("input[name=qos_upload]").val("8000");
     $("input[name=vlans]").val("1,2");
     $("input[name=vlan_ips]").val("10.1.v.1/24");
     $("input[name=sshaltport]").val("8022");

     $("input[name=dhcp_onvlan]").val("all");
     $("input[name=dhcp_scope]").val("195.130.131.139");
     $("input[name=ntp_server_ip]").val("195.104.37.238");

     $("input[name=vlan_style]").val("subinterface");
});

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