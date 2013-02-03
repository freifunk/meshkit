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

/*
function themeselect(themeoptions) {
	var e = document.getElementById('imageconf_webif');
	var selected = e.options[e.selectedIndex].value;
	if ( selected == 'none' ) {
		document.getElementById('theme_options').innerHTML = '';
		lucipackages = '';
		themepackages= '';
		update_defaultpkgs();
		};
	if ( selected == 'luci' ) {
		document.getElementById('theme_options').innerHTML = themeoptions;
		lucipackages = themeoptions;
		themepkgs();
		update_defaultpkgs();
		hideAll();
	};
}
*/  

/* Help link toggle */
/* from http://www.websemantics.co.uk/resources/accessible_form_help/scripts/showhide.js */

function addEvent(func){
  if (!document.getElementById | !document.getElementsByTagName) return
  var oldonload=window.onload
  if (typeof window.onload != 'function') {window.onload=func}
  else {window.onload=function() {oldonload(); func()}}
}

addEvent(hideAll)

function hideAll(){
  var obj,nextspan,anchor,content

  // get all spans
  obj=document.getElementsByTagName('span')

  // run through them
  for (var i=0;i<obj.length;i++){

    // if it has a class of helpLink
    if(/helpLink/.test(obj[i].className)){

      // get the adjacent span
      nextspan=obj[i].nextSibling
      while(nextspan.nodeType!=1) nextspan=nextspan.nextSibling

       // hide it
      nextspan.style.display='none'

      //create a new link
      anchor=document.createElement('a')

      // copy original helpLink text and add attributes
      content=document.createTextNode(obj[i].firstChild.nodeValue)
      anchor.appendChild(content)
      anchor.href='#help'
      anchor.title='Click to show help'
      anchor.className=obj[i].className
      anchor.nextspan=nextspan
      anchor.innerHTML='?'
      anchor.onclick=function(){showHide(this.nextspan);changeTitle(this);return false}
      // replace span with created link
      obj[i].replaceChild(anchor,obj[i].firstChild)
    }
  }
}

// used to flip helpLink title
function changeTitle(obj){
  if(obj)
    obj.title = obj.title=='Click to show help' ? 'Click to hide help' : 'Click to show help'
}

// used to flip the display property
function showHide(obj){
  if(obj)
    obj.style.display = obj.style.display=='none' ? 'block' : 'none'
}

/* End helplinktoggle */

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

	packages = packages.split(" ").sort();
	packages = packages.join(" ");
	addpackages = addpackages.split(" ")
	addpackages = sort_unique(addpackages);
	addpackages = trim(addpackages.join(" "));

	if (document.getElementById('default_packages')) {
		document.getElementById('default_packages').innerHTML = "<code>" + packages + "</code>";
	}

	if (document.getElementById('imageconf_packages')) {
		document.getElementById('imageconf_packages').value = addpackages;
	}

}

/* End package list */
