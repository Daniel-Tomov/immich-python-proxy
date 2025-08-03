from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    make_response,
    session,
    redirect,
    url_for,
    send_file,
    Response
)
from flask_compress import Compress
from requests import get

from utils import error_404, get_url, invalidResponse
from environment import items_per_page, config

class Share:
    def __init__(self, app:Flask):
        self.app = app
        self.register_routes()
    
    def register_routes(self):        
        @self.app.route("/<string:url_type>/<string:share_id>", methods=["GET"])
        def share(url_type:str, share_id:str):
            if url_type not in ['share', 's']:
                return error_404()
            
            if url_type == "share":
                key_or_slug = 'key' # key for auto-generated URL
            else:
                key_or_slug = 'slug' # slug for custom URL
            
            me = get_url(f'/api/shared-links/me?{key_or_slug}={share_id}').json()
            if 'message' in me and me['message'] == f'Invalid share {key_or_slug}':
                return invalidResponse()
            
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
            
            allowDownload = me['allowDownload']
            showMetadata = me['showMetadata']
            
            buckets = get_url(f'/api/timeline/buckets?albumId={album_id}&{key_or_slug}={share_id}&order=desc').json()

            image_urls = []
            
            lgInit = '{"lgConfig":{"controls":' + str(config['lightGallery']['controls']).lower() + ',"download":' + str(config['lightGallery']['download']).lower() + ',"mobileSettings":{"controls":' + str(config['lightGallery']['mobileSettings']['controls']).lower() + ',"showCloseIcon":' + str(config['lightGallery']['mobileSettings']['showCloseIcon']).lower() + ',"download":' + str(config['lightGallery']['mobileSettings']['download']).lower() + '}},"items":['
            
            # individual bucket : /api/timeline/bucket?albumId=<albumid>&key=<shareid>&order=desc&timeBucket=<somedate>
            for bucket in buckets:
                items_in_bucket = get_url(f'/api/timeline/bucket?albumId={album_id}&{key_or_slug}={share_id}&order=desc&timeBucket={bucket['timeBucket']}').json()
                for item_idx in range(0, bucket['count']):
                    if items_in_bucket['isImage'][item_idx]: 
                        if len(image_urls) < items_per_page:
                            image_urls.append(
                                {
                                    'type': 'photo',
                                    'thumb': f'/{url_type}/photo/{share_id}/{items_in_bucket['id'][item_idx]}/thumbnail',
                                    'preview': f'/{url_type}/photo/{share_id}/{items_in_bucket['id'][item_idx]}/preview',
                                    'original': f'/{url_type}/photo/{share_id}/{items_in_bucket['id'][item_idx]}/fullsize',
                                }
                            )
                        lgInit += '{"html":"<a href=\\\"/' + url_type + '/photo/' + share_id + '/' + items_in_bucket['id'][item_idx]+ '/preview\\\" data-download-url=\\\"/' + url_type + '/photo/' + share_id + '/' + items_in_bucket['id'][item_idx] + '/original\\\"><img alt=\\\"\\\" src=\\\"/' + url_type + '/photo/' + share_id + '/' + items_in_bucket['id'][item_idx] + '/thumbnail\\\"/></a>","thumbnailUrl":"/' + url_type + '/photo/' + share_id + '/' + items_in_bucket['id'][item_idx] + '/thumbnail"},'
                    else:
                        if len(image_urls) < items_per_page:
                            image_urls.append(
                                {
                                    'type': 'video',
                                    'thumb': f'/{url_type}/video/{share_id}/{items_in_bucket['id'][item_idx]}/thumbnail',
                                    'video': f'/{url_type}/video/{share_id}/{items_in_bucket['id'][item_idx]}',
                                    'original': f'/{url_type}/video/{share_id}/{items_in_bucket['id'][item_idx]}/original',
                                }
                            )    
                        lgInit += "{\"html\":\"<a data-video='{\\\"source\\\":[{\\\"src\\\":\\\"/" + url_type + "/video/" + share_id + "/" + items_in_bucket['id'][item_idx] + "\\\",\\\"type\\\":\\\"video/mp4\\\"}],\\\"attributes\\\":{\\\"playsinline\\\":\\\"playsinline\\\",\\\"controls\\\":\\\"controls\\\"}}' data-download-url=\\\"/" + url_type + "/photo/" + share_id + "/" + items_in_bucket['id'][item_idx] + "/original\\\"><img alt=\\\"\\\" src=\\\"/" + url_type + "/photo/" + share_id + "/" + items_in_bucket['id'][item_idx]+ "/thumbnail\\\"/><div class=\\\"play-icon\\\"></div></a>\",\"thumbnailUrl\":\"/" + url_type + "/photo/" + share_id + "/" + items_in_bucket['id'][item_idx] + "/thumbnail\"},"
            
            lgInit += ']}'
            return render_template('share.html', paths=image_urls, share_id=share_id, album_name=album_name, album_description=album_desc, album_thumbnail=album_thumbnail, lgInit=lgInit)

        @self.app.route("/<string:url_type>/photo/<string:share_id>/<string:asset_id>/<string:get_type>", methods=["GET"])
        def share_photo(url_type:str, share_id:str, asset_id:str, get_type:str):
            if url_type not in ['share', 's']:
                return invalidResponse()
            
            if url_type == "share":
                key_or_slug = 'key' # key for auto-generated URL
            else:
                key_or_slug = 'slug' # slug for custom URL
                
            if get_type not in ['thumbnail', 'preview', 'fullsize']:
                return invalidResponse()
            
            if get_type == "fullsize" and config['downloadOriginalPhoto'] == False:
                return invalidResponse()
            
            r = get_url(f'/api/assets/{asset_id}/thumbnail?{key_or_slug}={share_id}&size={get_type}')
            return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))


        @self.app.route("/<string:url_type>/video/<string:share_id>/<string:asset_id>", methods=["GET"])
        def share_video(url_type:str, share_id:str, asset_id:str):
            if url_type not in ['share', 's']:
                return invalidResponse()

            if url_type == "share":
                key_or_slug = 'key' # key for auto-generated URL
            else:
                key_or_slug = 'slug' # slug for custom URL
                
            range_header = request.headers.get('Range', None)
            headers = {}

            if range_header:
                headers['Range'] = range_header
            
            # get range from server
            r = get_url(f'/api/assets/{asset_id}/video/playback?{key_or_slug}={share_id}', headers=headers)
            
            # Get content type and content length from upstream
            content_type = r.headers.get('Content-Type', 'video/mp4')
            content_length = r.headers.get('Content-Length', None)
            status_code = r.status_code

            # Build Flask response
            response = Response(r.iter_content(chunk_size=2048), status=status_code, content_type=content_type)

            # Copy important headers from upstream response
            response.headers['Content-Length'] = content_length
            if 'Content-Range' in r.headers:
                response.headers['Content-Range'] = r.headers['Content-Range']
            response.headers['Accept-Ranges'] = 'bytes'

            return response
        
        @self.app.route("/<string:url_type>/video/<string:share_id>/<string:asset_id>/<string:get_type>", methods=["GET"])
        def share_video_thumbnail(url_type:str, share_id:str, asset_id:str, get_type:str):
            if url_type not in ['share', 's']:
                return invalidResponse()
            
            if url_type == "share":
                key_or_slug = 'key' # key for auto-generated URL
            else:
                key_or_slug = 'slug' # slug for custom URL
                
            if get_type not in ['original', 'thumbnail']:
                return invalidResponse()
            if get_type == 'thumbnail':
                r = get_url(f'/api/assets/{asset_id}/thumbnail?{key_or_slug}={share_id}')
                return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))
            elif get_type == 'original' and config['downloadOriginalPhoto']:
                print(f"original for {share_id}/{asset_id}")
                return f"original for {share_id}/{asset_id}"
            return invalidResponse()
        
        @self.app.route("/share/static/web.js", methods=["GET"])
        def share_web_js():
            return render_template('web.js', items_per_page=items_per_page)