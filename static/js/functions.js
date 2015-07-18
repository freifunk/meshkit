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
    var theme_select = $('#imageconf_theme');
    if ( theme_select.length ) { 
        themepackages = theme_select.val();
        update_defaultpkgs();
    }
}

function sticky_footer() {
    var window_height =  $(window).height();
    var footer_height = $("footer.footer").outerHeight();
	var scroll_height = $(window).scrollTop();
	var activate_height = $(document).height() - window_height - footer_height;
    
	if (scroll_height > activate_height) {
		$("footer.footer").removeClass('sticky')
            .css({"bottom": "auto"});
            $(".main-content").css({"padding-bottom": 0});
	} else {
		$("footer.footer").addClass("sticky")
            .css({"bottom": (footer_height - 30) / -1 });
            $(".main-content").css({"padding-bottom": footer_height});
	}
}

function init_grid() {
    /* enable all checkboxes on click in a selectable SQLFORM.grid */
    $('.grid-check-all').click(function(e) {
        var table = $(e.target).closest('table');
        $('td input:checkbox[name="records"]', table).prop('checked', this.checked);
    });
    
    /* add confirm message to delete all button */
    $(".w2p-confirm").click(function(e) {
        if (!$.web2py.confirm(w2p_ajax_confirm_message)) {
            e.preventDefault();
            $.web2py.stopEverything(e);
            return;
        }
    });
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
    dynwifi_buttons(new_count);
}

function dynwifi_buttons(wifi_count) {
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
    $( document ).on( "click", ".help-toggle", function() {
        var help_block = $(this).siblings(".help-block");
        if (help_block.hasClass("open")) {
            help_block.slideUp().removeClass("open");
            $(this).attr("title", msg_show_help);
        } else {
            help_block.slideDown().addClass("open");
            $(this).attr("title", msg_hide_help);
        }
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
    if (xmlHttpObject.readyState === 4) {
        profilepackages = xmlHttpObject.responseText;
        profilepackages = eval("(" + profilepackages + ")");

        var profile_select = $('#imageconf_profile');
        if (profile_select.length) {
            var sel = $('#imageconf_profile').val();
            var e = document.getElementById('imageconf_profile');
            var sel = e.options[e.selectedIndex].value;

            profilepackages = profilepackages['info'][sel]['packages'];
            update_defaultpkgs();
        }
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
	if( typeof webifpackages != "undefined") { addpackages += " " + webifpackages };
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
    ProfilePkgs(ajaxUrl + '/' + session.target, selected);
}

function themeselect() {
    var webif_packages = $("#imageconf_webif").find('option:selected').data('packages');
    if ( webif_packages.indexOf('luci-mod-admin') >= 0) {
        $("#theme_options").html(fields.theme);
        webifpackages = webif_packages;
        themepkgs();
        update_defaultpkgs();
    } else {
        $("#theme_options").html('');
        webifpackages = "";
        themepackages = "";
        update_defaultpkgs();   
    }
}

var range_bandwidth_sliders = {
	'min': [ 128, 16],
	'20%': [ 1024, 64 ],
	'50%': [ 4096, 128 ],
    '70%': [ 8192, 128 ],
    '85%': [ 16384, 256 ],
	'max': [ 100000 ]
};

function init_range_sliders() {
    $(".input-slider").each(function(){
       var linked_input = $(this).siblings("input").first();
       var preset = $(this).data("preset");
       var range = {};
       if (preset === 'bandwidth') {
           range = range_bandwidth_sliders;
       }
       $(this).noUiSlider({
            range: range,
            start: linked_input.val(),
            format: {
                to: function(value) {
                    return parseInt(value);
                },
                from: function(value) {
                    return parseInt(value);
                }
            }
        });
       $(this).noUiSlider_pips({
            mode: 'range',
            density: 3
        });
        $(this).Link('lower').to(linked_input);
    });
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
        $("#qos-options").html(fields.wan_qos_down + fields.wan_qos_up);
        update_defaultpkgs();
        init_range_sliders();
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
    init_range_sliders();
    ajax_packagelist();  
    $("#imageconf_profile").change(function() {
        set_packages();
    });
    $("#imageconf_webif").change(function() {
        themeselect();
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
    });
    $("#imageconf_wanproto").change(function() {
        wanselect();
    });
    $("#imageconf_sharenet").change(function() {
        nosharepkgs();
    });
    $("#imageconf_wan_qos").change(function() {
        qospkgs();
    });
}

function set_lang(lang) {
    var date = new Date();
    cookieDate = date.setTime(date.getTime() + (100 * 24 * 60 * 60 * 1000));
    document.cookie = 'all_lang=' + lang + ';expires=' + cookieDate + '';
    window.location.reload();
}

/* Map init and control functions */
function toggle_map_container(cmd, target) {
    if (cmd === 'show') {
        if ( $("#map").length ) {
            $(target).addClass('visible').slideDown();
        } else {
            var osm1 = function() {
                loadScript('http://www.openstreetmap.org/openlayers/OpenStreetMap.js', osm2);
            };
            $(target).html("<div id='map'></div><div class='powered-by-osm'>" +
                    "Map by <a href='http://www.openstreetmap.org' " +
                    "title='www.openstreetmap.org'>openstreetmap.org</a>, " +
                    "License CC-BY-SA</div>"
            ).addClass('visible').slideDown();
            loadScript('http://www.openlayers.org/api/OpenLayers.js', osm1);
            var osm2 = function() {
                loadScript(assets_js + "/osm.js", do_map);
            };
            var do_map = function() {
                init();
                drawmap();
            };
        }
    } else {
        $(target).slideUp().removeClass('visible');
    }
}

function map_init() {
    $("#showmap").click(function(e) {
        e.preventDefault();
        var button = $(this);
        if (button.html() === button.data("hidden")) {
            button.html(button.data("visible"));
            toggle_map_container('show', "#map-container");
        } else {
            button.html(button.data("hidden"));
            toggle_map_container('hide', "#map-container");
        }
    });
    
    $('.map-latitude, .map-longitude').change(function() {
        var lat = $('.map-latitude').val();
        var lon = $('.map-longitude').val();
        if ( $("#map") && parseFloat(lat) && parseFloat(lon)) {
            var y = lat2merc(lat);
            var x = lon2merc(lon);
            
            var lonLat = new OpenLayers.LonLat(lon, lat)
                    .transform(
                            new OpenLayers.Projection("EPSG:4326"), // Transformation aus dem Koordinatensystem WGS 1984
                            map.getProjectionObject() // in das Koordinatensystem 'Spherical Mercator Projection'
                            );
            map.panTo(lonLat);
            marker = markers['markers'][0];
            
            markers.removeMarker(marker);
            markers.addMarker(new OpenLayers.Marker(lonLat));
        }
    });
}

/* End Map init and control functions */

$( document ).ready(function() {
    $(".equal-height > div").matchHeight();
    sticky_footer();
    $(window).scroll(function() {
        sticky_footer();
    });
    help_toggle_init();
    pass_init();
    map_init();
    init_grid();
    $("#language-select").change(function() {
        set_lang($(this).val());
    });
    // Prevent closing the dropdown when user clicks on an input element
    $('.dropdown input, .dropdown label').click(function(e) {
        e.stopPropagation();
    });
});


/* START functions for the build.html page (build status/output) */

function update_buildqueue_status() {
    var timeout = 5000;
    var retries = 10;
    var tryCount = 0;

    $.ajax({
        url: url.status_ajax,
        type: 'get',
        data: '',
        dataType: 'json',
        timeout: timeout,
        tryCount: 0,
        retryLimit: retries,
        success: function(json) {
            function addLinks(name, size) {
                var size = (o.size / 1024 / 1024).toFixed(2);
                var addnew = "<a href='" + url.baseurl_bin + name + "'>" + name + "</a> (" + size + " M)<br/>";
                files = files + addnew;
            }
            var files = "";
            var meta = "";
            for (var i = json.length - 1; i >= 0; --i) {
                var o = json[i];
                var name = o.name;
                if (name == "md5sums" || name == "summary.json" || name == "build.log" || name == "sha256sums") {
                    var size = (o.size / 1024 / 1024).toFixed(2);
                    var addnew = "<a href='" + url.baseurl_bin + name + "'>" + name + "</a>";
                    meta = meta + " " + addnew;
                } else {
                    if (name.search("openwrt-ar71xx") != -1) {
                        if (name.search("sysupgrade") != -1 || name.search("factory") != -1) {
                            addLinks(name, o.size);
                        }
                    } else {
                        addLinks(name, o.size);
                    }
                }
            }
            meta = meta + "<br /><a href='" + url.baseurl_bin + "'>" + i18n.show_bindir + "</a>";
            $('#imagelist').html(
                files + "<br /><strong>" + i18n.metadata + "</strong>" + meta + "<br />"
            );
        },
        error: function(xhr, textStatus, errorThrown) {
            if (textStatus == 'timeout') {
                this.tryCount++;
                if (this.tryCount <= this.retryLimit) {
                    //try again
                    $.ajax(this);
                    return;
                }
                alert('We have tried ' + this.retryLimit + ' times and it is still not working. We give in. Sorry.');
                return;
            }
            if (xhr.status == 500) {
                alert('There seems to be a server problem, please try again later.');
            }
            else if (xhr.status == 404) {
                tryCount++;
                if (tryCount <= retries) {
                    setTimeout("ajax()", timeout);
                    return;
                }
            } else {
                alert('Oops! There was a problem, sorry.');
            }
        }
    });

}

function set_buildqueue_status_icon(classname) {
    $("#status .buildqueue-status")
            .removeClass('icon-hourglass icon-status-ok icon-status-notok icon-spin1')
            .addClass(classname);
}

function refreshQueue() {
    $.getJSON(url.status_api, '', function(json, textStatus) {
        var queued = json.queued;
        var status = json.status;
        if (status === 0) {
            msgsuccess = i18n.success;
            jQuery(".flash").html(msgsuccess).slideDown();
            set_buildqueue_status_icon("icon-status-ok");
            $("#status .buildqueue-status").html(i18n.success_msg);
            update_buildqueue_status();
            clearInterval(refreshInterval);
        }

        if (status === 1) {
            set_buildqueue_status_icon("icon-hourglass");
            $("#status .buildqueue-status").html(i18n.queued_msg + " " + queued);
        };

        if (status === 2 || status === 3) {
            msgfailed = i18n.failed;
            jQuery(".flash").html(msgfailed).slideDown();
            $("#status .buildqueue-status").html(i18n.failed_msg);
            set_buildqueue_status_icon("icon-status-notok");
            update_buildqueue_status();
            clearInterval(refreshInterval);
        }
        ;

        if (status === 4) {
            set_buildqueue_status_icon("icon-spin1");
            $("#status .buildqueue-status").html(i18n.processing);
        }
    });
}

/* END functions for the build.html page (build status/output) */

/* functions for status page */
function refreshStats() {
    $.getJSON('api/json/status', '', function(json, textStatus) {
        var workers_running = json.num_workers;
        if (workers_running > 0) {
            $(".worker").removeClass("icon-status-notok")
                    .addClass("icon-status-ok");
            $(".worker > .sr-only").html(i18n.yes);
        } else {
            $(".worker").removeClass("icon-status-ok")
                    .addClass("icon-status-notok");
            $(".worker > .sr-only").html(i18n.no);
        }
        $("#num-worker").html(workers_running);

        document.getElementById('memfree').innerHTML = json.memfree;
        document.getElementById('memused').innerHTML = json.memused;
        document.getElementById('loadavg').innerHTML = json.loadavg;
        updateGraphs(json);
    });
}
/* End functions for status page */

/* graphs (flotcharts.js) */

/* add an additional legent/annotation to a flotchart graph */
function graph_add_label(target, label) {
    var placeholder = $(target);
    placeholder.append(
        '<div class="annotation">' + label + '</div>'
    );    
}

/* format labels for flotchart pie graphs */
function labelFormatter(label, series) {
    return "<div class='pie-label'>" + label + "<br/>" + series.data[0][1] + "</div>";
}

/* render a pie chart */
function graph_pie(target, data) {
    var placeholder = $(target);
    /* set height of the placeholder */
    placeholder.css({height:placeholder.width() * 0.6});    
    $.plot(placeholder, data, {
        series: {
            pie: {
                innerRadius: 0.2,
                show: true,
                tilt: 0.4,
                opacity: 0.5,
                label: {
                    show: true,
                    radius: 0.75,
                    threshold: 0.05,
                    formatter: labelFormatter,
                    border: 1,
                    background: {
                        color: "#efefef",
                        opacity: 0.7
                    }
                },
            },
        },
    })
}

function graph_labels_and_colors(i, val) {
    var label = i;
    if (typeof val[1] !== 'undefined') {
        label = val[1];
    }
    var data = {
        data: val[0],
        label: label
    };
    if (typeof val[2] !== 'undefined') {
        data["color"] = val[2];
    }
    return data;
}

function graph_builds(stats) {
    /* graph build statistics */
    var data_status = [];
    var builds_total = 0;
    jQuery.each(stats["data"], function(i, val) {
        var data = graph_labels_and_colors(i, val);
        data_status.push(data);
        builds_total = builds_total + val[0];
    });
    var target = "#builds-overview";
    graph_pie(target, data_status);
    var title = stats["title"] + " | " + "Total: " + builds_total;
    graph_add_label(target, title);
}

function graph_builds_community(stats) {
    /* graph build count per community */
    var data = [];
    jQuery.each(stats["data"], function(i, val) {
        data.push(graph_labels_and_colors(i, val));
    });
    var target = "#builds-community";
    graph_pie(target, data);
    var title = stats["title"];
    graph_add_label(target, title);
}

function graph_builds_target(stats) {
    /* graph build count per target */
    var data = [];
    jQuery.each(stats["data"], function(i, val) {
        data.push(graph_labels_and_colors(i, val));
    });
    var target = "#builds-target";
    graph_pie(target, data);
    var title = stats["title"];
    graph_add_label(target, title);
}

function updateGraphs(json) {
    graph_builds(json.build_status);
    graph_builds_community(json.builds_community)
    graph_builds_target(json.builds_target)
}

/* end graphs */
