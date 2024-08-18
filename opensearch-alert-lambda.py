import json
import re
import os
from ast import literal_eval
import urllib3
import hmac
import hashlib
import base64
import urllib.parse
from pprint import pformat
import http.client
import asyncio
import time
import traceback
from datetime import datetime, timedelta
import hashlib

ACCESS_TOKEN="5db796fd683375146086da10ad2f0265c182411965f118e4cffc4100281a822c"
SIGN_SEC = "SEC4a30d38b89fe83b6f751a4fbefc76f7e49b1b7411edfcf072d1c758c37aa0125"

ACCESS_TOKEN_PROD = "f7bb91833b87b49f4b143c03be565a1bb40db4573d7ca67fdc72a947cd6d64d3"
SIGN_SEC_PROD = "SEC074490029488db92eb803f031836e197a6d33b573a8be088b3b842379e5c3690"

LAMBDA_SECURITY_TOKEN = "HzpMyJ5Ypntk9cuT7l58bXOEpF8erKLfNzEFNKblyUyij6R9eJqzFzYKlEUwGDtcJ7"
LAMBDA_FUNC_URL = "https://vcuhua4ufknky5zetllsawxf2a0xwaxj.lambda-url.ap-southeast-1.on.aws"

OPENSEARCH_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
OPENSEARCH_URL = """
https://opensearch.automation.dana.id/app/data-explorer/discover#?_a=(discover:(columns:!(kubernetes.deployment.name,message,_source),isDirty:!t,sort:!()),metadata:(indexPattern:'92dba400-8ea5-11ee-a56a-355d088e94d1',view:discover))
&_g=(filters:!(),refreshInterval:(pause:!t,value:0),
time:(from:'{TIMESTAMP_FROM}',to:'{TIMESTAMP_TO}'))
&_q=(filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'92dba400-8ea5-11ee-a56a-355d088e94d1',key:kubernetes.deployment.name.keyword,negate:!f,params:!(ticket-event-receiver-consumer-v1,ticket-event-receiver-v1,comment-event-receiver-v1,comment-public-event-receiver-consumer-v1,comment-private-event-receiver-consumer-v1,comment-private-event-receiver-experimental-consumer-v1,auto-replier-general-consumer-v1,auto-replier-outbound-consumer-v1,auto-replier-dlq-consumer-v1,auto-replier-facebook-public-consumer-v1),type:phrases,value:'ticket-event-receiver-consumer-v1,%20ticket-event-receiver-v1,%20comment-event-receiver-v1,%20comment-public-event-receiver-consumer-v1,%20comment-private-event-receiver-consumer-v1,%20comment-private-event-receiver-experimental-consumer-v1,%20auto-replier-general-consumer-v1,%20auto-replier-outbound-consumer-v1,%20auto-replier-dlq-consumer-v1,%20auto-replier-facebook-public-consumer-v1'),query:(bool:(minimum_should_match:1,should:!((match_phrase:(kubernetes.deployment.name.keyword:ticket-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:ticket-event-receiver-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-event-receiver-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-public-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-private-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-private-event-receiver-experimental-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-general-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-outbound-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-dlq-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-facebook-public-consumer-v1))))))
{ADDITIONAL_QUERY}
),query:(language:kuery,query:''))
""".strip().replace("\n", "")


def get_opensearch_url_with_exclude(filter_by: list[str], TIMESTAMP_FROM="", TIMESTAMP_TO="", exclude_words=None):
    if exclude_words is None:
        exclude_words = []

    conditions = []
    for condition in filter_by:
        conditions.append(f",('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'92dba400-8ea5-11ee-a56a-355d088e94d1',key:query,negate:!f,type:custom,value:'%7B%22match%22:%7B%22message%22:%22{condition}%22%7D%7D'),query:(match:(message:{condition})))")
    for condition in exclude_words:
        conditions.append(f",('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'92dba400-8ea5-11ee-a56a-355d088e94d1',key:query,negate:!f,type:custom,value:'%7B%22bool%22:%7B%22must_not%22:%7B%22match_phrase%22:%7B%22message%22:%22{condition}%22%7D%7D%7D%7D'),query:(bool:(must_not:(match_phrase:(message:{condition})))))")
    conditions = "".join(conditions)
    return OPENSEARCH_URL.format(ADDITIONAL_QUERY=conditions, TIMESTAMP_FROM=TIMESTAMP_FROM, TIMESTAMP_TO=TIMESTAMP_TO)


loop = asyncio.get_event_loop()


def lambda_handler(event, context):
    return loop.run_until_complete(main(event, context))

def is_prod():
    return os.environ.get("prod", 0) == "1"

async def main(event, context):
    raw_path = event.get("rawPath", "/")
    raw_query_str = event.get("rawQueryString", "")
    print("raw_query_str  ", raw_query_str)

    access_token, sign_token = ACCESS_TOKEN, SIGN_SEC
    if is_prod():
        access_token, sign_token = ACCESS_TOKEN_PROD, SIGN_SEC_PROD

    print("raw path:  ", raw_path)
    if raw_path.count("/") >= 3:
        ret = handle_redirect_url(raw_path)
        print("redirect ", ret)
        return ret
    if 'Records' in event:
        for record in event['Records']:
            message_body = json.loads(record['body'])
            if message_body['auth'] != LAMBDA_SECURITY_TOKEN:
                print("ERROR NOT AUTHENTICATED:  ", message_body)
                continue
            await handle_queue_message(message_body['body'], access_token, sign_token)
        return
    if event['headers'].get('security-token') != LAMBDA_SECURITY_TOKEN:
        return {
            'statusCode': 401,
            'body': "missing security header"
        }
    body = event["body"]
    body = json.loads(body) if isinstance(event['body'], str) else body
    if 'auth' in body:  # convert sqs-format to HTTP-POST format
        body = body['body']
    return await handle_queue_message(body, access_token, sign_token)


async def handle_queue_message(body, access_token, sign_token):
    try:
        """
        Expect opensearch sent-body (message) FOR POST REQUEST:
        {{#toJson}}ctx.results{{/toJson}}
        
        OR THROUGH API GATEWAY -> SQS -> This Lambda:
        {
            "auth": "HzpMyJ5Ypntk9cuT7l58bXOEpF8erKLfNzEFNKblyUyij6R9eJqzFzYKlEUwGDtcJ7",
            "deduplicationId":  "0{{#toJson}}ctx.results.0.hits.hits.0.fields.@timestamp.0{{/toJson}}",
            "body": {{#toJson}}ctx.results{{/toJson}}
        }
        
        """
        print(body)
        # TODO implement
        loaded = json.loads(body) if isinstance(body, str) else body

        print("SENDING TO DINGTALK")
        bbody, urgency, total_value  = await preprocess_body(loaded)
        response = send_dingtalk_message(bbody, access_token, sign_token, urgency > 0)

        if urgency > 0:
            for i in range(urgency):
                time.sleep(2)
                send_dingtalk_message(f"{total_value} errors occurred. Please respond"+" "*i, access_token, sign_token, False)

        print("Response  ", response)
        print("body  ", type(bbody).__name__)

        return {
            'statusCode': 200,
            'body': body,
            'response': response,
        }
    except Exception as e:
        if is_prod():
            print("ERROR2 PROD. Proceed No Longer. ",  traceback.format_exception(e))
            access_token, sign_token = ACCESS_TOKEN, SIGN_SEC
        response = send_dingtalk_message(body, access_token, sign_token)
        print("ERROR2 ", response,  traceback.format_exception(e))
        return {
            'statusCode': 200,
            # "body": json.dumps(event['body']) + "\n\n\n" + traceback.format_exception(e)
        }



def handle_redirect_url(raw_path):
    _, timestamp_from, timestamp_to, *filter_by = raw_path.split("/")

    includes = []
    excludes = []
    for i in filter_by:
        if len(i) == 0:
            continue
        if i.startswith("-"):
            excludes.append(i[1:])
            continue
        includes.append(i)

    url = get_opensearch_url_with_exclude(includes, TIMESTAMP_FROM=timestamp_from, TIMESTAMP_TO=timestamp_to,
                                          exclude_words=excludes)
    # return {"statusCode": 200, "body": url}
    return {
        "headers": {"Location": url, },
        "statusCode": 302,
    }


async def preprocess_body(loaded: list[dict]):
    if len(loaded) == 0:
        print("WARNING loaded empty where it shouldn't be empty")
        return "WARNING loaded empty where it shouldn't be empty"
    ret = []
    hits = loaded[0]["hits"]
    total_value = hits["total"]["value"]
    print("total_value", total_value)

    ret.append(f"Total error logs:  {total_value}")
    urgency = min(3, total_value // 10)
    for _ in range(urgency):
        ret[0] += f"\nTotal error logs:  {total_value}"

    tasks = []

    hits = hits["hits"]
    sent_messages = set()
    for logg in hits:
        msg_parser = MessageParser(logg['_source']['message'], logg['_source']['@timestamp'])
        if msg_parser.hash() in sent_messages:
            continue
        sent_messages.add(msg_parser.hash())
        tasks.append(asyncio.create_task(msg_parser.repr()))

    for task in tasks:
        # ret.append(f"{logg['_source']['kubernetes']['deployment']['name']}")
        ret.append(await task)
    ret = "\n\n===========================\n\n".join(map(str, ret))
    return ret, urgency, total_value


class MessageParser:
    def __init__(self, msg, opensearch_timestamp):
        self.opensearch_timestamp = opensearch_timestamp
        self.opensearch_datetime = datetime.strptime(opensearch_timestamp, OPENSEARCH_TIME_FORMAT)
        if msg.count(" ; ") <= 3:
            self.timestamp = self.severity = self.file = self.module = self.log_type = ""
            self.func = self.ticket_id = self.comment_id = self.scope = ""
            self.msg = msg
            return

        (self.timestamp, self.severity, self.file, self.module, self.func, *remaining)  = msg.split(" ; ", 9)

        self.ticket_id, self.comment_id, self.scope, self.log_type, self.msg = fill_left(remaining, 5, '')
        if not self.comment_id.isalnum():
            self.comment_id = None


    async def get_opensearch_url(self, only_include_error_log=False):
        delta = timedelta(minutes=4)
        from_ =(self.opensearch_datetime - delta).strftime(OPENSEARCH_TIME_FORMAT)
        to = (self.opensearch_datetime + delta).strftime(OPENSEARCH_TIME_FORMAT)

        url = f"{LAMBDA_FUNC_URL}/{from_}/{to}/{self.ticket_id}/{self.comment_id}"
        if only_include_error_log:
            url = f"{url}/ERROR/-INFO"

        shorten_prefix="error-log-" if only_include_error_log else "all-log-"
        # print(shorten_prefix, url)
        return await shorten_url_async(url, default_value=url, shorten_prefix=shorten_prefix)

    def hash(self):
        return hash(self.msg)

    async def repr(self):
        url_1 = asyncio.create_task(self.get_opensearch_url())
        url_2 = asyncio.create_task(self.get_opensearch_url(True))
        message = get_literals(self.msg)
        print(repr(message))

        return f"""
Timestamp:  {self.opensearch_timestamp}
Severity:   {self.severity}
Location:   {self.file} - {self.module} - {self.scope}
Ticket ID:  {self.ticket_id}
https://dana.zendesk.com/agent/tickets/{self.ticket_id}
Comment ID: {self.comment_id}
Misc Info:  {(self.scope)} {self.log_type}  
{remove_none_and_join([await url_1, await url_2])}
Msg:
{array_to_pretty_printed(message)}
        """.strip()


def fill_left(tuplee, target_num_of_item: int, fill_value=None):
    if len(tuplee) >= target_num_of_item:
        return tuplee
    ret = (fill_value,) * (target_num_of_item - len(tuplee)) + tuple(tuplee)
    return ret


def remove_none_and_join(arr, sep="\n"):
    new_arr = [i for i in arr if i is not None]
    return sep.join(map(str, new_arr))


def shorten_url(target_url, shorten_prefix, default_value=None):
    api = "https://www.ristek.link/api/shorten"
    http = urllib3.PoolManager()

    for retry in range(1, 15):
        hash_object = hashlib.sha256((target_url + str(retry)).encode())
        hex_digest = hash_object.hexdigest()
        shorten_url = f"{shorten_prefix}{hex_digest[-5:]}"

        response = http.request('POST', api, body={"shorten": shorten_url, "url" : target_url})
        response_data = response.read().decode('utf-8')
        if response.status == 200 or "Try creating a shortened URL" in response_data:
            return f"ristek.link/{shorten_url}"
    return default_value


async def shorten_url_async(target_url, shorten_prefix, default_value=None):
    api_host = "www.ristek.link"
    api_path = "/api/shorten"

    for retry in range(1, 3):
        # Generate the SHA-256 hash and get the last 5 hex digits
        hash_object = hashlib.sha256(f"{target_url}{retry}".encode())
        hex_digest = hash_object.hexdigest()
        shorten_url = f"{shorten_prefix}{hex_digest[-5:]}"

        # Asynchronously send the POST request
        conn = http.client.HTTPSConnection(api_host)
        headers = {"Content-Type": "application/json", "User-Agent": "PostmanRuntime/7.37.3", "Accept" : "*/*", "Connection": "keep-alive"}
        body = json.dumps({"shorten": shorten_url, "url": target_url})

        response = await loop.run_in_executor(
            None, lambda: conn.request("POST", api_path, body=body, headers=headers)
        )

        response = await loop.run_in_executor(None, conn.getresponse)
        response_data = response.read().decode("utf-8")
        print(response.status, shorten_url, response_data, target_url)

        if response.status == 200 or "Try creating a shortened URL" in response_data:
            conn.close()
            return f"https://ristek.link/{shorten_url}"

        conn.close()

    return default_value



def send_dingtalk_message(message, access_token, sign_token, mention_all=False):
    # Generate the timestamp and signature
    timestamp, signature = generate_dingtalk_signature(sign_token)

    # Construct the webhook URL with the signature and timestamp
    webhook_url = (
        f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"
        f"&timestamp={timestamp}&sign={signature}"
    )

    # Create the message payload
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "at": {
            "isAtAll": mention_all
        },
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    data = json.dumps(payload).encode('utf-8')

    # Send the POST request
    http = urllib3.PoolManager()
    try:
        response = http.request('POST', webhook_url, body=data, headers=headers)
        response_data = response.read().decode('utf-8')
        return {
            'statusCode': response.status,
            'body': response_data
        }
    except Exception as e:
        return {
            'body': f"{e}"
        }



def generate_dingtalk_signature(secret):
    # Get the current timestamp in milliseconds
    timestamp = str(round(time.time() * 1000))

    # Create the string to sign
    string_to_sign = f'{timestamp}\n{secret}'

    # Create the HMAC-SHA256 signature
    secret_enc = secret.encode('utf-8')
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()

    # Encode the signature in Base64
    sign = base64.b64encode(hmac_code).decode('utf-8')

    # URL encode the signature
    sign = urllib.parse.quote_plus(sign)

    return timestamp, sign


def array_to_pretty_printed(arr: list, separator="  "):
    ret = []
    for item in arr:
        if isinstance(item, str):
            ret.append(item)
            continue
        is_traceback_log = isinstance(item, list) and len(item) > 0 and (
                "Traceback" in item[0] or ("File" in item[0] and "line" in item[0]))
        if is_traceback_log:
            ret.append("\n" + "".join(item))
            continue
        ret.append(pformat(item))
    return separator.join(ret)


def get_literals(string: str):
    pair_mapping = {
        "{": "}",
        "[": "]",
        "'": "'",
        '"': '"',
        "(": ")",
    }

    evaluated = []
    curr_substring_start = 0

    pattern  = re.compile("\\[|\\(|\\{|\"|'")
    for match in pattern.finditer(string):
        start = match.start()
        if start < curr_substring_start:
            continue

        found = match.group()
        pair = pair_mapping[found]
        for next_potential_ending in find_iter(string, pair, start=start+1):
            next_potential_ending = next_potential_ending+1
            substring = string[start:next_potential_ending]
            try:
                result = literal_eval(substring)
                end = next_potential_ending
                if curr_substring_start < end:
                    evaluated.append(string[curr_substring_start: start])
                    curr_substring_start = end+1
                evaluated.append(result)
            except:
                pass
    end = len(string)
    if curr_substring_start < end:
        evaluated.append(string[curr_substring_start:])
    return evaluated



def find_iter(string, find, start=0):
    for index, char in enumerate(string[start:], start=start):
        if char == find:
            yield index
    return