/* Initialize variables*/
var section_prefix = "voyage";
var templateprefix = "method-";
var currentid = "voyage-guide-intro";
var current_section_name = "Guide";
var wrappername = "methodology00";
var selectedClass = "voyage_selected";
var enableCollapse = false; 

var sectionToc = [
	{"mainid" : "voyage-guide-intro", "hasSubsection" : false,},
	{"mainid" : "voyage-methodology", "hasSubsection" : true, "wrappername": "methodology00", },
]

$(document).ready(function() {
	/* Set up event handlers */
	setupleftmenu();
	
	/* Customize "Guide" to keep displaying all content */
	$("#voyage-guide").unbind("click");
	
	$("#voyage-guide").click(function() {
		$("#center-content-inner").load("voyage-guide.html", function() {
			$("#center-content-inner").resize();
		});
	});
	
	/* Default loading of the first page */
	$("#center-content-inner").load(currentid + ".html");
	$("#prev-page").hide();
	$("#next-page").hide();
	$("#inner-content-header").hide();	
});