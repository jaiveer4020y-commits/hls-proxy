from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .sites import gdmirrorbot, streamwish, streamp2p


def api_endpoint(request):
    return JsonResponse({'status': 'ok'})


@require_GET
def resolve_fileslug(request):
    fileslug = request.GET.get('fileslug')
    if not fileslug:
        return JsonResponse({'status': 'error', 'error': 'fileslug required'}, status=400)

    gd = gdmirrorbot.real_extract(fileslug)
    if gd.get('status') == 'error':
        return JsonResponse({'status': 'error', 'error': gd['error']}, status=502)

    embed_urls = gd.get('embed_urls', {})
    servers = []

    STREAMWISH_KEYS = {'StreamHG','streamhg','EarnVids','earnvids','FileMoon','filemoon','StreamWish','streamwish'}
    STREAMP2P_KEYS  = {'RpmShare','UpnShare','StreamP2p','rpmhub'}
    PLYR_WRAPPER    = 'https://plyr.technocosmos.surf/hlsplayer?url='

    for key, embed_url in embed_urls.items():
        if key in STREAMWISH_KEYS:
            try:
                res = streamwish.real_extract(embed_url)
                servers.append({'provider': key, 'result': res})
            except Exception as e:
                servers.append({'provider': key, 'status': 'error', 'error': str(e)})
        elif key in STREAMP2P_KEYS:
            if PLYR_WRAPPER in embed_url:
                embed_url = embed_url.split('?url=')[-1]
            try:
                res = streamp2p.real_extract(embed_url)
                servers.append({'provider': key, 'result': res})
            except Exception as e:
                servers.append({'provider': key, 'status': 'error', 'error': str(e)})

    if not servers:
        return JsonResponse({'status': 'error', 'error': 'No streams found'}, status=404)

    return JsonResponse({'status': 'success', 'servers': servers})
