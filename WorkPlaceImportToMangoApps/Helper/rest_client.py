import requests

class RestClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = kwargs.pop('headers', {})
        headers.update(self.headers)

        response = requests.request(method, url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response: {response.text}")
            raise

        return response

    def get(self, endpoint, params=None, headers=None):
        return self._make_request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint, data=None, json=None, headers=None):
        return self._make_request("POST", endpoint, data=data, json=json, headers=headers)

    def put(self, endpoint, data=None, json=None, headers=None):
        return self._make_request("PUT", endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint, headers=None):
        return self._make_request("DELETE", endpoint, headers=headers)

    def patch(self, endpoint, data=None, json=None, headers=None):
        return self._make_request("PATCH", endpoint, data=data, json=json, headers=headers)

    def download_image(self, image_url, filepath):
        image_data = requests.get(image_url, stream=True)
        if image_data.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in image_data:
                    f.write(chunk)
                    print("Downloading....")
        return filepath

    def upload_file(self, token, image_url, filepath):
        headers = {
          'Content-Type': 'application/json',
          'Cookie': "_felix_session_id=" + token,
        }

        url = image_url
        file_path = filepath
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            return response

        print(response.json())