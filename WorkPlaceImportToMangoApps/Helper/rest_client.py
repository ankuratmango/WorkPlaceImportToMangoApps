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

# # Example usage:
# if __name__ == "__main__":
#     api_client = RestClient("https://jsonplaceholder.typicode.com", headers={"Content-Type": "application/json"})

#     # GET request
#     response = api_client.get("/posts", params={"userId": 1})
#     print("GET Response:", response.json())

#     # POST request
#     response = api_client.post("/posts", json={"title": "foo", "body": "bar", "userId": 1})
#     print("POST Response:", response.json())

#     # PUT request
#     response = api_client.put("/posts/1", json={"id": 1, "title": "foo", "body": "bar", "userId": 1})
#     print("PUT Response:", response.json())

#     # DELETE request
#     response = api_client.delete("/posts/1")
#     print("DELETE Response Status Code:", response.status_code)
