from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from pysnmp.entity.rfc3413.oneliner import cmdgen
import statistics
import time
import requests
import json
from .forms import lbdn
import operator

#enabling the SNMP module
cmdGen = cmdgen.CommandGenerator()

#requests WAPI call and returns output as a list
def get_wapi_call(ip,username,password,wapi_object):
	try:
		requests.packages.urllib3.disable_warnings()
		base_url = "https://{}/wapi/v2.10/".format(ip)
		url = base_url + wapi_object
		response = requests.request("GET", url, auth=(username,password), verify = False)
		js = json.loads(response.text)	
		#return js
	except: 
		return redirect("http://127.0.0.1:8000/main/")
	else:
		return js

#polls the selected parameters by their OID through SNMP
def polling(ip):
	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
	cmdgen.CommunityData('public'),
	cmdgen.UdpTransportTarget((ip, 161)),
	'1.3.6.1.4.1.2021.10.1.3.1',
	)

	for name, val in varBinds:
		return str(val)

#login page
def main_lbdn(request):
	global username, password, IP_Address          #username, password and IP address of the grid member where the DTC service is hosted
	context={}
	context['form'] = lbdn()
	if request.GET:
		username = request.GET['username']
		password = request.GET['password']
		IP_Address = request.GET['IP_Address']
		print(IP_Address)
		return redirect('http://127.0.0.1:8000/infoblox/')
	return render(request, 'core/main.html', context)

#lbdn selection page
def infoblox(request):
	try:
		global l,lb                                                  #l is the mapping list of all LBDN's with pools. lb contains the selected LBDN
		requests.packages.urllib3.disable_warnings()
		geodata1 = get_wapi_call(IP_Address,username,password, 'dtc:lbdn?_return_fields%2B=auth_zones,health,lb_method,name,patterns,types,pools') 

		l = []
		for i in range(0,len(geodata1)):
			l.append({geodata1[i]['name'] : [] })
			for j in range(0,len(geodata1[i]['pools'])):
				k = (geodata1[i]['pools'][j]['pool']).split(':')
				(l[i][geodata1[i]['name']]).append(k[2])
		
		for i in geodata1:
			for j in i['pools']:
				k = j['pool'].split(':')
				j['pool'] = k[2]
			for u in range(0,len(i['auth_zones'])):
				m = i['auth_zones'][u].split(':')
				i['auth_zones'][u] = m[1]

		if request.GET:
			lb = request.GET['lbdn']
			#print(lb)
			return redirect('http://127.0.0.1:8000/pool/')
	except:
		return redirect("http://127.0.0.1:8000/main/")
	else:	
		return render(request,'core/infoblox.html', {
			'lbdn' : geodata1,
		})


#pool parameters selection view
def pool(request):
	try:
		global p,geo,yas,ras,pl,re
		requests.packages.urllib3.disable_warnings()
		p =[]          #this will contain names of the pools uns=der the selected LBDN

		for i in l:
			for k in i:
				if(k == lb):
					p.append({'pools' : i[k]})
		print(p)

		geo = []          #this will contain pool data w.r.t. the selected LBDN

		for i in p[0]['pools']:
			url5 = "https://{}/wapi/v2.10/dtc:pool?_return_fields%2B=availability,health,lb_preferred_method,monitors,name&name={}".format(IP_Address,i)
			response5 = requests.request("GET",url5, auth=(username,password), verify=False)
			geodata5 = json.loads(response5.text)
			geo.append(geodata5)

		for t in geo:
			for s in t:
				for u in range(0,len(s['monitors'])):
					m = s['monitors'][u].split(':')
					s['monitors'][u] = m[3]


		#next section is getting pool "refrence" for POST and PUT REST calls
		geodata2 = get_wapi_call(IP_Address,username,password, 'dtc:pool?_return_fields%2B=availability,health,lb_preferred_method,monitors,name,servers')
		pas = get_wapi_call(IP_Address,username,password,"dtc:lbdn?_return_fields%2B=pools")
		xas = []         
		ras = ""

		for i in range(0,len(pas)):
			if(pas[i]['name'] == lb):
				xas = pas[i]['pools'] 
				ras = pas[i]['_ref']
		yas = str(xas).replace("\'","\"")


		geodata1 = get_wapi_call(IP_Address,username,password,"dtc:lbdn?_return_fields%2B=auth_zones,health,lb_method,name,patterns,types,pools")
		geodata3  = get_wapi_call(IP_Address,username,password,"dtc:server?_return_fields%2B=auto_create_host_record,health,host,name")

		#some mappings to retrieve the data in the required formatting

		consolidated_pool = {}
		for i in range(0,len(geodata2)):
			consolidated_pool[geodata2[i]['name']] = []
			for j in range(0,len(geodata2[i]['servers'])):
				consolidated_pool[geodata2[i]['name']].append(geodata2[i]['servers'][j]['server'])

		consolidated_server = {}
		for i in range(0,len(geodata3)):
			consolidated_server[geodata3[i]['name']] = []
			consolidated_server[geodata3[i]['name']].append(geodata3[i]['host'])

		mapping = {}           #mappings for pools w.r.t. servers, IP address and CPU utils 
		for i in consolidated_pool:
			mapping[i] = []
			for j in range(0,len(consolidated_pool[i])):
				x = consolidated_pool[i][j].split(':')
				for k in consolidated_server:
					if(k==x[2]):
						x = polling(consolidated_server[k][0])
						mapping[i].append((k,consolidated_server[k],x))


		fin = {}                        #CPU utils at the servers
		for i in mapping:
			fin[i] = []
			for j in mapping[i]:
				fin[i].append(float(j[2]))

		
		final = {}                   #consolidated CPU Util at the pools
		for i in fin:
			final[i] = statistics.mean(fin[i])



		ratio_pool = {}                #storing the initial ratios os the pools
		for i in range(0,len(geodata1)):
			if(geodata1[i]['name'] == lb):
				for j in geodata1[i]['pools']:
					j['pool'] = (j['pool'].split(':'))[2]
					ratio_pool[j['pool']] = j['ratio']


		poll = []                      #pool details for dsplaying in the fieldset
		for k in final:
			if(k in p[0]['pools']):
				poll.append({'name' : k, 'cpu' : final[k], 'ratio': ratio_pool[k] })
		print(poll)

		if request.GET:
			pl = request.GET['threshold']	       #stores the threshold entered by the user	
			re = request.GET['restart']	
			return redirect('http://127.0.0.1:8000/dtc/')
	except:
		return redirect('http://127.0.0.1:8000/main/')
	else:

		return render(request,'core/pool.html', {
			'pool' : geo,
			'poll' : poll,
		})

#the monitoring view
def dtc(request):
	requests.packages.urllib3.disable_warnings()
	geodata1 = get_wapi_call(IP_Address,username,password,"dtc:lbdn?_return_fields%2B=auth_zones,health,lb_method,name,patterns,types,pools")
	geodata2  = get_wapi_call(IP_Address,username,password,"dtc:pool?_return_fields%2B=availability,health,lb_preferred_method,monitors,name,servers")
	geodata3  = get_wapi_call(IP_Address,username,password,"dtc:server?_return_fields%2B=auto_create_host_record,health,host,name")

	#g_lbdn, g_pool, g_server is formatted data to be displayed as table contents on the webpage
	g_lbdn = []

	for i in geodata1:
		if(i['name']) == lb:
			g_lbdn.append(i)

	for i in g_lbdn:
		for j in range(0,len(i['auth_zones'])):
			k = i['auth_zones'][j].split(':')
			i['auth_zones'][j] = k[1]
		for j in i['pools']:
			k = j['pool'].split(':')
			j['pool'] = k[2]

	g_pool = []
	for i in geodata2:
		if(i['name'] in p[0]['pools']):
			g_pool.append(i)

	for s in g_pool:
		for u in range(0,len(s['monitors'])):
			m = s['monitors'][u].split(':')
			s['monitors'][u] = m[3]


	#consolidated results for reference during polling the servers
	consolidated_lbdn = {}
	for i in range(0,len(geodata1)):
		consolidated_lbdn[geodata1[i]['name']] = []
		for j in range(0,len(geodata1[i]['pools'])):
			consolidated_lbdn[geodata1[i]['name']].append(geodata1[i]['pools'][j]['pool'])


	consolidated_pool = {}
	for i in range(0,len(geodata2)):
		consolidated_pool[geodata2[i]['name']] = []
		for j in range(0,len(geodata2[i]['servers'])):
			consolidated_pool[geodata2[i]['name']].append(geodata2[i]['servers'][j]['server'])

	consolidated_server = {}
	for i in range(0,len(geodata3)):
		consolidated_server[geodata3[i]['name']] = []
		consolidated_server[geodata3[i]['name']].append(geodata3[i]['host'])

	h = []
	for i in p[0]['pools']:
		if i in consolidated_pool:
			for j in consolidated_pool[i]:
				k = j.split(':')
				h.append(k[2])

	g_server = []
	for i in geodata3:
		if(i['name'] in h):
			g_server.append(i)

	#loop to continously poll the CPU's and consolidate at the pool level.
	#also to change the ratios dynamically as and when required

	while(True):

		ratio_pool = {}
		call = get_wapi_call(IP_Address,username,password,"dtc:lbdn?_return_fields%2B=pools")
		for val in range(0,len(geodata1)):
			if(call[val]['name'] == lb):
				for val2 in geodata1[val]['pools']:
					ratio_pool[val2['pool']] = val2['ratio']

		mapping = {}
		for i in consolidated_pool:
			mapping[i] = []
			for j in range(0,len(consolidated_pool[i])):
				x = consolidated_pool[i][j].split(':')
				
				for k in consolidated_server:
					if(k==x[2]):
						x = polling(consolidated_server[k][0])
						mapping[i].append((k,consolidated_server[k],x))

		print(mapping)
		print("Consolidated Pool Results")
		fin = {}
		for i in mapping:
			fin[i] = []
			for j in mapping[i]:
				fin[i].append(float(j[2]))
		print(fin)

		global final                     #final consolidated retults at the pool level
		final = {}
		stat = ['remark','update']
		for i in fin:
			if(i in p[0]['pools']):
				final[i] = round(statistics.mean(fin[i]),2)
		print(final)

		change = 0

		for i in final:
			if(final[i] >= int(pl)):
				change = 1
			else:
				continue

		#check the ratios and modify dynamically as and when required
		if(change == 1):	
			ratio(final)            #for updating the ratios when CPU Utilization crosses the threshold
			print("New ratios")
			stat[0] = "CPU Utilization exceeded the Threshold"
			stat[1] = "Modifying Pool Ratios"
			flag = 'RED'
			restart()       

		else:
			data = "{\"lb_method\": \"RATIO\", \"name\": \""+lb+"\", \"pools\": "+yas+"}"
			print(data)
			header = {'content-type': "application/json"}
			url = "https://{}/wapi/v2.10/{}?_return_fields%2B=name,pools".format(IP_Address,ras)
			response = requests.request("PUT", url , auth=(username,password), data = data, headers=header, verify=False)   #for resetting the ratios when the CPU Utilization is within the limits
			print(response)
			print("Old ratios")
			stat[0] = "CPU Utilization within the Threshold"
			stat[1] = "Pool Ratios Maintained"
			flag = 'GREEN'
			restart()

		print("Final Answer")
		print(final)

		sol = []            #formatted list for displaying contents on the webpage
		for key in mapping:
			if(key in p[0]['pools']):
				temp_list = []
				for i in mapping[key]:
					temp_dict = {'name': i[0] , 'host' : i[1] , 'cpu' : i[2]}
					temp_list.append(temp_dict)
				sol.append({'pool' : key , 'server' : temp_list , 'cpu' : final[key], 'pool_ratio' : ratio_pool[key] })
		
		
		#print(sol)

		print("____________________________________________")
		time.sleep(1)


		return render(request, 'core/dtc.html', {
			'dtclbdn' : g_lbdn,
			'dtcpool': g_pool,
			'dtcserver': g_server,
			'pool' : geo,
			'resu' : sol,
			'statement' : stat,
			'flag' : flag,

		})


#function for ratio modification at the pool level
def ratio(final):
	p = get_wapi_call(IP_Address,username,password,"dtc:lbdn?_return_fields%2B=pools")
	x = []
	r = ""
	for i in range(0,len(p)):
		if(p[i]['name'] == lb):
			x = p[i]['pools'] 
			r = p[i]['_ref']

	print(x)

	rat = calculate(x,final)

	for i in range(0,len(x)):
		for j in rat:
			for k,v in j.items():
				if(k in x[i]['pool']):
					x[i]['ratio'] = int(v) 

	print(x)

	ans = str(x).replace("\'","\"")
	print("ans")
	print(ans)

	data = "{\"lb_method\": \"RATIO\", \"name\": \""+lb+"\", \"pools\": "+ans+"}"
	#print(data)
	header = {'content-type': "application/json"}
	url = "https://{}/wapi/v2.10/{}?_return_fields%2B=name,pools".format(IP_Address,r)
	#print(url)
	response = requests.request("PUT", url , auth=(username,password), data = data, headers=header, verify=False)
	print(response)


#logic to find optimum ratios for the pool having CPU utilization stored in variable - "final"
def calculate(p,final):
	ratios = []
	pools = {}

	for i in p:
		temp = {}	
		temp['pool'] = i['pool']
		temp['pool'] = (temp['pool'].split(':'))[2]
		pools[temp['pool']] = i['ratio']

	cpu_dict = dict(sorted(final.items() , key = operator.itemgetter(1), reverse=False))
	print("cpu cpu_dict")
	print(cpu_dict)
	pools_dict = dict(sorted(pools.items() , key = operator.itemgetter(1), reverse=True))
	print("pools_dict")
	print(pools_dict)
	reference_ratio = list(pools_dict.values())
	print("reference_ratio")
	print(reference_ratio)

	count = 0
	for k,v in cpu_dict.items():
		ratios.append({k : reference_ratio[count]}) 
		count = count + 1

	print(ratios)
	return ratios



#restart functionality for the grid when the ratios are updated
def restart():
	a = get_wapi_call(IP_Address,username,password,"grid")
	ref = []
	for i in range(0,int(len(a))):
		ref.append(a[i]['_ref'])

	data = "{\"member_order\" : \"SIMULTANEOUSLY\", \"service_option\": \"ALL\"}"
	header = {'content-type': "application/json"}
	url= "https://{}/wapi/v2.10/{}?_function=restartservices".format(IP_Address,ref[0])

	response = requests.request("POST", url , auth=(username,password), data = data, headers=header, verify=False)
	print(response)

