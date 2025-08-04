from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context
)
from requests import get

from utils import error_404, get_url, post_url, invalidResponse
from environment import items_per_page, config

allowed_url_types = ['share', 's']

class Share:
    def __init__(self, app:Flask):
        self.app = app
        self.register_routes()
        
    def single_image_album(self, url_type:str, share_id:str, key_or_slug:str, me:Response) -> Response:
        asset = me['assets'][0]
        if me['allowDownload']: # if the downloading is not enabled for the share, ignore environment.py
            allowDownloadAll = config['ipp']['allowDownloadAll']
            showMetadata = True
        elif me['showMetadata']:
            showMetadata = True
            allowDownloadAll = False
        else:
            allowDownloadAll = False # ignore Immich album config if disabled in environment.py
            showMetadata = False
        lgInit = self.add_lg_config()[0]
        
        if asset['type'] == "IMAGE":
            image_urls = [self.add_image_urls(url_type, share_id, asset['id'], me['allowDownload'])]
            lgInit += self.add_lg_image(url_type, share_id, asset['id'])
        else: # video
            image_urls = [self.add_video_urls(url_type, share_id, asset['id'], me['allowDownload'])]
            lgInit += self.add_lg_video(url_type, share_id, asset['id'])
            
        lgInit += self.add_lg_config()[1]
        return render_template('share.html', paths=image_urls, share_id=share_id, album_thumbnail=asset['id'], lgInit=lgInit, url_type=url_type, allowDownloadAll=allowDownloadAll, items_per_page=items_per_page)
    
    def add_lg_config(self) -> str:
        lg_config = [
            '{"lgConfig":{"controls":' + str(config['lightGallery']['controls']).lower() + ',"download":',
            ']}'
        ]
        lg_config[0] += str(config['lightGallery']['download']).lower()    
        lg_config[0] += ',"mobileSettings":{"controls":' + str(config['lightGallery']['mobileSettings']['controls']).lower() + ',"showCloseIcon":' + str(config['lightGallery']['mobileSettings']['showCloseIcon']).lower() + ',"download":'
        lg_config[0] += str(config['lightGallery']['mobileSettings']['download']).lower()
        lg_config[0] += '}},"items":['
        
        if config['ipp']['showMetadata']['description'] == 0:
            ""
        return lg_config
    
    def add_image_urls(self, url_type:str, share_id:str, id:str, allowDownload:bool) -> dict:
        r = {
                'type': 'photo',
                'thumb': f'/{url_type}/photo/{share_id}/{id}/thumbnail',
                'preview': f'/{url_type}/photo/{share_id}/{id}/preview',
            }
        if allowDownload and config['ipp']['downloadOriginalPhoto']:
                r['original'] = f'/{url_type}/photo/{share_id}/{id}/fullsize'
        else:
            r['original'] = r['preview']
            
        return r
    def add_lg_image(self, url_type:str, share_id:str, id:str) -> str:
        return '{"html":"<a href=\\\"/'+ url_type + '/photo/' + share_id + '/' + id + '/preview\\\" data-download-url=\\\"/' + url_type + '/photo/' + share_id + '/' + id + '/original\\\"><img alt=\\\"\\\" src=\\\"/' + url_type + '/photo/' + share_id + '/' + id + '/thumbnail\\\"/></a>","thumbnailUrl":"/' + url_type + '/photo/' + share_id + '/' + id + '/thumbnail"},'
        
    def add_video_urls(self, url_type:str, share_id:str, id:str, allowDownload:bool) -> dict:
        r = {
                'type': 'video',
                'thumb': f'/{url_type}/video/{share_id}/{id}/thumbnail',
                'video': f'/{url_type}/video/{share_id}/{id}',
                'original': f'/{url_type}/video/{share_id}/{id}/original',
            }
        
        if allowDownload and config['ipp']['downloadOriginalPhoto']:
                r['original'] = f'/{url_type}/photo/{share_id}/{id}/fullsize'
        else:
            r['original'] = r['video']
        return r
        
    def add_lg_video(self, url_type:str, share_id:str, id:str) -> str:
        return "{\"html\":\"<a data-video='{\\\"source\\\":[{\\\"src\\\":\\\"/" + url_type + "/video/" + share_id + "/" + id + "\\\",\\\"type\\\":\\\"video/mp4\\\"}],\\\"attributes\\\":{\\\"playsinline\\\":\\\"playsinline\\\",\\\"controls\\\":\\\"controls\\\"}}' data-download-url=\\\"/" + url_type + "/photo/" + share_id + "/" + id + "/original\\\"><img alt=\\\"\\\" src=\\\"/" + url_type + "/photo/" + share_id + "/" + id + "/thumbnail\\\"/><div class=\\\"play-icon\\\"></div></a>\",\"thumbnailUrl\":\"/" + url_type + "/photo/" + share_id + "/" + id + "/thumbnail\"},"
    
    def key_or_slug(self, url_type:str) -> str:
        if url_type == "share":
            return 'key' # key for auto-generated URL
        else:
            return 'slug' # slug for custom URL

    def register_routes(self):        
        @self.app.route("/<string:url_type>/<string:share_id>", methods=["GET"])
        def share(url_type:str, share_id:str):
            if url_type not in allowed_url_types:
                return error_404()
            
            key_slug = self.key_or_slug(url_type)
            
            me = get_url(f'/api/shared-links/me?{key_slug}={share_id}').json()
            if 'message' in me and me['message'] == f'Invalid share {key_slug}':
                return invalidResponse()
            
            if me['type'] == "INDIVIDUAL": # single image album
                return self.single_image_album(url_type, share_id, key_slug, me)
            
            album_id = me['album']['id']
            if config['ipp']['showGalleryTitle']:
                album_name = me['album']['albumName']
            else:
                album_name = ""
            
            if config['ipp']['showGalleryDescription']:
                album_desc = me['album']['description']
            else:
                album_desc = ""
                
            album_thumbnail = me['album']['albumThumbnailAssetId']
            lgInit = self.add_lg_config()[0]
            
            if me['allowDownload']: # if the downloading is not enabled for the share, ignore environment.py
                allowDownloadAll = config['ipp']['allowDownloadAll']
                showMetadata = True
            elif me['showMetadata']:
                showMetadata = True
                allowDownloadAll = False
            else:
                allowDownloadAll = False # ignore Immich album config if disabled in environment.py
                showMetadata = False
            
            buckets = get_url(f'/api/timeline/buckets?albumId={album_id}&{key_slug}={share_id}&order=desc').json()

            image_urls = []
            
            # individual bucket : /api/timeline/bucket?albumId=<albumid>&key=<shareid>&order=desc&timeBucket=<somedate>
            for bucket in buckets:
                items_in_bucket = get_url(f'/api/timeline/bucket?albumId={album_id}&{key_slug}={share_id}&order=desc&timeBucket={bucket['timeBucket']}').json()
                for item_idx in range(0, bucket['count']):
                    if items_in_bucket['isImage'][item_idx]: 
                        if len(image_urls) < items_per_page:
                            image_urls.append(self.add_image_urls(url_type, share_id, items_in_bucket['id'][item_idx], me['allowDownload']))
                        lgInit += self.add_lg_image(url_type, share_id, items_in_bucket['id'][item_idx])
                    else:
                        if len(image_urls) < items_per_page:
                            image_urls.append(self.add_video_urls(url_type, share_id, items_in_bucket['id'][item_idx], me['allowDownload']))    
                        lgInit += self.add_lg_video(url_type, share_id, items_in_bucket['id'][item_idx])
            
            lgInit += self.add_lg_config()[1]
            
            return render_template('share.html', paths=image_urls, share_id=share_id, album_name=album_name, album_description=album_desc, album_thumbnail=album_thumbnail, lgInit=lgInit, url_type=url_type, allowDownloadAll=allowDownloadAll, items_per_page=items_per_page)

        @self.app.route("/<string:url_type>/photo/<string:share_id>/<string:asset_id>/<string:get_type>", methods=["GET"])
        def share_photo(url_type:str, share_id:str, asset_id:str, get_type:str):
            if url_type not in allowed_url_types:
                return invalidResponse()
            
            key_slug = self.key_or_slug(url_type)
                
            if get_type not in ['thumbnail', 'preview', 'fullsize']:
                return invalidResponse()
            
            if get_type == "fullsize" and config['ipp']['downloadOriginalPhoto'] == False:
                return invalidResponse()
            
            r = get_url(f'/api/assets/{asset_id}/thumbnail?{key_slug}={share_id}&size={get_type}')
            if b'message' in r.content:
                return invalidResponse()
            
            return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'), headers=config['ipp']['responseHeaders'])


        @self.app.route("/<string:url_type>/video/<string:share_id>/<string:asset_id>", methods=["GET"])
        def share_video(url_type:str, share_id:str, asset_id:str):
            if url_type not in allowed_url_types:
                return invalidResponse()

            key_slug = self.key_or_slug(url_type)
            
            range_header = request.headers.get('Range', None)
            headers = {}

            if range_header:
                headers['Range'] = range_header
            
            # get range from server
            r = get_url(f'/api/assets/{asset_id}/video/playback?{key_slug}={share_id}', headers=headers, stream=True)
            
            # Get content type and content length from upstream
            content_type = r.headers.get('Content-Type', 'video/mp4')
            content_length = r.headers.get('Content-Length', None)
            status_code = r.status_code

            # Build Flask response
            response = Response(r.iter_content(chunk_size=config['ipp']['videoChunkSize']), status=status_code, content_type=content_type)

            # Copy important headers from upstream response
            response.headers['Content-Length'] = content_length
            if 'Content-Range' in r.headers:
                response.headers['Content-Range'] = r.headers['Content-Range']
            response.headers['Accept-Ranges'] = 'bytes'

            return response
        
        @self.app.route("/<string:url_type>/video/<string:share_id>/<string:asset_id>/<string:get_type>", methods=["GET"])
        def share_video_thumbnail(url_type:str, share_id:str, asset_id:str, get_type:str):
            if url_type not in allowed_url_types:
                return invalidResponse()
            
            key_slug = self.key_or_slug(url_type)
            
            if get_type not in ['original', 'thumbnail']:
                return invalidResponse()
            if get_type == 'thumbnail':
                r = get_url(f'/api/assets/{asset_id}/thumbnail?{key_slug}={share_id}')
                return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))
            elif get_type == 'original' and config['downloadOriginalPhoto']:
                print(f"original for {share_id}/{asset_id}")
                return f"original for {share_id}/{asset_id}"
            return invalidResponse()
        
        @self.app.route('/<string:url_type>/<string:share_id>/download', methods=["GET"])
        def download(url_type:str, share_id:str):
            if url_type not in allowed_url_types:
                return invalidResponse()
            key_slug = self.key_or_slug(url_type=url_type)
            
            me = get_url(f'/api/shared-links/me?{key_slug}={share_id}').json()
            if me['type'] == "INDIVIDUAL": # single image album
                asset_ids = []
            else:    
                album_id = me['album']['id']
                
                download_info = post_url(f'/api/download/info?{key_slug}={share_id}', json={'albumId': album_id}).json()
                if 'archives' not in download_info:
                    return invalidResponse()
                archives = download_info['archives']
                
                download_info = post_url(f'/api/download/info?{key_slug}={share_id}', json={'albumId': album_id}).json()
                asset_ids = []
                for archive in archives:
                    for id in archive['assetIds']:
                        asset_ids.append(id)
                
            zip_response = post_url(f'/api/download/archive?{key_slug}={share_id}', headers={"accept-encoding": "br"}, json={"assetIds": asset_ids}, stream=True)
            
            response = Response(zip_response.iter_content(chunk_size=config['ipp']['downloadAllChunkSize']), status=zip_response.status_code, content_type=zip_response.headers.get('Content-Type', 'application/octet-stream'), headers=zip_response.headers)
            response.headers['Content-Type'] = 'application/zip'
            response.headers['keep-alive'] = 'timeout=5'
            if me['type'] == "INDIVIDUAL": # single image album
                response.headers['Content-Disposition'] = f'attachment; filename="{me['assets'][0]['originalFileName']}"'
            else:
                response.headers['Content-Disposition'] = f'attachment; filename="{me['album']['albumName']}.zip"'
            del response.headers['content-encoding']

            return response
           # return {'assets': archives}
        
        @self.app.route('/<string:url_type>/<string:share_id>/download/<int:archive_id>', methods=["GET"])
        def download_archive(url_type:str, share_id:str, archive_id:int):
            if url_type not in allowed_url_types:
                return invalidResponse()
             
            key_slug = self.key_or_slug(url_type=url_type)
            
            me = get_url(f'/api/shared-links/me?{key_slug}={share_id}').json()
            album_id = me['album']['id']
            
            download_info = post_url(f'/api/download/info?{key_slug}={share_id}', json={'albumId': album_id}).json()
            zip_response = post_url(f'/api/download/archive?{key_slug}={share_id}', json={"assetIds": download_info['archives'][archive_id]['assetIds']}, stream=True)
            response = Response(zip_response.iter_content(chunk_size=config['ipp']['downloadAllChunkSize']), status=zip_response.status_code, content_type=zip_response.headers.get('Content-Type', 'application/octet-stream'), headers=zip_response.headers)

            return response
        
        