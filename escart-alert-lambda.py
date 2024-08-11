import json
import urllib3
import hmac
import hashlib
import base64
import urllib.parse
import http.client
import asyncio
import time
import traceback
from datetime import datetime, timedelta
import hashlib

ACCESS_TOKEN="5db796fd683375146086da10ad2f0265c182411965f118e4cffc4100281a822c"
SIGN_SEC = "SEC4a30d38b89fe83b6f751a4fbefc76f7e49b1b7411edfcf072d1c758c37aa0125"
LAMBDA_SECURITY_TOKEN = "HzpMyJ5Ypntk9cuT7l58bXOEpF8erKLfNzEFNKblyUyij6R9eJqzFzYKlEUwGDtcJ7"
LAMBDA_FUNC_URL = "https://vcuhua4ufknky5zetllsawxf2a0xwaxj.lambda-url.ap-southeast-1.on.aws"

OPENSEARCH_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
OPENSEARCH_URL = """
https://opensearch.automation.dana.id/app/data-explorer/discover#?_a=
(discover:(columns:!(kubernetes.deployment.name,message,_source),isDirty:!t,sort:!()),metadata:(indexPattern:'92dba400-8ea5-11ee-a56a-355d088e94d1',view:discover))&_g=(filters:!(),refreshInterval:(pause:!t,value:0),
time:(from:'{TIMESTAMP_FROM}',to:'{TIMESTAMP_TO}'))
&_q=(filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'92dba400-8ea5-11ee-a56a-355d088e94d1',key:kubernetes.deployment.name.keyword,negate:!f,params:!(ticket-event-receiver-consumer-v1,ticket-event-receiver-v1,comment-event-receiver-v1,comment-public-event-receiver-consumer-v1,comment-private-event-receiver-consumer-v1,comment-private-event-receiver-experimental-consumer-v1,auto-replier-general-consumer-v1,auto-replier-outbound-consumer-v1,auto-replier-dlq-consumer-v1,auto-replier-facebook-public-consumer-v1),type:phrases,value:'ticket-event-receiver-consumer-v1,%20ticket-event-receiver-v1,%20comment-event-receiver-v1,%20comment-public-event-receiver-consumer-v1,%20comment-private-event-receiver-consumer-v1,%20comment-private-event-receiver-experimental-consumer-v1,%20auto-replier-general-consumer-v1,%20auto-replier-outbound-consumer-v1,%20auto-replier-dlq-consumer-v1,%20auto-replier-facebook-public-consumer-v1'),query:(bool:(minimum_should_match:1,should:!((match_phrase:(kubernetes.deployment.name.keyword:ticket-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:ticket-event-receiver-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-event-receiver-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-public-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-private-event-receiver-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:comment-private-event-receiver-experimental-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-general-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-outbound-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-dlq-consumer-v1)),(match_phrase:(kubernetes.deployment.name.keyword:auto-replier-facebook-public-consumer-v1)))))),('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'92dba400-8ea5-11ee-a56a-355d088e94d1',key:query,negate:!f,type:custom,value:'%7B%22match%22:%7B%22message%22:%2240116314%22%7D%7D')
,{ADDITIONAL_QUERY}query:(language:kuery,query:''))
""".strip().replace("\n", "")

loop = asyncio.get_event_loop()


def lambda_handler(event, context):
    return loop.run_until_complete(main(event, context))

async def main(event, context):
    raw_path = event.get("rawPath", "/")
    raw_query_str = event.get("rawQueryString", "")

    print("raw path:  ", raw_path)
    if raw_path.count("/") >= 3:
        ret = handle_redirect_url(raw_path)
        print("redirect ", ret)
        return ret
    if event['headers'].get('security-token') != LAMBDA_SECURITY_TOKEN:
        return {
            'statusCode': 401,
            'body': "missing security header"
        }

    try:
        """
        Expect opensearch sent-body (message):
        {{#toJson}}ctx.results{{/toJson}}
        """
        print(event['body'])
        # TODO implement
        loaded = json.loads(event['body'])

        print("SENDING TO DINGTALK")
        response = send_dingtalk_message(await preprocess_body(loaded))
        print("Response  ", response)

        return {
            'statusCode': 200,
            'body': event,
            'response': response,
        }
    except Exception as e:
        response = send_dingtalk_message(event['body'])
        print("ERROR2 ", response,  traceback.format_exception(e))
        return {
            'statusCode': 200,
            # "body": json.dumps(event['body']) + "\n\n\n" + traceback.format_exception(e)
        }


def handle_redirect_url(raw_path):
    _, timestamp_from, timestamp_to, ticket_id, *comment_id = raw_path.split("/")
    comment_id = comment_id[0] if len(comment_id) > 0 else None

    ADDITIONAL_QUERY = [
        f"query:(match:(message:'{ticket_id}')))),",
        f"query:(match:(message:'{comment_id}'))))," if comment_id is not None else "",
    ]
    url = OPENSEARCH_URL.format(TIMESTAMP_FROM=timestamp_from, TIMESTAMP_TO=timestamp_to,
                                ADDITIONAL_QUERY="".join(ADDITIONAL_QUERY))
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

    ret.append(f"Total log error:  {total_value}")
    ret.append("")
    ret.append("")

    tasks = []

    hits = hits["hits"]
    for logg in hits:
        msg_parser = MessageParser(logg['_source']['message'], logg['_source']['@timestamp'])
        tasks.append(asyncio.create_task(msg_parser.repr()))

    for task in tasks:
        # ret.append(f"{logg['_source']['kubernetes']['deployment']['name']}")
        ret.append(await task)
        ret.append("")
    ret = "\n".join(map(str, ret))
    print(ret)
    return ret


class MessageParser:
    def __init__(self, msg, opensearch_timestamp):
        self.opensearch_timestamp = opensearch_timestamp
        self.opensearch_datetime = datetime.strptime(opensearch_timestamp, OPENSEARCH_TIME_FORMAT)
        if msg.count(" ; ") <= 3:
            self.timestamp = self.severity = self.file = self.module = self.log_type = ""
            self.func = self.ticket_id = self.comment_id = self.scope = ""
            self.msg = msg
            return

        (self.timestamp, self.severity, self.file, self.module,
         self.func, self.ticket_id, self.comment_id, *remaining)  = msg.split(" ; ", 9)
        if not self.comment_id.isalnum():
            self.comment_id = None
        if len(remaining) == 3:
            self.scope, self.log_type, self.msg = remaining
        elif len(remaining) == 2:
            scope = "-"
            self.log_type, self.msg = remaining
        elif len(remaining) == 1:
            self.msg = remaining[0]

    async def get_opensearch_url(self, filter_by_comm_id=False):
        if filter_by_comm_id and self.comment_id is None:
            return None

        delta = timedelta(minutes=4)
        from_ =(self.opensearch_datetime - delta).strftime(OPENSEARCH_TIME_FORMAT)
        to = (self.opensearch_datetime + delta).strftime(OPENSEARCH_TIME_FORMAT)

        url = f"{LAMBDA_FUNC_URL}/{from_}/{to}/{self.ticket_id}"
        if filter_by_comm_id:
            url = f"{LAMBDA_FUNC_URL}/{from_}/{to}/{self.comment_id}"

        shorten_prefix="comment-log-" if filter_by_comm_id else "ticket-log-"
        print(shorten_prefix, url)
        return await shorten_url_async(url, default_value=url, shorten_prefix=shorten_prefix)


    async def repr(self):
        url_1 = asyncio.create_task(self.get_opensearch_url())
        url_2 = asyncio.create_task(self.get_opensearch_url(True))

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
{self.msg}
        """.strip()


def remove_none_and_join(arr, sep="\n"):
    new_arr = [i for i in arr if i is not None]
    return sep.join(map(str, new_arr))


def shorten_url(target_url, shorten_prefix, default_value=None):
    api = "https://www.ristek.link/api/shorten"
    http = urllib3.PoolManager()

    for retry in range(1, 15):
        hash_object = hashlib.sha256(input_string.encode(target_url + str(retry)))
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
        print("RETRY  ", shorten_prefix, retry)
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



def send_dingtalk_message(message):
    # Generate the timestamp and signature
    timestamp, signature = generate_dingtalk_signature(SIGN_SEC)

    # Construct the webhook URL with the signature and timestamp
    webhook_url = (
        f"https://oapi.dingtalk.com/robot/send?access_token={ACCESS_TOKEN}"
        f"&timestamp={timestamp}&sign={signature}"
    )

    # Create the message payload
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "at": {
            "isAtAll": False
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
            'body': json.loads(response_data)
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