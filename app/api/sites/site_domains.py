# site_domains.py

SITE_DOMAINS = {
    'multimovies': 'https://multimovies.city/',
    'gdmirrorbot': 'https://ssn.techinmind.space/',
    'streamwish': 'https://swiftplayers.com',
    'streamp2p': 'https://multimovies.p2pplay.pro'
}

def get_domain(site_name: str) -> str:
    return SITE_DOMAINS.get(site_name)
