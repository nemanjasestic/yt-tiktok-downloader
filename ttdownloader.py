import requests

class snaptik:
    def __init__(self, url):
        self.url = url
        self.video = self._get_video()

    def _get_video(self):
        api = "https://api.tikmate.app/api/lookup"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {"url": self.url}
        response = requests.post(api, headers=headers, data=payload)
        result = response.json()
        return f"https://tikmate.app/download/{result['token']}/{result['id']}.mp4"
