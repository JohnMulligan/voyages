# remaining work on maps ui

~~## 1. fix oddities with the search ui~~

~~* there are certain ports that aren't rendering properly when we search~~
~~	* rio pongo when region of embarkation is senegambia & offshore atlantic --> why is it even appearing in the results?~~

~~I am pretty sure this is an issue with the search ui, not with my use of it~~

## 2. handle mapping for geographically distributed languages

need stable m2m relations added to the language_group --> moderncountry

~~* waiting on philip & david for these~~
* waiting on domingos for proper integration of language_group into the search bar

~~## 3. handle mapping for overlapping nodes~~

~~* some language groups & even ports have the exact same lat/long, out to 7 decimal places~~
~~* I could make marker clustering to differentiate these (and may have to for #2 above...) but I think at base this is a data problem. if we're mapping with that kind of precision, then why do 5-ish Yoruba language groups have the exact same location?~~

## 4. translation

* need to integrate the terms used in the map into the django po's

## 5. more interactivity?

* zoom to fit
	* click on a region, it zooms you in to the bounds of the constituent ports
	* downside of this is that i'm not sure how the mobile would look
	* right now mouseover or click nodes gets you a popup -- adding click=zoom interactivity, would tablet users be unable to see those region popups because they'd be hurried into the port-level zoom?
* auto-filter origins
	* we're now showing routes to origins only when the connected nodes are moused over
	* but i could see it cleaning the interface up even further if that mouseover event hid the non-relevant origin nodes?
	* downside is that i'm not sure what subsequent user event would trigger the reappearance of those hidden nodes... we're getting close to functionality that is better handled as a query/search

## 6. manual data changes

* ports
	* 60699 to 7.9840736,4.5504317
	* 60502 to ???
	* 60917 to ???
	* 60220 to ???
	* 60501 looks to be way too far inland
	* 60264 to -13.2857840,8.4275610
	* something wrong with Iles Plantain -- route origin doesn't align with port location
* language groups (lat/long)
	* 160219 to -8.0391000,5.1441000
	* 360605 to ???
* language group (codes): The following language group codes were swapped from a-->b in the people_to_languagegroups.tsv map before importing the data
	* 160273 to 160272
	* 160524 to 160523
	* 160525 to 160523
* Link
	* Mandinka to 6012, 6013, 6014, 6021, 6022
	* Arabic/Islamic to 6012, 6013, 6014, 6021, 6022, 6031, 6032, 6041, 6042, 6051, 6052, 6061, 6064, 6065, 6082

