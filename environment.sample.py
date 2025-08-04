config = {
  "ipp": {
    "IMMICH_URL": "http://localhost:2283",
    "responseHeaders": {
      "Cache-Control": "public, max-age=2592000",
      "Access-Control-Allow-Origin":  "*"
    },
    "singleImageGallery": False, # TODO
    "singleItemAutoOpen": True,  # TODO
    "downloadOriginalPhoto": True, # doesn't matter if lightGallery.download is False or if downloading is diabled in Immich
    "allowDownloadAll": True,
    "showHomePage": True,
    "showGalleryTitle": True,
    "showGalleryDescription": True,
    'downloadAllChunkSize': 2**32, # change to bigger value to possibly increase downloadAll speeds
    'videoChunkSize': 2**11, # change to bigger value if videos buffer 
    "showMetadata": {
      "description": False # TODO
    },
    "customInvalidResponse": 'https://google.com'
  },
  "lightGallery": {
    "controls": True,
    "download": False,
    "mobileSettings": {
      "controls": False,
      "showCloseIcon": True,
      "download": False
    }
  }
}

API_URL = config['ipp']['IMMICH_URL']
items_per_page = 35
customInvalidResponse = config["ipp"]['customInvalidResponse']

