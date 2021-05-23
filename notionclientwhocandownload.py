from notion.client import NotionClient

from requests import get
import time
import os
from zipfile import ZipFile
class NotionClientWhoCanDownload(NotionClient):
    def _get_task_id(self, response):
        """
        When you export a file, notion creates a task to make the file with the 'enqueueTask' endpoint.
        Then another method looks at the task ID and returns the file when the task finishes.
        So, we need to save the taskId into a variable. This is a helper function to do that.
        """
        return response.json()['taskId']

    # Source from https://requests.readthedocs.io/en/master/user/quickstart/#raw-response-content
    def _download_url(self, url, save_path, chunk_size=128):
        """
        Downloads the zip file and saves it to a file.
        url - string of the url from which to download.
        save_path - string of the file name to output the zip file into.
        chunk_size = size of the chunk. This is adjustable. See the documentation for more info.
        """
        r = get(url, stream=True)
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

    def _unzip_file(self, file, delete=True):
        """
        Helper function to unzip the zipped download.
        file - string of the zip file name
        delete - delete the zip file or not.
        """
        with ZipFile(file) as zipObj:
            zipObj.extractall()
        if delete:
            os.remove(file)

    def download_block(
        self,
        block_id: str,
        path: str,
        recursive: bool = False,
        export_type: str = "markdown",
        time_zone: str = "America/Chicago",
        locale: str = "en",
    ):
        """
        Download block.

        TODO: Add support for downloading a list of blocks.


        Arguments
        ---------
        block_id : str
            ID of the block.

        recursive : bool, optional
            Whether or not to include sub pages.
            Defaults to False.

        export_type : str
            Type of the output file.
            The options are "markdown", "pdf", "html".
            Defaults to "markdown".

        time_zone : str, optional
            I don't know what values go here. I'm in the Chicago
            timezone (central) and this is what I saw in the request.
            Defaults to "America/Chicago".
            TODO: test? hard code?

        locale : str, optional
            Locale for the export.
            Defaults to "en".
        """
        data = {
            "task": {
                "eventName": "exportBlock",
                "request": {
                    "blockId": block_id,
                    "recursive": recursive,
                    "exportOptions": {
                        "exportType": export_type,
                        "timeZone": time_zone,
                        "locale": locale,
                    },
                },
            }
        }

        if export_type in ["pdf", "html"]:
            data["task"]["request"]["exportOptions"]["pdfFormat"] = "Letter"

        def fetch():
            time.sleep(0.1)
            return self.post("getTasks", {"taskIds": task_ids}).json()

        task_ids = [self.post("enqueueTask", data).json()["taskId"]]
        task = fetch()

        # Ensure that we're getting the data when it's ready.
        while "status" not in task["results"][0]:
            print(task["results"])
            task = fetch()

        while "exportURL" not in task["results"][0]["status"]:
            task = fetch()

        url = task["results"][0]["status"]["exportURL"]
        self._download_url(url, path)