#!/usr/bin/python

import json
import logging
import urllib
import urllib2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LIFECYCLE_KEY = "LifecycleHookName"
ASG_KEY = "AutoScalingGroupName"
EC2_KEY = "EC2InstanceId"

url_auth = "https://URL"
url_api = "https://URL/api_jsonrpc.php"
user_api = "USER"
pass_api = "PASSWORD"
user_htaccess = "USER" 
pass_htaccess = "PASSWORD


def lambda_handler(event, context):
    try:
        logger.info(json.dumps(event))
        message = event['detail']
        if LIFECYCLE_KEY in message and ASG_KEY in message:
            life_cycle_hook = message[LIFECYCLE_KEY]
            auto_scaling_group = message[ASG_KEY]
            instance_id = message[EC2_KEY]
            host = instance_id
            token = get_token()
            host_id = get_host_id(token,host)
            disable_host(token,host_id)
            logger.info("Disable instance: "+instance_id)
    except Exception, e:
        logging.error("Error: %s", str(e))

def zabbix_api(url_api,payload):
    passManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passManager.add_password(None, url_auth, user_htaccess, pass_htaccess)
    handler = urllib2.HTTPBasicAuthHandler(passManager)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    req = urllib2.Request(url_api, payload.encode(), {"Content-type":"application/json"})
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

def get_host_id(token,host):
    payload_get_host_id = json.dumps(
	{
    	    "jsonrpc": "2.0",
    	    "method": "host.get",
    	    "params": {
	        "output": ["hostid"],
                "filter": {
                    "host": [
                        ""+host+"" 
                 ]
                 }
            },
            "id": 2,
            "auth": ""+token+""
    }).encode()
    get_host_id_req = zabbix_api(url_api,payload_get_host_id)
    return get_host_id_req[0]['hostid']



def disable_host(token,hostid):
    payload_disable_host = json.dumps(
  	{
   	    "jsonrpc": "2.0",
   	    "method": "host.update",
   	    "params": {
      	    "hostid": ""+hostid+"",
      	    "status": 1
   	    },
   	    "auth": ""+token+"",
   	    "id": 4
  	}).encode()
    get_dis_req = zabbix_api(url_api,payload_disable_host)
    return get_dis_req
