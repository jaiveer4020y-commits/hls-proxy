from django.http import JsonResponse
from .sites import streamwish, multimovies

# List of extractors with corresponding domains
site_extractors = [
    (['hlsflex', 'streamwish'], streamwish),
    (['iqsmartgames'], multimovies)
]

def api_endpoint(request):
    target_url = request.GET.get('url', None)
    tmdb_id    = request.GET.get('id', None)

    # =================================================
    # Direct TMDB route: ?id=124364&type=tv&s=1&e=1
    # =================================================

    if tmdb_id and not target_url:
        data = multimovies.real_extract(None, request)

        if not isinstance(data, dict):
            data = {'error': 'Unexpected error: invalid response from real_extract'}

        return JsonResponse(data, status=data.get('status_code', 200))

    # =================================================
    # Original URL-based route
    # =================================================

    if not target_url:
        return JsonResponse({'error': 'URL parameter "url" is required'}, status=400)

    for domains, extractor in site_extractors:
        if any(domain in target_url for domain in domains):
            data = extractor.real_extract(target_url, request)
            break
    else:
        return JsonResponse({'error': 'Invalid site name'}, status=400)

    if not isinstance(data, dict):
        data = {'error': 'Unexpected error: invalid response from real_extract'}

    return JsonResponse(data, status=data.get('status_code', 200))
