function trim(str) {
	return str.replace(/^\s+|\s+$/g,"");
}
function addpackage(package) {
	document.MAINFORM.packages.value += " "+package;
}

function loadScript(url, callback)
{
   var head = document.getElementsByTagName('head')[0];
   var script = document.createElement('script');
   script.type = 'text/javascript';
   script.src = url;

   script.onreadystatechange = callback;
   script.onload = callback;

   head.appendChild(script);
}

function themepkgs() {
	var e = document.getElementById('imageconf_theme');
	var selected = e.options[e.selectedIndex].value;
	themepackages = selected;
	update_defaultpkgs();
}

// used to flip the display property
//function showHide(obj){
//  if(obj)
//    obj.style.display = obj.style.display=='none' ? 'block' : 'none'
//}


function dynwifi_addif(index) {
    var wifi_options = "";
    var wifi_if = "wifi" + index;
    //var hidden_name = "imageconf_" + wifi_if + "enabled";
    //wifi_options += '<input type="hidden" name="' + hidden_name + '" value="1" />';
    wifi_options += '<fieldset class="wifi-interface" data-index="' + index + '" id="wifi-interface-' + wifi_if + '">';
    wifi_options += '<legend>' + wifi_if + '</legend>';
    $.each(fields[wifi_if], function(key, value){
       wifi_options += fields[wifi_if][key];
    });
    wifi_options += '</fieldset>';
    
    var new_count = parseInt(index) + 1;
    $("#wifiifsnr").val(new_count);
    dynwifi_buttons(new_count);
    return wifi_options;
}

function dynwifi_remove_last() {
    var last_if = $("#wifi-interfaces").find("fieldset.wifi-interface").last();
    last_if.remove();
    var new_count = parseInt($("#wifiifsnr").val()) - 1;
    $("#wifiifsnr").val(new_count);
    console.log("remove, wifi count is now " + new_count);
    dynwifi_buttons(new_count);
}

function dynwifi_buttons(wifi_count) {
    console.log("changed" + wifi_count);
    if (wifi_count < 1) {
        $("#wifi-interface-remove").addClass("hidden");
    } else {
        $("#wifi-interface-remove").removeClass("hidden");
    }
    if (wifi_count >= wifi_ifs_max) {
        $("#wifi-interface-add").addClass("hidden");
    } else {
        $("#wifi-interface-add").removeClass("hidden");
    }
}

function dynwifi() {
    var wifi_index = 0;
    var wifi_ifs = parseInt($("#wifiifsnr").val());

    while ( wifi_index < wifi_ifs_initial || wifi_index < wifi_ifs ) {
        $("#wifi-interfaces").append(dynwifi_addif(wifi_index));
        $("#imageconf_wifi" + wifi_index + "enabled").prop('checked', true);;
        wifi_index++;
    }

    
    $("#wifi-interface-add").click(function() {
        //var last_index = $("#wifiifsnr").val();
        var last_index = $("#wifi-interfaces").find("fieldset.wifi-interface").last().data("index");
        var index = parseInt(last_index) + 1;
        console.log("foo" + last_index);
        if ( last_index === undefined) {
            last_index = -1;
        }
        
        $("#wifi-interfaces").append(dynwifi_addif(index));
        $("#imageconf_wifi" + index + "enabled").prop('checked', true);
    });
    
    $("#wifi-interface-remove").click(function() {
        dynwifi_remove_last();
    });
}
        

function help_toggle_init() {
    $(".help-toggle").each(function() {
        $(this).click(function() {
            var help_block = $(this).siblings(".help-block");
            if (help_block.hasClass("open")) {
                help_block.slideUp().removeClass("open");
                $(this).attr("title", msg_show_help);
            } else {
                help_block.slideDown().addClass("open");
                $(this).attr("title", msg_hide_help);
            }
        });
    });
}

/* Toggle Divs */

function ToggleDiv(DivID)
{   
    if (document.getElementById(DivID).style.display == "block")
    {   
        document.getElementById(DivID).style.display = "none";
    }   
    else
    {   
        document.getElementById(DivID).style.display = "block";
    }
}

function displayselect(obj,id1,id2) {
	txt = obj.options[obj.selectedIndex].value;
	document.getElementById(id1).style.display = 'none';
	document.getElementById(id2).style.display = 'none';
	if ( txt.match(id1) ) {
		document.getElementById(id1).style.display = 'block';
	}
	if ( txt.match(id2) ) {
		document.getElementById(id2).style.display = 'block';
	}
}

/* End Toggle Divs */

/* Package list */

var xmlHttpObject = false;

if (typeof XMLHttpRequest != 'undefined') 
{
	xmlHttpObject = new XMLHttpRequest();
}
if (!xmlHttpObject) 
{
	try 
	{
		xmlHttpObject = new ActiveXObject("Msxml2.XMLHTTP");
	}
	catch(e) 
	{
	try 
		{
			xmlHttpObject = new ActiveXObject("Microsoft.XMLHTTP");
		}
		catch(e) 
		{
			xmlHttpObject = null;
		}
	}
}

function loadContent(content)
{
	xmlHttpObject.open('get',content);
	xmlHttpObject.onreadystatechange = handleContent;
	xmlHttpObject.send(null);
	return false;
}

function handleContent()
{
	if (xmlHttpObject.readyState == 4)
	{
	document.getElementById('packagelist').innerHTML = xmlHttpObject.responseText;
	}
}

function handleProfilePkgs()
{
        if (xmlHttpObject.readyState == 4)
        {
		profilepackages=xmlHttpObject.responseText
		profilepackages=eval( "(" + profilepackages + ")" );
		var e = document.getElementById('imageconf_profile');
		var sel = e.options[e.selectedIndex].value
                profilepackages = profilepackages['info'][sel]['packages']
		update_defaultpkgs();
	}
}



function ProfilePkgs(content)
{
        xmlHttpObject.open('get',content);
        xmlHttpObject.onreadystatechange = handleProfilePkgs;
        xmlHttpObject.send(null);
        return false;
}


function sort_unique(array) {
	array.sort();
	for(var i = 1; i < array.length; i++) {
		if (array[i] === array[ i - 1 ]) {
			array.splice(i--, 1);
		}
	}
	return array;
};

function update_defaultpkgs() {

	if( typeof profilepackages != "undefined") {
		packages = profilepackages
	};
        addpackages = '';
	if( typeof user_packagelist != "undefined") {
		if (document.getElementById('imageconf_packages')) {
			addpackages += " " + user_packagelist;
		}
	}
	if( typeof lucipackages != "undefined") { addpackages += " " + lucipackages };
	if( typeof themepackages != "undefined") { addpackages += " " + themepackages };
	if( typeof defaultpackages != "undefined") { packages += " " + defaultpackages };
	if( typeof communitypackages != "undefined") { addpackages += " " + communitypackages };
	if( typeof nosharepackages != "undefined") { addpackages += " " + nosharepackages };
	if( typeof extrapackages != "undefined") { addpackages += " " + extrapackages };
	if( typeof ipv6packages != "undefined") { addpackages += " " + ipv6packages };
        if( typeof qospackages != "undefined") { addpackages += " " + qospackages };

	packages = packages.split(" ").sort();
	packages = packages.join(" ");
	addpackages = addpackages.split(" ")
	addpackages = sort_unique(addpackages);
	addpackages = trim(addpackages.join(" "));

	if (document.getElementById('default-packages')) {
		document.getElementById('default-packages').innerHTML = "<code>" + packages + "</code>";
	}

	if (document.getElementById('imageconf_packages')) {
		document.getElementById('imageconf_packages').value = addpackages;
	}

}


/* End package list */


function pass_status(field_hash) {
    var status = field_hash.data("pass_empty");
    if (field_hash.val().length > 0) {
        status = field_hash.data("pass_set");
        //status += ' (' + field_hash.val() + ')';
    }
    return status
}

function pass_init() {
    $(".password-hash-container").each(function(){
        var container = $(this);
        var field_hash = $(this).children(".password-hash").first();
        var btn_toggle = $(this).children(".password-edit-toggle").first();
        

        var status = pass_status(field_hash);
        btn_toggle.append('<span class="pass-status">' + status + '</span>');
        
        btn_toggle.click(function(e){
            if (! $(this).hasClass("open")) {
                e.preventDefault();
                $(this).addClass("open");
                pass_edit(container);
                return false;
            }
        });
    });
}

/* md5 crypt a password */
function pass_md5crypt(id) {
    var input = $("#" + id);
    var container = $("#" + id + "_container");
    var pw_plain = container.find('.pass-edit-pw1').val();

    if (pw_plain.length > 0) {
        var salt = random_salt(8);
        var hash = md5crypt(pw_plain, salt);
        if (hash.substr(0, 3) === "$1$") {
            input.val(hash);
        } else {
            input.val('');
            alert(input.data("error"));
        }   
    } else {
        alert(input.data("removed"));
        input.val('');
    }
}

function pass_verify(container) {
    var pw1 = container.find(".pass-edit-pw1");
    var pw2 = container.find(".pass-edit-pw2");
    var btn_toggle = container.children(".password-edit-toggle").first();
    
    if (pw1.val().length < 1 && pw2.val().length < 1) {
        pw1.removeClass("match mismatch");
        pw1.removeClass("match mismatch");
    } else {
        if (pw1.val() === pw2.val()) {
            pw1.removeClass("mismatch").addClass("match");
            pw2.removeClass("mismatch").addClass("match");
            btn_toggle.find("button").removeAttr("disabled");
        } else {
            pw1.removeClass("match").addClass("mismatch");
            pw2.removeClass("match").addClass("mismatch");
            btn_toggle.find("button").attr("disabled", "disabled");
        }
    }  
}

function pass_edit(container) {
    var field_hash = container.children(".password-hash").first();
    var btn_toggle = container.children(".password-edit-toggle").first();
    
    var pw1 = $('<input type="password" />')
           .addClass("string form-control pass-edit pass-edit-pw1")
           .attr("placeholder", field_hash.data("placeholder"))
           .keyup(function() {
               pass_verify(container);
           });
  
   
    var pw2 = $('<input type="password" />')
           .addClass("string form-control pass-edit pass-edit-pw2")
           .attr("placeholder", field_hash.data("placeholder_confirm"))
           .keyup(function() {
               pass_verify(container);
           });
   
    var pass_options = $('<div></div>')
            .addClass("pass-options")
    
    var btn_apply = $('<button type="button"></button>')
            .html(field_hash.data("apply"))
            .attr("disabled", "disabled")
            .addClass("btn btn-default")
            .click(function(){
                pass_md5crypt(field_hash.attr('id'));    
                field_hash = container.children(".password-hash").first();
                var status = pass_status(field_hash);
                container.find(".pass-options").remove();
                container.find(".password-edit-toggle").removeClass("open").html(status);
                return false;
            });
            
    pass_options.append(pw1);
    pass_options.append(pw2);
    pass_options.append(btn_apply);
   
    if (btn_toggle.find(".pass-options").length < 1) {
        btn_toggle.html(pass_options);
        //container.children(".pass-options").css({"display": "block", "float": "none" })
        btn_toggle.find(".pass-edit-pw1").focus();
    }
}

/* wizard step2 */

function set_packages() {
    var selected = $("#imageconf_profile").val();
    ProfilePkgs(ajaxUrl + session.target, selected);
}

function themeselect() {
    var selected = $("#imageconf_webif").val();
    if (selected === "none") {
        $("#theme_options").html('');
        lucipackages = "";
        themepackages = "";
        update_defaultpkgs();
    }
    if (selected === "luci") {
        var newdiv = fields.theme;
        document.getElementById("theme_options").innerHTML = newdiv;
        lucipackages = luci_default_packages;
        themepkgs();
        update_defaultpkgs();
    };
}

function lanselect() {
    var extra_fields = []
    var lan_options = ""
    var selected = $("#imageconf_lanproto").val();
    
    if (selected === "static") {
        $("#lan_options").empty();
    }
    
    if (selected === "olsr") {
        extra_fields = [ "lan_ipv6addr", "landhcp", "landhcprange" ];   
    }
    
    $.each(extra_fields, function( index, value ) {
        if (typeof fields[value] !== 'undefined') {
            lan_options += fields[value];
        }
    });
    
    $("#lan_options").html(lan_options);
}

function wanselect() {
    var selected = $('#imageconf_wanproto').val();
    var extra_fields = []
    var wan_options = ""
    
    if (selected == 'dhcp') {
        extra_fields = [ "wan_allow_ssh", "wan_allow_web", "localrestrict", "sharenet", "wan_qos" ];
    };
    
    if (selected == 'static') {
        extra_fields = [ "wanipv4addr",  "wannetmask", "wangateway", "wandns", "localrestrict", "sharenet", "wan_allow_ssh", "wan_allow_web", "wan_qos" ];
    }
    if (selected == 'olsr') {
        extra_fields = [ "wanipv4addr",  "wannetmask" ];
    };
    
    $.each(extra_fields, function( index, value ) {
        if (typeof fields[value] !== 'undefined') {
            wan_options += fields[value];
        }
    });
    $('#wan_options').html(wan_options);
}
;
wanselect();

function toggle_map_container(cmd, target) {
    if (cmd == 'show') {
        var osm1 = function() {
            loadScript('http://www.openstreetmap.org/openlayers/OpenStreetMap.js', osm2);
        };
        $(target).html("<div id='map'></div><div style='font-size:0.8em'>Map by <a href='http://www.openstreetmap.org' title='www.openstreetmap.org'>openstreetmap.org</a>, License CC-BY-SA</div>");
        loadScript('http://www.openlayers.org/api/OpenLayers.js', osm1);
        var osm2 = function() {
            loadScript(assets_js + "osm.js", do_map);
        };
        var do_map = function() {
            init();
            drawmap();
        };

    } else {
        $(target).html("");
    }
}

function nosharepkgs() {
    if (document.getElementById("imageconf_sharenet").checked) {
        nosharepackages = '';
        update_defaultpkgs();
    }
    else {
        nosharepackages = 'freifunk-policyrouting luci-app-freifunk-policyrouting luci-i18n-freifunk-policyrouting-de';
        update_defaultpkgs();
    }
}

function qospkgs() {
    if (document.getElementById("imageconf_wan_qos").checked) {
        qospackages = 'qos-scripts';
        $("#qos-options").html(wan_qos_down + wan_qos_up);
        update_defaultpkgs();
    }
    else {
        qospackages = '';
        $("#qos-options").html('');
        update_defaultpkgs();
    }
}

function ajax_packagelist() {
    $.ajax({
        url: package_vars.ajaxUrl,
        type: 'get',
        dataType: 'json',
        timeout: 10000,
        tryCount: 0,
        retryLimit: 10,
        success: function(json) {
            var packagelist = "";
            for (var section in json) {
                packagelist += '<div class="panel panel-default">';
                packagelist += '<div class="panel-heading" role="tab" id="' + section + '-heading">';
                var panel_title_link = '<a data-toggle="collapse" data-parent="#packagelist" href="#packages-' + section + '" aria-expanded="false" aria-controls="packages-' + section + '">' + section + '</a>';
                packagelist += '<h4 class="panel-title">' + panel_title_link + '</h4>';
                packagelist += '</div>';
                packagelist += '<div id="packages-' + section + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="' + section + '-heading">';
                packagelist += '<div class="panel-body">';
                packagelist += "<table><thead><tr>";
                packagelist += "<th></th>";
                packagelist += "<th width='300px'>" + package_vars.lang.Package + "</th>";
                packagelist += "<th width='450px'>" + package_vars.lang.Version + "</th>";
                packagelist += "<th width='100px'>" + package_vars.lang.Size + "</th>";
                packagelist += "</tr></thead>";
                d = json[section];
                for (var pkg in d) {
                    size = json[section][pkg]['size'];
                    version = json[section][pkg]['version'];
                    packagelist += "<tr>";
                    packagelist += "<td><input type='button' value='+' style='margin:0px 10px 0 0; border:0px' onClick='addpackage(\"" + pkg + "\");'></td>";
                    packagelist += "<td>" + pkg + "</td>";
                    packagelist += "<td>" + version + "</td>";
                    packagelist += "<td>" + size + "</td>";
                    packagelist += "</tr>";
                }
                packagelist += "</table></div></div></div>"
            }
            document.getElementById('packagelist').innerHTML = packagelist;
        },
        error: function(xhr, textStatus, errorThrown) {
            if (textStatus == 'parsererror') {
                $('#packagelist').html(package_vars.errors.parseError);
                return;
            }
            if (textStatus == 'timeout') {
                this.tryCount++;
                if (this.tryCount <= this.retryLimit) {
                    //try again
                    $.ajax(this);
                    return;
                }
                $('packagelist').html = package_vars.errors.timeout;
                return;
            }
            if (xhr.status == 500) {
                $('packagelist').html = package_vars.errors.serverError;
            }
            else {
                $('packagelist').html = package_vars.errors.unspecified;
            }
        }
    });
}

function ipv6pkgs() {
    if (document.getElementById("imageconf_ipv6")) {
        if (document.getElementById("imageconf_ipv6").checked) {
            ipv6packages = ipv6packages_default;
            update_defaultpkgs();
        } else {
            ipv6packages = '';
            update_defaultpkgs();
        }
    }
}

function init_step2() {
//    $("#accordion").accordion({
//        heightStyle: "content" }
//    );
    set_packages();
    update_defaultpkgs();
    themeselect();
    themepkgs();
    lanselect();
    wanselect();
    nosharepkgs();
    ipv6pkgs();
    update_defaultpkgs();
    dynwifi();
    ajax_packagelist();  
    $("#imageconf_profile").change(function() {
        set_packages();
    });
    $("#imageconf_webif").change(function() {
        themeselect();
        help_toggle_init();
    });
    $("#imageconf_theme").change(function() {
        themepkgs();
    });
    $("#imageconf_ipv6").change(function() {
        ipv6pkgs();
    });
    $("#imageconf_nodenumber").change(function() {
        FFReg.check(this.value, _ffreg_check_callback);
    });
    $("#imageconf_lanproto").change(function() {
        lanselect();
        help_toggle_init();
    });
    $("#imageconf_wanproto").change(function() {
        wanselect();
        help_toggle_init();
    });
    $("#imageconf_sharenet").change(function() {
        nosharepkgs();
    });
    $("#imageconf_wan_qos").change(function() {
        qospkgs();
    });
    $("#showmap").click(function() {
        var button = $(this);
        if (button.html() === button.data("hidden")) {
                button.html(button.data("visible"));
                toggle_map_container('show', "#map-container");
        } else {
            button.html(button.data("hidden"));
            toggle_map_container('hide', "#map-container");
        }
    });
}

function set_lang(lang) {
    var date = new Date();
    cookieDate = date.setTime(date.getTime() + (100 * 24 * 60 * 60 * 1000));
    document.cookie = 'all_lang=' + lang + ';expires=' + cookieDate + '';
    window.location.reload();
}

$( document ).ready(function() {
    help_toggle_init();
    pass_init();
    $("#language-select").change(function() {
        set_lang($(this).val())
    });
});


/* end wizard step2 */