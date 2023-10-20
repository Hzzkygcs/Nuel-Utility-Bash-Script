import json
import requests
import cmd

URL = "https://api-loctool.loc.staging-traveloka.com/api/v2/holiday/"
SERVICE_TOKEN_LOCTOOLS = "eyJraWQiOiJZWGN4ektWdXQwXC9wWWhRcjlLMUcrRGZIclpYTVprd2J3Y1kyR3dBc09BST0iLCJhbGciOiJSUzI1NiJ9.eyJodHRwczpcL1wvdHZsa1wvcGVybWlzc2lvbnMiOiJbXCJ2OnZhY2F0aW9uXCIsXCJkOm5lcmRvY3VtZW50XCIsXCJ2OmhvbGlkYXlcIixcInY6bG5kbWtTcmNcIixcInY6bG5kbWtcIixcInY6c3RyZWV0U3JjXCIsXCJ2OnVuaXZzZWFyY2hcIixcInY6c3JzcGxhdGZvcm1cIixcInc6bG5kbWtfc291cmNpbmdcIixcImM6c3RyZWV0XCIsXCJyZWFkOmFsbFwiLFwidjpnZW9cIixcImU6dW5pdnNlYXJjaFwiLFwidjpzdHJlZXRcIixcImU6c3RyZWV0XCIsXCJ2OnVuaXZzZWFyY2hQQUdcIixcImM6YXByXCIsXCJyOmFwclwiLFwiZTpsbmRta1wiLFwiZTpzdHJlZXRTcmNcIixcImM6bG5kbWtcIixcImU6Z2VvXCIsXCJlOmFwclwiXSIsImF0X2hhc2giOiJCQVVIekNrZG9MTTFweW96SEtneWpRIiwiaHR0cHM6XC9cL3R2bGtcL2dyb3VwcyI6IltcIkxvY2FsIEVuZ2luZWVyXCJdIiwic3ViIjoiN2MzZmEyMDQtMDQxOC00ZDIyLTk5NDctM2NhZmZmMDkyY2IxIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTFfY2t5bHMwbGoyIiwiY29nbml0bzp1c2VybmFtZSI6IjM0MTc2YWU1LWM5NzktNGU3Yy1hNzgwLTllOGEyNjA0Zjc5ZCIsImh0dHBzOlwvXC90dmxrXC9jb21wcmVzc2lvbi1tZXRob2QiOiJub25lIiwibm9uY2UiOiJaMVEzTVU4d1QyMTVTVXhWU1ZWTGJXWjJVVWx4Ym01blJVVjROMmN5ZDFjM2IzaEpUWEZSUkV3MFpRPT0iLCJvcmlnaW5fanRpIjoiYmQ0YmFmMjMtMmFhOC00MjZmLWI1ZWMtNGU4NWQ3YmRkNWU3IiwiYXVkIjoiN2RnbnFpZWNiYjZvbW45M2xtM3A4NGlrcSIsImlkZW50aXRpZXMiOlt7InVzZXJJZCI6IjEwNDM4MTQzNDcxMDI3NTU3OTQ0NSIsInByb3ZpZGVyTmFtZSI6Ikdvb2dsZSIsInByb3ZpZGVyVHlwZSI6Ikdvb2dsZSIsImlzc3VlciI6bnVsbCwicHJpbWFyeSI6ImZhbHNlIiwiZGF0ZUNyZWF0ZWQiOiIxNjk0NjgyNTQxNTI0In1dLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY5NzUzMDk2MCwibmFtZSI6IkltbWFudWVsIEltbWFudWVsIiwiZXhwIjoxNjk3NTM0NTYwLCJpYXQiOjE2OTc1MzA5NjEsImp0aSI6IjZhOTFjZGRmLTU3MTItNDFhOC1iNGI4LTFkMTNjYjFmN2VkZCIsImVtYWlsIjoidC1pbW1hbnVlbC5pbW1hbnVlbEB0cmF2ZWxva2EuY29tIn0.iECxaf9OMInHiiEFiFoKzbIpdkKjN9OKDadQ4HcJspRqCJdy2kLVw1QA7jj47ro2H3Rlk0ZelM5052RZfU6G3GZbX2S3m1AprTNwgzZBlAEbZ9QPn6X6cSrPMXYJTbbRadCMpgULqHqy05kaho8MUMo1TYPOWk_txdPbadozoz_7HM8IuuQcUHBkO898h_BpAjbNvb-osznJkRhYHqtethEfWJGK6iSW9GCuX5vh_kL6YaQskJdPxgddSYRjlP_s5tAmPf1T8nlw5gOUTAD9jvXHPbE0oC3MVH78DFAx2c9QP_swYwUlBv3Z3rfWQ72SFyPebuiD6ebv6OFnh5uF-w"


class CmdParse(cmd.Cmd):
    prompt = '> '
    commands = []
        
    def default(self, line):
        # Write your code here by handling the input entered
        exit_code, output = run_command(
            line
        )
        print("Exit code:", exit_code)
        print()
        print(output)

    def do_exit(self, line):
        return True


def main():
    CmdParse().cmdloop()



def clear():
    print("\n" * 30)


def run_command(command):
    result = RequestMaker(SERVICE_TOKEN_LOCTOOLS, URL).sendreq("execute", {
            "bashCommand": command
        },)
    return result['exitCode'], result['output']



class RequestMaker:
    def __init__(self, authToken, baseUrl):
        self.authToken = authToken
        self.baseUrl = baseUrl
        self.headers = {
            "origin": "https://loctool.loc.staging-traveloka.com"
        }

    def sendreq(self, url, data):
        response = requests.post(self.baseUrl + url, json={
            "clientInterface": "desktop",
            "context": {
                "authServiceToken": self.authToken
            },
            "data": data,
            "fields": []
        }, headers=self.headers)
        if "data" not in response.json():
            print(response.json())
        return response.json()["data"]
    


if __name__ == "__main__":
    main()
