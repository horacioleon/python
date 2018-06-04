import urllib
import urllib2
import json
import requests
import time
import datetime
import logging

def zabbix_api(url,payload):
	req = urllib2.Request(url, payload.encode(), {"Content-type":"application/json"})
	response = urllib2.urlopen(req)
	output_json = json.loads(response.read())
	output_func = output_json['result']
	return output_func


def get_token():
	payload_auth = json.dumps(
	{
	    "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                          "user": ""+user_api+"",
                          "password": ""+pass_api+""
                      },
            "id": 1 
        }).encode()
	auth_token = zabbix_api(url_api,payload_auth)
	return auth_token



def get_host_from_group(token,groupid):
        payload_get_host_from_group = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["hostid"],
		"selectHosts": "extended",
                "filter": { "groupid": [ ""+groupid+"" ]  }
            },
            "id": 2,
            "auth": ""+token+""
        }).encode()
        get_host_from_group_req = zabbix_api(url_api,payload_get_host_from_group)
        return get_host_from_group_req[0]['hosts']


def get_decommissioned(token,hostid):
        payload_get_decommissioned_time = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "host.get",
	    "params": {
                "output": ["date_hw_decomm"],
                "filter": { "hostid": [ ""+hostid+"" ] },
		"selectInventory": ["date_hw_decomm"]
            },
            
	    "auth": ""+token+"",
            "id": 3
        }).encode()
        get_time_req = zabbix_api(url_api,payload_get_decommissioned_time)
        return get_time_req

def delete_host(token,hostid):
	payload_delete_host = json.dumps(
	{
    	    "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [
                ""+hostid+""
    		      ],
            "auth": ""+token+"",
            "id": 4
	}).encode()
	get_del_req = zabbix_api(url_api,payload_delete_host)
	return get_del_req


url_api = "http://$SERVER/api_jsonrpc.php"
user_api = "$API_USER"
pass_api = "$API_PASSWORD"

token = get_token()
group_id="$GROUP_ID DISABLED HOST"
hosts_deleted = 0
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', filename='/var/log/zabbix/zabbix_deleted_hosts.log',level=logging.DEBUG)
retention = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%s')
saida = get_host_from_group(token,group_id)

for i  in saida:
	host_id = i['hostid']
	date_hw_decomm =  float(get_decommissioned(token,host_id)[0]['inventory']['date_hw_decomm'])
	if date_hw_decomm > float(retention):
		delete_host(token,host_id)
		hosts_deleted = hosts_deleted + 1

if hosts_deleted == 0:
	logging.info("No hosts were deleted")
