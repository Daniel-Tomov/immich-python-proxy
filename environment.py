config = {
  "ipp": {
    "IMMICH_URL": "http://192.168.55.179:2283",
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
    "customInvalidResponse": 'https://danieltomov.com'
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

