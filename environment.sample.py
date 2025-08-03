config = {
  "ipp": {
    "IMMICH_URL": "http://localhost:2283",
    "responseHeaders": {
      "Cache-Control": "public, max-age=2592000",
      "Access-Control-Allow-Origin":  "*"
    },
    "singleImageGallery": False,
    "singleItemAutoOpen": True,
    "downloadOriginalPhoto": True,
    "allowDownloadAll": 1,
    "showHomePage": True,
    "showGalleryTitle": True,
    "showGalleryDescription": True,
    "showMetadata": {
      "description": False
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

