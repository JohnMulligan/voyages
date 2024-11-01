from concurrent.futures import process
from distutils.log import fatal
from unittest import skip
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.transaction import atomic
import csv
from voyages.apps.common.utils import *
from voyages.apps.past.models import Enslaved, EnslavedInRelation, EnslavedSourceConnection, EnslavementRelation, EnslavementRelationType, EnslaverAlias, EnslaverIdentity, EnslaverIdentitySourceConnection, EnslaverInRelation, EnslaverRole, EnslaverVoyageConnection, EnslaverCachedProperties,CaptiveFate
from voyages.apps.voyage.models import Place, Voyage,VoyageSources,VoyageShipOwnerConnection,VoyageCaptainConnection
import re

class Command(BaseCommand):
	
	def handle(self, *args, **options):

		def noblank(v,c=None,blank=False):
			if type(v)==list:
				v=v[0]
			if v in ['',None]:
				if blank:
					return ''
				else:
					return None
			else:
				if c=='int':
					return(int(float(v)))
				elif c=='float':
					return(float(v))
				else:
					return v

		def getuniqueorcreatenew(uniqueobj,objdata):
			if len(uniqueobj)!=0:
				return uniqueobj[0]
			else:
				return objdata

		allvoyages=Voyage.all_dataset_objects.all().filter(dataset=1)
		
		##step 1: enslaver setup
		enslavercachedproperties=[]
		enslavervoyageconnections=[]
		enslaver_identities={}
		enslaver_aliases={}
		enslaver_identity_pk_ai=max(EnslaverIdentity.objects.all().values_list('id'))[0]+1
		enslaver_alias_pk_ai=max(EnslaverAlias.objects.all().values_list('id'))[0]+1

		texas_enslaver_aliases=EnslaverAlias.objects.all().filter(manual_id__icontains='Texas')
		texas_enslaver_identities=EnslaverIdentity.objects.all().filter(aliases__manual_id__icontains='Texas')
		enslaver_roles={}
		for enslaver_role_name in ['Owner','Shipper','Captain','Investor']:
			enslaver_role=getuniqueorcreatenew(
				EnslaverRole.objects.all().filter(name=enslaver_role_name),
				EnslaverRole(name=enslaver_role_name)
			)
			enslaver_roles[enslaver_role_name]=enslaver_role

		##step 1A: captains and vessel owners ('investors') from the voyages table, corresponding with the voyages in this sheet
		with open('voyages/apps/past/management/commands/texas_enslaved.csv',encoding='utf-8-sig') as csvfile:
			reader = csv.DictReader(csvfile)
			sheet_voyage_ids=[]
			for row in reader:
				voyage_id=noblank(row['VOYAGEID'],"int")
				sheet_voyage_ids.append(voyage_id)

		sheet_voyage_ids=list(set(sheet_voyage_ids))

		sheet_voyages=[noblank(list(v for v in allvoyages.filter(voyage_id=vi))) for vi in sheet_voyage_ids]
		shipownernames={}
		shipcaptainnames={}

		for voy in sheet_voyages:
			shipowners=[vsoc.owner for vsoc in VoyageShipOwnerConnection.objects.all().filter(voyage=voy) if vsoc.owner.name is not None]
			shipcaptains=[vcc.captain for vcc in VoyageCaptainConnection.objects.all().filter(voyage=voy) if vcc.captain.name is not None]
			for shipowner in shipowners:
				shipownername=shipowner.name
				if shipownername in shipownernames:
					shipownernames[shipownername].append(voy)
				else:
					shipownernames[shipownername]=[voy]
			for shipcaptain in shipcaptains:
				shipcaptainname=shipcaptain.name
				if shipcaptainname in shipcaptainnames:
					shipcaptainnames[shipcaptainname].append(voy)
				else:
					shipcaptainnames[shipcaptainname]=[voy]
		
		role=enslaver_roles['Investor']
		for enslavername in shipownernames:
			enslaver_identity=EnslaverIdentity(
				id=enslaver_identity_pk_ai,
				principal_alias=enslavername
			)
			enslaver_identity.save()
			enslaver_alias=EnslaverAlias(
				id=enslaver_alias_pk_ai,
				identity=enslaver_identity,
				alias=enslavername,
				manual_id="Texas_"+str(enslaver_alias_pk_ai)
			)
			enslaver_alias.save()
			
			ecp=EnslaverCachedProperties(identity=enslaver_identity,enslaved_count=0)
			ecp.save()
			enslaver_identity_pk_ai+=1
			enslaver_alias_pk_ai+=1
			for voy in shipownernames[enslavername]:
				enslaver_voyage_connection=EnslaverVoyageConnection(
					enslaver_alias=enslaver_alias,
					role=role,
					voyage=voy
				)
				enslaver_voyage_connection.save()
				enslavervoyageconnections.append(enslaver_voyage_connection)
		
		role=enslaver_roles['Captain']
		for enslavername in shipcaptainnames:
			enslaver_identity=EnslaverIdentity(
				id=enslaver_identity_pk_ai,
				principal_alias=enslavername
			)
			enslaver_identity.save()
			enslaver_alias=EnslaverAlias(
				id=enslaver_alias_pk_ai,
				identity=enslaver_identity,
				alias=enslavername,
				manual_id="Texas_"+str(enslaver_alias_pk_ai)
			)
			enslaver_alias.save()
			
			ecp=EnslaverCachedProperties(identity=enslaver_identity,enslaved_count=0)
			ecp.save()
			enslaver_identity_pk_ai+=1
			enslaver_alias_pk_ai+=1
			for voy in shipcaptainnames[enslavername]:
				enslaver_voyage_connection=EnslaverVoyageConnection(
					enslaver_alias=enslaver_alias,
					role=role,
					voyage=voy
				)
				enslaver_voyage_connection.save()
				enslavervoyageconnections.append(enslaver_voyage_connection)
		
		print("%d captain names" %len(shipcaptainnames))
		print("%d captain & owner aliases" %len(shipownernames))
		print("%d captain & owner voyage connections" %len(enslavervoyageconnections))

		##step 1B: enslavers with direct enslavement connections
		##THIS IS VERY SIMPLE RIGHT NOW. IT ASSUMES UNIQUE NAMES FOR ALL ENSLAVERS WHOSE ALIASES HAVE "TEXAS" IN THEIR MANUAL ID FIELD.
		##IT DOES NOT WRITE NEW DATA TO THESE ENSLAVERS IF THEY EXIST (BECAUSE OUR BIOGRAPHICAL DATA ON THEM RIGHT NOW IS MINIMAL)
		##BUT IT DOES CREATE NEW ALIAS AND IDENTITY OBJECTS AS NEEDED ON THE BASIS OF THE UNIQUE NAME CONSTRAING -- AND THEN LINK THEM


		with open('voyages/apps/past/management/commands/texas_enslaved.csv',encoding='utf-8-sig') as csvfile:

			reader = csv.DictReader(csvfile)
		
			enslavernames=[]
			captains_voyages={}
			enslavercolumnnames=['Shipper','Owner A','Owner B']


			for row in reader:
				for ecn in enslavercolumnnames:
					enslavernames.append(row[ecn])
	
			enslavernames=[i for i in list(set(enslavernames)) if i!='']
# 			captain_names=[i for i in list(set(captain_names)) if i!='']
		
			for enslavername in enslavernames:
				enslaver_identity=getuniqueorcreatenew(
					texas_enslaver_identities.filter(aliases__alias=enslavername),
					EnslaverIdentity(
						id=enslaver_identity_pk_ai,
						principal_alias=enslavername
					)
				)
			
				enslaver_alias=getuniqueorcreatenew(
					texas_enslaver_aliases.filter(alias=enslavername),
					EnslaverAlias(
						id=enslaver_alias_pk_ai,
						identity=enslaver_identity,
						alias=enslavername,
						manual_id="Texas_"+str(enslaver_alias_pk_ai)
					)
				)
				ecp=EnslaverCachedProperties(identity=enslaver_identity,enslaved_count=0)
				enslavercachedproperties.append(ecp)
			
				enslaver_aliases[enslavername]=enslaver_alias
				enslaver_identities[enslavername]=enslaver_identity
				enslaver_identity_pk_ai+=1
				enslaver_alias_pk_ai+=1
			print("%d enslaver identities" %len(enslaver_identities))
			print("%d enslaver aliases" %len(enslaver_aliases))


		##step 2: sources
		sourcecolumnnames=['SOURCEA','SOURCEB']
		sources={}
		with open('voyages/apps/past/management/commands/texas_enslaved.csv',encoding='utf-8-sig') as csvfile:
			tmp_sources=[]
			reader = csv.DictReader(csvfile)
			#very basic -- the first letters before the comma.
			#Erik Engquist: when you think you've solved a problem with regular expressions, you've got three problems
			#for instance, what I should really be doing here is insisting that the script stops if a good matching source can't be found
			#because the source format for the texas data assumes that there is already a good matching source in the db
			for row in reader:
				for scn in sourcecolumnnames:
					entry=row[scn]
					if entry!='':
						shortref=re.search("[^,]+",row[scn]).group(0)
						tmp_sources.append(shortref)
			tmp_sources=list(set(tmp_sources))
			db_sources=VoyageSources.objects.all()
			for short_ref in tmp_sources:
				this_source=getuniqueorcreatenew(
					db_sources.filter(short_ref=short_ref),
					VoyageSources(
						short_ref=short_ref,
						source_type_id=1,
						full_ref=short_ref
					)
				)
		# 				print(this_source)
				sources[short_ref]=this_source

		print("%d sources" %len(sources))
		
		##step 3: enslaved
		enslaveds={}
		enslavedsourceconnections=[]
		captivefates={}
		captivefatenamesdict={97:'Embarked, subsequent fate unknown'}
		places=Place.objects.all()
		with open('voyages/apps/past/management/commands/texas_enslaved.csv',encoding='utf-8-sig') as csvfile:

			reader = csv.DictReader(csvfile)

			enslaved=Enslaved.objects.all()

			for row in reader:
				enslavement_sources=[row[i] for i in sourcecolumnnames if row[i]!='']
				tmp_sources={}
				for enslavement_source in enslavement_sources:
					shortref=re.search("[^,]+",enslavement_source).group(0)
					leftover=enslavement_source[len(shortref)+2:]
					tmp_sources[shortref]={"obj":sources[shortref],"text_ref":leftover}

				captive_fate_id=row['Captive fate']
				if captive_fate_id != '':
		
					captive_fate_id=int(captive_fate_id)
					captive_fate_name=captivefatenamesdict.get(captive_fate_id) or "Unknown Value"
		
					captive_fate=getuniqueorcreatenew(
						CaptiveFate.objects.all().filter(id=captive_fate_id),
						CaptiveFate(
							id=captive_fate_id,
							name=captive_fate_name
						)
					)
					captivefates[captive_fate_id]=captive_fate
		
				else:
					captive_fate=None



				enslaved_id=int(row['ID'])
				last_known_location=noblank(places.filter(value=noblank(row['Last known loction'],'int')))
				voyage_id=noblank(row['VOYAGEID'],"int")
				voyage=noblank(list(v for v in allvoyages.filter(voyage_id=voyage_id)))
				age=noblank(row['Age'],'int')
				gender=noblank(row['Sex'],'int')
				height=noblank(row['Height in inches'],'float')
				skin_color=noblank(row['Racial descriptor'])
				captive_name=noblank(row['Captive name'],blank=True)
				enslaved_person=getuniqueorcreatenew(
					enslaved.filter(enslaved_id=enslaved_id),
					Enslaved(
						enslaved_id=enslaved_id,
						documented_name=captive_name,
						age=age,
						captive_fate=captive_fate,
						gender=gender,
						height=height,
						skin_color=skin_color,
						voyage=voyage,
						dataset=1
					)
				)
			
				c=1
			
				for shortref in tmp_sources:
					source=tmp_sources[shortref]
					enslavedsourceconnection=EnslavedSourceConnection(
						enslaved=enslaved_person,
						source=source['obj'],
						source_order=c,
						text_ref=source['text_ref']
					)
					c+=1
					enslavedsourceconnections.append(enslavedsourceconnection)
			
				enslaveds[enslaved_id]=enslaved_person
	
		print("%d enslaved" %len(enslaveds))
		print("%d enslaved source connections" %len(enslavedsourceconnections))

		##4. relations
		enslavement_relations=[]
		enslaver_in_relations=[]
		enslaved_in_relations=[]
	
		enslavement_relation_types={}
	
		for enslavement_relation_type_name in ['Ownership','Transportation']:
		
			enslavement_relation_type=getuniqueorcreatenew(
				EnslavementRelationType.objects.all().filter(name=enslavement_relation_type_name),
				EnslavementRelationType(name=enslavement_relation_type_name)
			)
		
			enslavement_relation_types[enslavement_relation_type_name]=enslavement_relation_type
		enslavementrelation_pk_ai=max(EnslavementRelation.objects.all().values_list('id'))[0]+1
		enslaverinrelation_pk_ai=max(EnslaverInRelation.objects.all().values_list('id'))[0]+1
		enslavedinrelation_pk_ai=max(EnslavedInRelation.objects.all().values_list('id'))[0]+1
	
		with open('voyages/apps/past/management/commands/texas_enslaved.csv',encoding='utf-8-sig') as csvfile:

			reader = csv.DictReader(csvfile)
			for row in reader:

				enslaved_id=int(row['ID'])
				enslaved_person=enslaveds[enslaved_id]
			
				day=str(row['Day of manifest'])
				month=str(row['Month of manifest'])
				year=str(row['Year of manifest'])
			
				if len(day)==1:
					day="0"+day
				if len(month)==1:
					month="0"+month
			
				relation_date=','.join([month,day,year])
			
				owner_names=list(set([row[i] for i in ['Owner A','Owner B'] if row[i]!='']))
				if len(owner_names)>0:
				
					enslavement_relation_type=enslavement_relation_types['Ownership']
					enslaver_role=enslaver_roles['Owner']
					for owner_name in owner_names:
						enslavement_relation=EnslavementRelation(
							id=enslavementrelation_pk_ai,
							relation_type=enslavement_relation_type,
							date=relation_date
						)
						enslavement_relations.append(enslavement_relation)
						enslavementrelation_pk_ai+=1
						enslaver_in_relation=getuniqueorcreatenew(
							EnslaverInRelation.objects.all().filter(enslaver_alias=enslaver_aliases[owner_name],relation=enslavement_relation,role=enslaver_role),
							EnslaverInRelation(id=enslaverinrelation_pk_ai,enslaver_alias=enslaver_aliases[owner_name],relation=enslavement_relation,role=enslaver_role)
						)
						enslaverinrelation_pk_ai+=1
						enslaver_in_relations.append(enslaver_in_relation)
					
						enslaved_in_relation=getuniqueorcreatenew(
							EnslavedInRelation.objects.all().filter(enslaved=enslaved_person,relation=enslavement_relation),
							EnslavedInRelation(id=enslavedinrelation_pk_ai,enslaved=enslaved_person,relation=enslavement_relation)
						)
						enslavedinrelation_pk_ai+=1
						enslaved_in_relations.append(enslaved_in_relation)
			
				shipper_names=list(set([row[i] for i in ['Shipper'] if row[i]!='']))
				voyage_id=noblank(row['VOYAGEID'],"int")
				voyage=noblank(list(v for v in allvoyages.filter(voyage_id=voyage_id)))
				for shipper_name in shipper_names:

					enslavement_relation_type=enslavement_relation_types['Transportation']
					enslavement_relation=EnslavementRelation(
						id=enslavementrelation_pk_ai,
						relation_type=enslavement_relation_type,
						date=relation_date,
						voyage=voyage
					)
					enslavement_relations.append(enslavement_relation)
					enslavementrelation_pk_ai+=1
					
					
					enslaver_alias=enslaver_aliases[shipper_name]
					enslaver_role=enslaver_roles["Shipper"]
				
					enslaver_in_relation=getuniqueorcreatenew(
						EnslaverInRelation.objects.all().filter(enslaver_alias=enslaver_alias,relation=enslavement_relation,role=enslaver_role),
						EnslaverInRelation(id=enslaverinrelation_pk_ai,enslaver_alias=enslaver_alias,relation=enslavement_relation,role=enslaver_role)
					)
					enslaverinrelation_pk_ai+=1
					enslaver_in_relations.append(enslaver_in_relation)
					
					enslaved_in_relation=getuniqueorcreatenew(
						EnslavedInRelation.objects.all().filter(enslaved=enslaved_person,relation=enslavement_relation),
						EnslavedInRelation(id=enslavedinrelation_pk_ai,enslaved=enslaved_person,relation=enslavement_relation)
					)
					enslavedinrelation_pk_ai+=1
					enslaved_in_relations.append(enslaved_in_relation)
	
		print("%d enslavement relations" %len(enslavement_relations))
		print("%d enslaver in relations" %len(enslaver_in_relations))
		print("%d enslaved in relations" %len(enslaved_in_relations))
		print("%d enslaver roles" %len(enslaver_roles))

		itemlists=[
			captivefates,
# 			sources,
			enslaveds,
			enslavedsourceconnections,
			enslavement_relations,
			enslaver_roles,
			enslaver_identities,
			enslaver_aliases,
			enslaver_in_relations,
			enslaved_in_relations,
			enslavercachedproperties
		]

		for itemlist in itemlists:

			if type(itemlist)==list and len(itemlist)>0:
				print("importing objects like this-->",itemlist[0])
				for item in itemlist:
					try:
						item.save()
					except:
						print(item.__dict__)
		
			elif type(itemlist)==dict and len(itemlist)>0:
				print("importing objects like this-->",itemlist[list(itemlist.keys())[0]])
				for k in itemlist:
					try:
						itemlist[k].save()
					except:
						print(print(k,itemlist[k].__dict__))


