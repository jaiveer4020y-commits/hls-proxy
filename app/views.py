from django.http import HttpResponse


def home(request):
    html_content = r"""
   <html lang="en" __gcrremoteframetoken="d0db1bb5f175ac516ebffb377a75e1c3"><head>
    <meta http-equiv="Accept-CH" content="Viewport-Width, Width">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, shrink-to-fit=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta charset="UTF-8">
    <title>Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        @font-face{font-family:'Netflix Sans';src:url('https://assets.nflxext.com/ffe/siteui/fonts/netflix-sans/v3/NetflixSans_W_Rg.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
        @font-face{font-family:'Netflix Sans';src:url('https://assets.nflxext.com/ffe/siteui/fonts/netflix-sans/v3/NetflixSans_W_Md.woff2') format('woff2');font-weight:500;font-style:normal;font-display:swap}
        @font-face{font-family:'Netflix Sans';src:url('https://assets.nflxext.com/ffe/siteui/fonts/netflix-sans/v3/NetflixSans_W_Bd.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}
        html,body{height:100%;width:100vw;margin:0;padding:0;overflow:hidden;font-family:'Netflix Sans',sans-serif;background:#000}
        body{padding-bottom:env(safe-area-inset-bottom)}
        .bottom-control-button:hover{transform:scale(1.1)}
        #timeline-row{display:flex;width:100%;box-sizing:border-box;gap:1rem;align-items:center;position:relative}
        #bottom-controls-row{display:flex;width:100%;padding-top:4px;gap:8px;box-sizing:border-box;position:relative;margin-top:0}
        .bottom-control-button{background:transparent;border-radius:.2rem;border:none;color:#fff;cursor:pointer;padding:0;margin:0!important;position:relative;transition:transform 200ms;width:3rem;height:3rem}
        #mobile-skip-backward-button{margin-right:calc(1.5rem*calc(1 - var(--tw-space-x-reverse)))}
        #mobile-skip-forward-button{margin-left:calc(1.5rem*calc(1 - var(--tw-space-x-reverse)))}
        @media(min-width:1000px){
            #bottom-controls-row{padding-top:24px!important;padding-bottom:24px!important}
            #mobile-skip-backward-button{margin-right:calc(2.5rem*calc(1 - var(--tw-space-x-reverse)))}
            #mobile-skip-forward-button{margin-left:calc(2.5rem*calc(1 - var(--tw-space-x-reverse)))}
            .bottom-control-button{width:3rem;height:3rem}
        }
        @media(max-width:1000px){
            #right-controlbuttons{justify-content:center}
            #speed-button{position:relative;left:0}
            #bottom-controls-row{justify-content:center}
            #left-controlbuttons{display:none}
            #center-controls-mobile-only{width:50vw;justify-content:space-between!important}
            #skip-forward-button,#skip-backward-button{display:none}
            .mobile-labeled-btn{width:auto!important;height:auto!important;flex-direction:row!important;gap:5px;padding:4px 6px!important}
            .mobile-labeled-btn svg{width:1.4rem!important;height:1.4rem!important}
            .mobile-btn-label{display:inline-block;font-size:.7rem;font-weight:500;color:#fff;white-space:nowrap;line-height:1}
        }
        @media(min-width:1000px){.mobile-btn-label{display:none}}
        @media(max-width:500px){
            #back-button,#report-button,#mobile-title{display:none!important}
            #right-controlbuttons{width:unset;justify-content:space-between}
            #speed-button{position:relative}
        }
        #mobile-title{display:none}
        @media(max-width:999px){#mobile-title{display:flex}#mobile-title-main{font-size:16px!important;font-weight:400!important}}
        @media(min-width:1000px){#mobile-title{display:none!important}}
        #top-bar{pointer-events:none}
        #top-bar>*{pointer-events:auto}
        @media(min-width:500px){#left-controlbuttons,#right-controlbuttons{gap:1.5rem}#bottom-controls-row{padding-top:24px;padding-bottom:24px}}
        #controls-bar{padding:0 16px}
        #progress-indicator,#seek-thumb{background:rgb(225,0,0)}
        #center-controls-mobile-only{width:50vw;justify-content:center}
        #seek-bar{height:3px;transition:height .15s ease;cursor:pointer}
        #seek-bar:hover{height:6px}
        #seek-thumb{height:1rem;width:1rem;transform:translateY(-50%) scale(1)}
        #video-container{width:100vw;height:100vh;background:#000}
        .controls-visible{opacity:1;pointer-events:auto}
        .controls-hidden{opacity:0;pointer-events:none}
        #volume-slider-track{background:#ffffff33}
        #audio-tracks-container::-webkit-scrollbar,#subtitle-tracks-container::-webkit-scrollbar{width:8px}
        #audio-tracks-container::-webkit-scrollbar-thumb,#subtitle-tracks-container::-webkit-scrollbar-thumb{background:#555;border-radius:4px}
        @media(max-width:999px){#audio-list,#subtitle-list{font-size:16px!important}}
        .track-selector{border-radius:4px;padding:8px 10px!important;transition:background .15s ease}
        .track-selector:hover{background:rgba(255,255,255,.1)!important}
        @media(max-width:999px){
            #audio-subtitle-menu:not(.hidden){background:black!important;position:fixed!important;top:0!important;left:0!important;right:0!important;bottom:0!important;width:100%!important;max-width:100%!important;height:100%!important;max-height:100%!important;border-radius:0!important;display:flex!important;flex-direction:column!important;z-index:99999!important;overflow:hidden!important;padding:0!important}
            #audio-subtitle-menu-inner{flex:1;overflow:hidden;padding:16px;display:flex;flex-direction:column}
            #audio-subtitle-menu-inner>.flex{flex:1;min-height:0;overflow:hidden}
            #audio-tracks-container,#subtitle-tracks-container{max-height:unset!important;overflow-y:visible!important;border:none;min-height:0}
            #audio-tracks-container #audio-list,#subtitle-tracks-container #subtitle-list{max-height:unset!important;overflow-y:auto!important;flex:1;min-height:0}
            #audio-subtitle-menu-footer{display:flex!important}
        }
        @media(min-width:1000px){
            #audio-subtitle-menu-footer{display:none!important}
            #audio-subtitle-menu-inner{padding:0!important;flex:unset!important;overflow-y:unset!important}
        }
        #loading-indicator img{width:50px;height:50px;border-radius:50%;animation:spin 1s linear infinite}
        @keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
        ::cue{background:transparent;color:#fff;font-family:'Netflix Sans',sans-serif;font-size:1.1em;font-weight:400;text-shadow:0 1px 3px rgba(0,0,0,.9),0 0 8px rgba(0,0,0,.7);line-height:1.4}
        video::-webkit-media-text-track-display{overflow:visible!important}
        video::cue{background:transparent}
        #skip-hint{position:fixed;top:50%;transform:translateY(-50%);font-weight:700;font-size:3.5rem;text-shadow:0 0 20px rgba(0,0,0,.8);opacity:0;transition:opacity .3s ease,transform .15s ease-out;z-index:40;pointer-events:none}
        @media(min-width:768px){#skip-hint{font-size:5rem}}
        #skip-hint.show{opacity:1;transform:translateY(-50%) scale(1)}
        #skip-hint.left{left:8%}
        #skip-hint.right{right:8%}
        #title-display{position:absolute;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;pointer-events:none;white-space:nowrap;overflow:hidden;max-width:40vw}
        #title-display .title-main{color:#fff;font-size:16px;font-weight:400;letter-spacing:.01em;text-overflow:ellipsis;white-space:nowrap;max-width:100%}
        @media(max-width:600px){#title-display{max-width:28vw}#title-display .title-main{font-size:.75rem}}
        @media(max-width:999px){#title-display{display:none!important}}
        .report-modal{position:absolute;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center;z-index:99999;opacity:0;pointer-events:none;transition:opacity .2s ease;padding:16px}
        .report-modal.active{opacity:1;pointer-events:auto}
        .report-modal-box{background:#141414;width:100%;max-width:420px;border-radius:6px;padding:20px;box-shadow:0 20px 60px rgba(0,0,0,.8);transform:translateY(10px) scale(.96);transition:transform .2s ease}
        .report-modal.active .report-modal-box{transform:translateY(0) scale(1)}
        .report-modal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
        .report-modal-title{color:#fff;font-size:18px;margin:0;font-weight:700}
        .report-close-btn{background:none;border:none;color:#b3b3b3;font-size:22px;cursor:pointer;line-height:1}
        .report-close-btn:hover{color:#fff}
        .report-modal-body label{display:block;margin:14px 0 6px;font-size:13px;color:#b3b3b3}
        .report-modal-body select,.report-modal-body textarea{width:100%;padding:12px 40px 12px 12px;background:#000;border:1px solid #2a2a2a;color:#fff;border-radius:4px;font-size:14px;font-family:'Netflix Sans',sans-serif;outline:none;box-sizing:border-box}
        .report-modal-body select{appearance:none;-webkit-appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23b3b3b3' d='M6 8L0 0h12z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;background-size:12px}
        .report-modal-body select:focus,.report-modal-body textarea:focus{border-color:rgb(225,0,0)}
        .report-modal-body textarea{resize:none;min-height:96px}
        .report-modal-footer{display:flex;justify-content:flex-end;margin-top:20px}
        .report-submit-btn{padding:10px 18px;background:rgb(225,0,0);cursor:pointer;border-radius:4px;font-weight:700;border:none;color:#fff}
        .report-submit-btn:disabled{opacity:.5;cursor:not-allowed}
        @media(max-width:480px){.report-modal-box{padding:16px}.report-modal-title{font-size:16px}}
        #quality-menu{position:absolute;bottom:4rem;right:0;width:13rem;border-radius:8px;background:rgba(28,28,30,.95);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);padding:8px 0;color:#fff;z-index:50;box-shadow:0 8px 20px rgba(0,0,0,.5)}
        #quality-list{list-style:none;margin:0;padding:0;font-size:.9rem}
        #quality-list li{padding:10px 16px;cursor:pointer;transition:background .15s;display:flex;justify-content:space-between;align-items:center}
        #quality-list li:hover{background:rgba(255,255,255,.1)}
        #quality-list li .quality-badge{font-size:.7rem;background:rgba(255,255,255,.2);padding:2px 6px;border-radius:4px}
        .quality-active{color:rgb(225,0,0)}
        .quality-active .quality-badge{background:rgb(225,0,0);color:#fff}
        #next-episode-button{background:transparent;border:none;color:#fff;cursor:pointer;display:none;align-items:center;justify-content:center;gap:4px;width:auto;padding:0 8px;font-size:.85rem;font-weight:500;font-family:'Netflix Sans',sans-serif;transition:transform .2s ease;white-space:nowrap}
        #next-episode-button svg{width:18px;height:18px}
        #next-episode-button:hover{transform:scale(1.05)}
        @media(max-width:1000px){#next-episode-button{font-size:.7rem;padding:0 4px}#next-episode-button svg{width:14px;height:14px}}
        video::-webkit-media-controls{display:none!important}
        video::-webkit-media-controls-enclosure{display:none!important}
    </style>
<style>*, ::before, ::after{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }::backdrop{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }/* ! tailwindcss v3.4.17 | MIT License | https://tailwindcss.com */*,::after,::before{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}::after,::before{--tw-content:''}:host,html{line-height:1.5;-webkit-text-size-adjust:100%;-moz-tab-size:4;tab-size:4;font-family:ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";font-feature-settings:normal;font-variation-settings:normal;-webkit-tap-highlight-color:transparent}body{margin:0;line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,pre,samp{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;font-feature-settings:normal;font-variation-settings:normal;font-size:1em}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}button,input,optgroup,select,textarea{font-family:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-size:100%;font-weight:inherit;line-height:inherit;letter-spacing:inherit;color:inherit;margin:0;padding:0}button,select{text-transform:none}button,input:where([type=button]),input:where([type=reset]),input:where([type=submit]){-webkit-appearance:button;background-color:transparent;background-image:none}:-moz-focusring{outline:auto}:-moz-ui-invalid{box-shadow:none}progress{vertical-align:baseline}::-webkit-inner-spin-button,::-webkit-outer-spin-button{height:auto}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}summary{display:list-item}blockquote,dd,dl,figure,h1,h2,h3,h4,h5,h6,hr,p,pre{margin:0}fieldset{margin:0;padding:0}legend{padding:0}menu,ol,ul{list-style:none;margin:0;padding:0}dialog{padding:0}textarea{resize:vertical}input::placeholder,textarea::placeholder{opacity:1;color:#9ca3af}[role=button],button{cursor:pointer}:disabled{cursor:default}audio,canvas,embed,iframe,img,object,svg,video{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}[hidden]:where(:not([hidden=until-found])){display:none}.pointer-events-none{pointer-events:none}.pointer-events-auto{pointer-events:auto}.absolute{position:absolute}.relative{position:relative}.inset-0{inset:0px}.inset-y-0{top:0px;bottom:0px}.bottom-0{bottom:0px}.bottom-12{bottom:3rem}.left-0{left:0px}.left-1\/2{left:50%}.right-0{right:0px}.right-1\/2{right:50%}.top-0{top:0px}.top-1\/2{top:50%}.z-10{z-index:10}.z-20{z-index:20}.z-30{z-index:30}.mb-2{margin-bottom:0.5rem}.mt-4{margin-top:1rem}.flex{display:flex}.hidden{display:none}.h-10{height:2.5rem}.h-12{height:3rem}.h-20{height:5rem}.h-24{height:6rem}.h-4{height:1rem}.h-6{height:1.5rem}.h-full{height:100%}.max-h-56{max-height:14rem}.min-h-0{min-height:0px}.w-10{width:2.5rem}.w-12{width:3rem}.w-2{width:0.5rem}.w-20{width:5rem}.w-4{width:1rem}.w-48{width:12rem}.w-6{width:1.5rem}.w-72{width:18rem}.w-full{width:100%}.max-w-\[85vw\]{max-width:85vw}.flex-1{flex:1 1 0%}.flex-shrink-0{flex-shrink:0}.flex-grow{flex-grow:1}.-translate-x-1\/2{--tw-translate-x:-50%;transform:translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y))}.-translate-y-1\/2{--tw-translate-y:-50%;transform:translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y))}.cursor-pointer{cursor:pointer}.select-none{-webkit-user-select:none;user-select:none}.flex-col{flex-direction:column}.items-center{align-items:center}.justify-end{justify-content:flex-end}.justify-center{justify-content:center}.justify-between{justify-content:space-between}.gap-4{gap:1rem}.space-x-1 > :not([hidden]) ~ :not([hidden]){--tw-space-x-reverse:0;margin-right:calc(0.25rem * var(--tw-space-x-reverse));margin-left:calc(0.25rem * calc(1 - var(--tw-space-x-reverse)))}.space-x-2 > :not([hidden]) ~ :not([hidden]){--tw-space-x-reverse:0;margin-right:calc(0.5rem * var(--tw-space-x-reverse));margin-left:calc(0.5rem * calc(1 - var(--tw-space-x-reverse)))}.space-x-6 > :not([hidden]) ~ :not([hidden]){--tw-space-x-reverse:0;margin-right:calc(1.5rem * var(--tw-space-x-reverse));margin-left:calc(1.5rem * calc(1 - var(--tw-space-x-reverse)))}.space-y-1 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.25rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.25rem * var(--tw-space-y-reverse))}.space-y-2 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.5rem * var(--tw-space-y-reverse))}.overflow-y-auto{overflow-y:auto}.rounded-\[0\.4rem\]{border-radius:0.4rem}.rounded-full{border-radius:9999px}.rounded-lg{border-radius:0.5rem}.border-l{border-left-width:1px}.border-gray-700{--tw-border-opacity:1;border-color:rgb(55 65 81 / var(--tw-border-opacity, 1))}.bg-black\/50{background-color:rgb(0 0 0 / 0.5)}.bg-black\/80{background-color:rgb(0 0 0 / 0.8)}.bg-red-800{--tw-bg-opacity:1;background-color:rgb(153 27 27 / var(--tw-bg-opacity, 1))}.bg-white\/30{background-color:rgb(255 255 255 / 0.3)}.bg-white\/50{background-color:rgb(255 255 255 / 0.5)}.bg-gradient-to-t{background-image:linear-gradient(to top, var(--tw-gradient-stops))}.from-black\/70{--tw-gradient-from:rgb(0 0 0 / 0.7) var(--tw-gradient-from-position);--tw-gradient-to:rgb(0 0 0 / 0) var(--tw-gradient-to-position);--tw-gradient-stops:var(--tw-gradient-from), var(--tw-gradient-to)}.to-transparent{--tw-gradient-to:transparent var(--tw-gradient-to-position)}.object-cover{object-fit:cover}.p-3{padding:0.75rem}.p-4{padding:1rem}.px-6{padding-left:1.5rem;padding-right:1.5rem}.pb-1{padding-bottom:0.25rem}.pl-2{padding-left:0.5rem}.pr-2{padding-right:0.5rem}.text-center{text-align:center}.text-sm{font-size:0.875rem;line-height:1.25rem}.text-xs{font-size:0.75rem;line-height:1rem}.font-medium{font-weight:500}.leading-tight{line-height:1.25}.text-gray-200{--tw-text-opacity:1;color:rgb(229 231 235 / var(--tw-text-opacity, 1))}.text-gray-400{--tw-text-opacity:1;color:rgb(156 163 175 / var(--tw-text-opacity, 1))}.text-white{--tw-text-opacity:1;color:rgb(255 255 255 / var(--tw-text-opacity, 1))}.opacity-100{opacity:1}.opacity-0{opacity:0}.shadow-2xl{--tw-shadow:0 25px 50px -12px rgb(0 0 0 / 0.25);--tw-shadow-colored:0 25px 50px -12px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-lg{--tw-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);--tw-shadow-colored:0 10px 15px -3px var(--tw-shadow-color), 0 4px 6px -4px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-xl{--tw-shadow:0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);--tw-shadow-colored:0 20px 25px -5px var(--tw-shadow-color), 0 8px 10px -6px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.transition-all{transition-property:all;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.transition-opacity{transition-property:opacity;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.transition-transform{transition-property:transform;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.duration-100{transition-duration:100ms}.duration-150{transition-duration:150ms}.duration-200{transition-duration:200ms}.duration-500{transition-duration:500ms}.hover\:opacity-80:hover{opacity:0.8}.focus\:outline-none:focus{outline:2px solid transparent;outline-offset:2px}@media (min-width: 768px){.md\:h-14{height:3.5rem}.md\:h-16{height:4rem}.md\:h-9{height:2.25rem}.md\:h-full{height:100%}.md\:w-12{width:3rem}.md\:w-14{width:3.5rem}.md\:w-16{width:4rem}.md\:w-9{width:2.25rem}.md\:w-\[450px\]{width:450px}.md\:w-full{width:100%}.md\:space-x-2 > :not([hidden]) ~ :not([hidden]){--tw-space-x-reverse:0;margin-right:calc(0.5rem * var(--tw-space-x-reverse));margin-left:calc(0.5rem * calc(1 - var(--tw-space-x-reverse)))}.md\:space-x-4 > :not([hidden]) ~ :not([hidden]){--tw-space-x-reverse:0;margin-right:calc(1rem * var(--tw-space-x-reverse));margin-left:calc(1rem * calc(1 - var(--tw-space-x-reverse)))}.md\:space-y-3 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.75rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.75rem * var(--tw-space-y-reverse))}.md\:p-4{padding:1rem}.md\:text-sm{font-size:0.875rem;line-height:1.25rem}}@media (min-width: 1280px){.xl\:hidden{display:none}}</style><style type="text/css">.eruda-search-highlight-block{display:inline}.eruda-search-highlight-block .eruda-keyword{background:#332a00;color:#ffcb6b}</style><style type="text/css">@font-face{font-family:eruda-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,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') format('woff')}[class*=' eruda-icon-'],[class^='eruda-icon-']{display:inline-block;font-family:eruda-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.eruda-icon-arrow-left:before{content:'\f101'}.eruda-icon-arrow-right:before{content:'\f102'}.eruda-icon-caret-down:before{content:'\f103'}.eruda-icon-caret-right:before{content:'\f104'}.eruda-icon-clear:before{content:'\f105'}.eruda-icon-compress:before{content:'\f106'}.eruda-icon-copy:before{content:'\f107'}.eruda-icon-delete:before{content:'\f108'}.eruda-icon-error:before{content:'\f109'}.eruda-icon-expand:before{content:'\f10a'}.eruda-icon-eye:before{content:'\f10b'}.eruda-icon-filter:before{content:'\f10c'}.eruda-icon-play:before{content:'\f10d'}.eruda-icon-record:before{content:'\f10e'}.eruda-icon-refresh:before{content:'\f10f'}.eruda-icon-reset:before{content:'\f110'}.eruda-icon-search:before{content:'\f111'}.eruda-icon-select:before{content:'\f112'}.eruda-icon-tool:before{content:'\f113'}.eruda-icon-warn:before{content:'\f114'}@font-face{font-family:luna-console-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,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') format('woff')}[class*=' luna-console-icon-'],[class^=luna-console-icon-]{display:inline-block;font-family:luna-console-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.luna-console-icon-caret-down:before{content:'\f101'}.luna-console-icon-caret-right:before{content:'\f102'}.luna-console-icon-warn:before{content:'\f103'}.luna-console-icon-error:before{content:'\f104'}.luna-console-icon-input:before{content:'\f105'}.luna-console-icon-output:before{content:'\f106'}.luna-console{background:#fff;overflow-y:auto;-webkit-overflow-scrolling:touch;height:100%;position:relative;will-change:scroll-position;cursor:default;font-size:12px;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace}.luna-console.luna-console-theme-dark{background-color:#141414}.luna-console-hidden{display:none}.luna-console-fake-logs{position:absolute;left:0;top:0;pointer-events:none;visibility:hidden;width:100%}.luna-console-logs{padding-top:1px;position:absolute;width:100%}.luna-console-log-container{box-sizing:content-box}.luna-console-log-container.luna-console-selected .luna-console-log-item{background:#ecf1f8}.luna-console-log-container.luna-console-selected .luna-console-log-item:not(.luna-console-error):not(.luna-console-warn){border-color:#ccdef5}.luna-console-header{white-space:nowrap;display:flex;font-size:11px;color:#545454;border-top:1px solid transparent;border-bottom:1px solid #ccc}.luna-console-header .luna-console-time-from-container{overflow-x:auto;-webkit-overflow-scrolling:touch;padding:3px 10px}.luna-console-nesting-level{width:14px;flex-shrink:0;margin-top:-1px;margin-bottom:-1px;position:relative;border-right:1px solid #ccc}.luna-console-nesting-level.luna-console-group-closed::before{content:""}.luna-console-nesting-level::before{border-bottom:1px solid #ccc;position:absolute;top:0;left:0;margin-left:100%;width:5px;height:100%;box-sizing:border-box}.luna-console-log-item{position:relative;display:flex;border-top:1px solid transparent;border-bottom:1px solid #ccc;margin-top:-1px;color:#333}.luna-console-log-item:after{content:"";display:block;clear:both}.luna-console-log-item .luna-console-code{display:inline;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace}.luna-console-log-item .luna-console-code .luna-console-keyword{color:#881280}.luna-console-log-item .luna-console-code .luna-console-number{color:#1c00cf}.luna-console-log-item .luna-console-code .luna-console-operator{color:gray}.luna-console-log-item .luna-console-code .luna-console-comment{color:#236e25}.luna-console-log-item .luna-console-code .luna-console-string{color:#1a1aa6}.luna-console-log-item a{color:#15c!important}.luna-console-log-item .luna-console-icon-container{margin:0 -6px 0 10px}.luna-console-log-item .luna-console-icon-container .luna-console-icon{line-height:20px;font-size:12px;color:#333;position:relative}.luna-console-log-item .luna-console-icon-container .luna-console-icon-caret-down,.luna-console-log-item .luna-console-icon-container .luna-console-icon-caret-right{top:0;left:-2px}.luna-console-log-item .luna-console-icon-container .luna-console-icon-error{top:0;color:#ef3842}.luna-console-log-item .luna-console-icon-container .luna-console-icon-warn{top:0;color:#e8a400}.luna-console-log-item .luna-console-count{background:#8097bd;color:#fff;padding:2px 4px;border-radius:10px;font-size:12px;float:left;margin:1px -6px 0 10px}.luna-console-log-item .luna-console-log-content-wrapper{flex:1;overflow:hidden}.luna-console-log-item .luna-console-log-content{padding:3px 0;margin:0 10px;overflow-x:auto;-webkit-overflow-scrolling:touch;white-space:pre-wrap;-webkit-user-select:text;-moz-user-select:text;-ms-user-select:text;user-select:text}.luna-console-log-item .luna-console-log-content *{-webkit-user-select:text;-moz-user-select:text;-ms-user-select:text;user-select:text}.luna-console-log-item .luna-console-log-content>*{vertical-align:top}.luna-console-log-item .luna-console-log-content .luna-console-null,.luna-console-log-item .luna-console-log-content .luna-console-undefined{color:#5e5e5e}.luna-console-log-item .luna-console-log-content .luna-console-number{color:#1c00cf}.luna-console-log-item .luna-console-log-content .luna-console-boolean{color:#0d22aa}.luna-console-log-item .luna-console-log-content .luna-console-regexp,.luna-console-log-item .luna-console-log-content .luna-console-symbol{color:#881391}.luna-console-log-item .luna-console-data-grid,.luna-console-log-item .luna-console-dom-viewer{white-space:initial}.luna-console-log-item.luna-console-error{z-index:50;background:#fff0f0;color:red;border-top:1px solid #ffd6d6;border-bottom:1px solid #ffd6d6}.luna-console-log-item.luna-console-error .luna-console-stack{padding-left:1.2em;white-space:nowrap}.luna-console-log-item.luna-console-error .luna-console-count{background:red}.luna-console-log-item.luna-console-debug{z-index:20}.luna-console-log-item.luna-console-input{border-bottom-color:transparent}.luna-console-log-item.luna-console-warn{z-index:40;color:#5c5c00;background:#fffbe5;border-top:1px solid #fff5c2;border-bottom:1px solid #fff5c2}.luna-console-log-item.luna-console-warn .luna-console-count{background:#e8a400}.luna-console-log-item.luna-console-info{z-index:30}.luna-console-log-item.luna-console-group,.luna-console-log-item.luna-console-groupCollapsed{font-weight:700}.luna-console-preview{display:inline-block}.luna-console-preview .luna-console-preview-container{display:flex;align-items:center}.luna-console-preview .luna-console-json{overflow-x:auto;-webkit-overflow-scrolling:touch;padding-left:12px}.luna-console-preview .luna-console-preview-icon-container{display:block}.luna-console-preview .luna-console-preview-icon-container .luna-console-icon{position:relative;font-size:12px}.luna-console-preview .luna-console-preview-icon-container .luna-console-icon-caret-down{top:2px}.luna-console-preview .luna-console-preview-icon-container .luna-console-icon-caret-right{top:1px}.luna-console-preview .luna-console-preview-content-container{word-break:break-all}.luna-console-preview .luna-console-descriptor,.luna-console-preview .luna-console-object-preview{font-style:italic}.luna-console-preview .luna-console-key{color:#881391}.luna-console-preview .luna-console-number{color:#1c00cf}.luna-console-preview .luna-console-null{color:#5e5e5e}.luna-console-preview .luna-console-string{color:#c41a16}.luna-console-preview .luna-console-boolean{color:#0d22aa}.luna-console-preview .luna-console-special{color:#5e5e5e}.luna-console-theme-dark{color-scheme:dark}.luna-console-theme-dark .luna-console-log-container.luna-console-selected .luna-console-log-item{background:#29323d}.luna-console-theme-dark .luna-console-log-container.luna-console-selected .luna-console-log-item:not(.luna-console-error):not(.luna-console-warn){border-color:#4173b4}.luna-console-theme-dark .luna-console-log-item{color:#a5a5a5;border-bottom-color:#3d3d3d}.luna-console-theme-dark .luna-console-log-item .luna-console-code .luna-console-keyword{color:#e36eec}.luna-console-theme-dark .luna-console-log-item .luna-console-code .luna-console-number{color:#9980ff}.luna-console-theme-dark .luna-console-log-item .luna-console-code .luna-console-operator{color:#7f7f7f}.luna-console-theme-dark .luna-console-log-item .luna-console-code .luna-console-comment{color:#747474}.luna-console-theme-dark .luna-console-log-item .luna-console-code .luna-console-string{color:#f29766}.luna-console-theme-dark .luna-console-log-item.luna-console-error{background:#290000;color:#ff8080;border-top-color:#5c0000;border-bottom-color:#5c0000}.luna-console-theme-dark .luna-console-log-item.luna-console-error .luna-console-count{background:#ff8080}.luna-console-theme-dark .luna-console-log-item.luna-console-warn{color:#ffcb6b;background:#332a00;border-top-color:#650;border-bottom-color:#650}.luna-console-theme-dark .luna-console-log-item .luna-console-count{background:#42597f;color:#949494}.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-null,.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-undefined{color:#7f7f7f}.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-boolean,.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-number{color:#9980ff}.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-regexp,.luna-console-theme-dark .luna-console-log-item .luna-console-log-content .luna-console-symbol{color:#e36eec}.luna-console-theme-dark .luna-console-icon-container .luna-console-icon-caret-down,.luna-console-theme-dark .luna-console-icon-container .luna-console-icon-caret-right{color:#9aa0a6}.luna-console-theme-dark .luna-console-header{border-bottom-color:#3d3d3d}.luna-console-theme-dark .luna-console-nesting-level{border-right-color:#3d3d3d}.luna-console-theme-dark .luna-console-nesting-level::before{border-bottom-color:#3d3d3d}.luna-console-theme-dark .luna-console-preview .luna-console-key{color:#e36eec}.luna-console-theme-dark .luna-console-preview .luna-console-number{color:#9980ff}.luna-console-theme-dark .luna-console-preview .luna-console-null{color:#7f7f7f}.luna-console-theme-dark .luna-console-preview .luna-console-string{color:#f29766}.luna-console-theme-dark .luna-console-preview .luna-console-boolean{color:#9980ff}.luna-console-theme-dark .luna-console-preview .luna-console-special{color:#7f7f7f}@font-face{font-family:luna-object-viewer-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,d09GRgABAAAAAAS8AAsAAAAAB7QAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAABHU1VCAAABCAAAAGEAAACMISgl+k9TLzIAAAFsAAAAPQAAAFZLxUkWY21hcAAAAawAAADWAAACdBU42qdnbHlmAAAChAAAAC4AAAAwabU7V2hlYWQAAAK0AAAALwAAADZzjr4faGhlYQAAAuQAAAAYAAAAJAFyANlobXR4AAAC/AAAABAAAABAAZAAAGxvY2EAAAMMAAAAEAAAACIAtACobWF4cAAAAxwAAAAfAAAAIAEbAA9uYW1lAAADPAAAASkAAAIWm5e+CnBvc3QAAARoAAAAUwAAAHZW8MNZeJxNjTsOQFAQRc/z/+sV1mABohKV0gZeJRJR2X9cT4RJZu7nFIMBMjoGvHGaF6rdngcNAc/c/O/Nvq2W5E1igdNE2zv1iGh1c5FQPlYXUlJRyxt9+/pUKadQa/AveGEGZQAAAHicY2BkkGScwMDKwMBQx9ADJGWgdAIDJ4MxAwMTAyszA1YQkOaawnCAQfcjE8MJIFcITDIwMIIIAFqDCGkAAAB4nM2STQ4BQRCFv54ZP8MwFhYW4gQcShBsSERi50BWDuFCcwJedddKRGKnOt8k9aanqudVAy0gF3NRQLgTsLhJDVHP6UW94Kp8zEhKwYIlG/YcOXHm0mTPp96aumLLwdUQ1fcIqmJrwpSZL+iqak5JmyE1Ayr1bdGhr/2ZPmp/qPQtuj/uJzqQl+pfDyypesQD6AT/ElV8PjyrMccT9rdLR3PUFBI227VTio1jbm6dodg5VnPvmAsHxzofHfmi+Sbs/pwdWcXFkWdNSNg9arIE2QufuSCyAAB4nGNgZACBlQzTGZgYGMyVxVc2O073AIpAxHsYloHFRc2dPZY2OTIwAACmEQesAAB4nGNgZGBgAOINe2b6x/PbfGXgZjgBFIjifLyvAUEDwUqGZUCSg4EJxAEAUn4LLAB4nGNgZGBgOMHAACdXMjAyoAIBADizAkx4nGNgAIITUEwGAABZUAGReJxjYAACHgYJ3BAAE94BXXicY2BkYGAQYGBmANEMDExAzAWEDAz/wXwGAApcASsAeJxlkD1uwkAUhMdgSAJSghQpKbNVCiKZn5IDQE9Bl8KYtTGyvdZ6QaLLCXKEHCGniHKCHChj82hgLT9/M2/e7soABviFh3p5uG1qvVq4oTpxm/Qg7JOfhTvo40W4S38o3MMbpsJ9POKdO3j+HZ0BSuEW7vEh3Kb/KeyTv4Q7eMK3cJf+j3APK/wJ9/HqDdPIFLEp3FIn+yy0Z3n+rrStUlOoSTA+WwtdaBs6vVHro6oOydS5WMXW5GrOrs4yo0prdjpywda5cjYaxeIHkcmRIoJBgbipDktoJNgjQwh71b3UK6YtKvq1VpggwPgqtWCqaJIhlcaGyTWOrBUOPG1K1zGt+FrO5KS5zGreJCMr/u+6t6MT0Q+wbaZKzDDiE1/kg+YO+T89EV6oAAAAeJxdxjkOgCAUANE/uOOGB+FQBIjaaEJIuL6FsfE1M6Lk9fXPoKioaWjp6BnQjEzMLKwYNtHepZhtuMs1vpvO/ch4HIlIxhK4KVyc7BwiD8nvDlkA') format('woff')}[class*=' luna-object-viewer-icon-'],[class^=luna-object-viewer-icon-]{display:inline-block;font-family:luna-object-viewer-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.luna-object-viewer-icon-caret-down:before{content:'\f101'}.luna-object-viewer-icon-caret-right:before{content:'\f102'}.luna-object-viewer{overflow-x:auto;-webkit-overflow-scrolling:touch;overflow-y:hidden;cursor:default;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;font-size:12px;line-height:1.2;min-height:100%;color:#333;list-style:none!important}.luna-object-viewer ul{list-style:none!important;padding:0!important;padding-left:12px!important;margin:0!important}.luna-object-viewer li{position:relative;white-space:nowrap;line-height:16px;min-height:16px}.luna-object-viewer>li>.luna-object-viewer-key{display:none}.luna-object-viewer span{position:static!important}.luna-object-viewer li .luna-object-viewer-collapsed~.luna-object-viewer-close:before{color:#999}.luna-object-viewer-array .luna-object-viewer-object .luna-object-viewer-key{display:inline}.luna-object-viewer-null{color:#5e5e5e}.luna-object-viewer-regexp,.luna-object-viewer-string{color:#c41a16}.luna-object-viewer-number{color:#1c00cf}.luna-object-viewer-boolean{color:#0d22aa}.luna-object-viewer-special{color:#5e5e5e}.luna-object-viewer-key,.luna-object-viewer-key-lighter{color:#881391}.luna-object-viewer-key-lighter{opacity:.6}.luna-object-viewer-key-special{color:#5e5e5e}.luna-object-viewer-collapsed .luna-object-viewer-icon,.luna-object-viewer-expanded .luna-object-viewer-icon{position:absolute!important;left:-12px;color:#727272;font-size:12px}.luna-object-viewer-icon-caret-right{top:0}.luna-object-viewer-icon-caret-down{top:1px}.luna-object-viewer-expanded>.luna-object-viewer-icon-caret-down{display:inline}.luna-object-viewer-expanded>.luna-object-viewer-icon-caret-right{display:none}.luna-object-viewer-collapsed>.luna-object-viewer-icon-caret-down{display:none}.luna-object-viewer-collapsed>.luna-object-viewer-icon-caret-right{display:inline}.luna-object-viewer-hidden~ul{display:none}.luna-object-viewer-theme-dark{color:#fff}.luna-object-viewer-theme-dark .luna-object-viewer-null,.luna-object-viewer-theme-dark .luna-object-viewer-special{color:#a1a1a1}.luna-object-viewer-theme-dark .luna-object-viewer-regexp,.luna-object-viewer-theme-dark .luna-object-viewer-string{color:#f28b54}.luna-object-viewer-theme-dark .luna-object-viewer-boolean,.luna-object-viewer-theme-dark .luna-object-viewer-number{color:#9980ff}.luna-object-viewer-theme-dark .luna-object-viewer-key,.luna-object-viewer-theme-dark .luna-object-viewer-key-lighter{color:#5db0d7}@font-face{font-family:luna-dom-viewer-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,d09GRgABAAAAAAS8AAsAAAAAB7QAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAABHU1VCAAABCAAAAGEAAACMISgl+k9TLzIAAAFsAAAAPQAAAFZLxUkWY21hcAAAAawAAADWAAACdBU42qdnbHlmAAAChAAAAC4AAAAwabU7V2hlYWQAAAK0AAAALwAAADZzjr4faGhlYQAAAuQAAAAYAAAAJAFyANlobXR4AAAC/AAAABAAAABAAZAAAGxvY2EAAAMMAAAAEAAAACIAtACobWF4cAAAAxwAAAAfAAAAIAEbAA9uYW1lAAADPAAAASkAAAIWm5e+CnBvc3QAAARoAAAAUwAAAHZW8MNZeJxNjTsOQFAQRc/z/+sV1mABohKV0gZeJRJR2X9cT4RJZu7nFIMBMjoGvHGaF6rdngcNAc/c/O/Nvq2W5E1igdNE2zv1iGh1c5FQPlYXUlJRyxt9+/pUKadQa/AveGEGZQAAAHicY2BkkGScwMDKwMBQx9ADJGWgdAIDJ4MxAwMTAyszA1YQkOaawnCAQfcjE8MJIFcITDIwMIIIAFqDCGkAAAB4nM2STQ4BQRCFv54ZP8MwFhYW4gQcShBsSERi50BWDuFCcwJedddKRGKnOt8k9aanqudVAy0gF3NRQLgTsLhJDVHP6UW94Kp8zEhKwYIlG/YcOXHm0mTPp96aumLLwdUQ1fcIqmJrwpSZL+iqak5JmyE1Ayr1bdGhr/2ZPmp/qPQtuj/uJzqQl+pfDyypesQD6AT/ElV8PjyrMccT9rdLR3PUFBI227VTio1jbm6dodg5VnPvmAsHxzofHfmi+Sbs/pwdWcXFkWdNSNg9arIE2QufuSCyAAB4nGNgZACBlQzTGZgYGMyVxVc2O073AIpAxHsYloHFRc2dPZY2OTIwAACmEQesAAB4nGNgZGBgAOINe2b6x/PbfGXgZjgBFIjifLyvAUEDwUqGZUCSg4EJxAEAUn4LLAB4nGNgZGBgOMHAACdXMjAyoAIBADizAkx4nGNgAIITUEwGAABZUAGReJxjYAACHgYJ3BAAE94BXXicY2BkYGAQYGBmANEMDExAzAWEDAz/wXwGAApcASsAeJxlkD1uwkAUhMdgSAJSghQpKbNVCiKZn5IDQE9Bl8KYtTGyvdZ6QaLLCXKEHCGniHKCHChj82hgLT9/M2/e7soABviFh3p5uG1qvVq4oTpxm/Qg7JOfhTvo40W4S38o3MMbpsJ9POKdO3j+HZ0BSuEW7vEh3Kb/KeyTv4Q7eMK3cJf+j3APK/wJ9/HqDdPIFLEp3FIn+yy0Z3n+rrStUlOoSTA+WwtdaBs6vVHro6oOydS5WMXW5GrOrs4yo0prdjpywda5cjYaxeIHkcmRIoJBgbipDktoJNgjQwh71b3UK6YtKvq1VpggwPgqtWCqaJIhlcaGyTWOrBUOPG1K1zGt+FrO5KS5zGreJCMr/u+6t6MT0Q+wbaZKzDDiE1/kg+YO+T89EV6oAAAAeJxdxjkOgCAUANE/uOOGB+FQBIjaaEJIuL6FsfE1M6Lk9fXPoKioaWjp6BnQjEzMLKwYNtHepZhtuMs1vpvO/ch4HIlIxhK4KVyc7BwiD8nvDlkA') format('woff')}[class*=' luna-dom-viewer-icon-'],[class^=luna-dom-viewer-icon-]{display:inline-block;font-family:luna-dom-viewer-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.luna-dom-viewer-icon-caret-down:before{content:'\f101'}.luna-dom-viewer-icon-caret-right:before{content:'\f102'}.luna-dom-viewer{padding:0 0 0 12px;cursor:default;list-style:none;min-width:100%;color:rgba(0,0,0,.88);color:var(--luna-color-text,rgba(0,0,0,.88));background-color:rgba(0,0,0,0);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";font-family:var(--luna-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji");box-sizing:border-box;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;font-size:14px}.luna-dom-viewer .luna-dom-viewer-hidden,.luna-dom-viewer.luna-dom-viewer-hidden{display:none}.luna-dom-viewer .luna-dom-viewer-invisible,.luna-dom-viewer.luna-dom-viewer-invisible{visibility:hidden}.luna-dom-viewer *{box-sizing:border-box}.luna-dom-viewer.luna-dom-viewer-theme-dark{color-scheme:dark;color:hsla(0,0%,100%,.85);color:var(--luna-color-text-dark,rgba(255,255,255,.85));background-color:rgba(0,0,0,0)}.luna-dom-viewer{font-size:12px;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace}.luna-dom-viewer ul{display:inline-block}.luna-dom-viewer-toggle{min-width:12px;margin-left:-12px}.luna-dom-viewer-icon-caret-down,.luna-dom-viewer-icon-caret-right{position:absolute!important;font-size:12px!important}.luna-dom-viewer-tree-item{min-width:200px;line-height:16px;min-height:16px;position:relative;z-index:10;outline:0}.luna-dom-viewer-tree-item.luna-dom-viewer-selected .luna-dom-viewer-selection,.luna-dom-viewer-tree-item:hover .luna-dom-viewer-selection{display:block}.luna-dom-viewer-tree-item .luna-dom-viewer-icon-caret-down{display:none}.luna-dom-viewer-tree-item.luna-dom-viewer-expanded .luna-dom-viewer-icon-caret-down{display:inline-block}.luna-dom-viewer-tree-item.luna-dom-viewer-expanded .luna-dom-viewer-icon-caret-right{display:none}.luna-dom-viewer-attribute-value{word-break:break-all}.luna-dom-viewer-attribute-value.luna-dom-viewer-attribute-underline{text-decoration:underline}.luna-dom-viewer-selection{position:absolute;display:none;left:-10000px;right:0;top:0;bottom:0;z-index:-1}.luna-dom-viewer-children{margin:0;overflow-x:visible;overflow-y:visible;padding-left:15px}.luna-dom-viewer-theme-light .luna-dom-viewer-icon-caret-down,.luna-dom-viewer-theme-light .luna-dom-viewer-icon-caret-right{color:#9aa0a6}.luna-dom-viewer-theme-light .luna-dom-viewer-html-tag,.luna-dom-viewer-theme-light .luna-dom-viewer-tag-name{color:#881280}.luna-dom-viewer-theme-light .luna-dom-viewer-attribute-name{color:#994500}.luna-dom-viewer-theme-light .luna-dom-viewer-attribute-value{color:#1a1aa6}.luna-dom-viewer-theme-light .luna-dom-viewer-html-comment{color:#236e25}.luna-dom-viewer-theme-light .luna-dom-viewer-tree-item:hover .luna-dom-viewer-selection{background:#e8eaed}.luna-dom-viewer-theme-light .luna-dom-viewer-tree-item.luna-dom-viewer-selected .luna-dom-viewer-selection{background:#e0e0e0}.luna-dom-viewer-theme-light .luna-dom-viewer-tree-item.luna-dom-viewer-selected:focus .luna-dom-viewer-selection{background:#cfe8fc}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node{word-break:break-all}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node .luna-dom-viewer-keyword{color:#881280}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node .luna-dom-viewer-number{color:#1c00cf}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node .luna-dom-viewer-operator{color:gray}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node .luna-dom-viewer-comment{color:#236e25}.luna-dom-viewer-theme-light .luna-dom-viewer-text-node .luna-dom-viewer-string{color:#1a1aa6}.luna-dom-viewer-theme-dark{color:#e8eaed}.luna-dom-viewer-theme-dark .luna-dom-viewer-icon-caret-down,.luna-dom-viewer-theme-dark .luna-dom-viewer-icon-caret-right{color:#9aa0a6}.luna-dom-viewer-theme-dark .luna-dom-viewer-html-tag,.luna-dom-viewer-theme-dark .luna-dom-viewer-tag-name{color:#5db0d7}.luna-dom-viewer-theme-dark .luna-dom-viewer-attribute-name{color:#9bbbdc}.luna-dom-viewer-theme-dark .luna-dom-viewer-attribute-value{color:#f29766}.luna-dom-viewer-theme-dark .luna-dom-viewer-html-comment{color:#898989}.luna-dom-viewer-theme-dark .luna-dom-viewer-tree-item:hover .luna-dom-viewer-selection{background:#083c69}.luna-dom-viewer-theme-dark .luna-dom-viewer-tree-item.luna-dom-viewer-selected .luna-dom-viewer-selection{background:#454545}.luna-dom-viewer-theme-dark .luna-dom-viewer-tree-item.luna-dom-viewer-selected:focus .luna-dom-viewer-selection{background:#073d69}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node{word-break:break-all}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node .luna-dom-viewer-keyword{color:#e36eec}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node .luna-dom-viewer-number{color:#9980ff}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node .luna-dom-viewer-operator{color:#7f7f7f}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node .luna-dom-viewer-comment{color:#747474}.luna-dom-viewer-theme-dark .luna-dom-viewer-text-node .luna-dom-viewer-string{color:#f29766}@font-face{font-family:luna-text-viewer-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,d09GRgABAAAAAAS0AAsAAAAAB2QAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAABHU1VCAAABCAAAAFQAAAB0INElr09TLzIAAAFcAAAAPQAAAFZL+0klY21hcAAAAZwAAACfAAACEAEewxRnbHlmAAACPAAAAIYAAACkNSDggmhlYWQAAALEAAAALgAAADZzrb4oaGhlYQAAAvQAAAAWAAAAJAGRANNobXR4AAADDAAAABAAAAAoAZAAAGxvY2EAAAMcAAAAEAAAABYBWgFIbWF4cAAAAywAAAAdAAAAIAEXADtuYW1lAAADTAAAASkAAAIWm5e+CnBvc3QAAAR4AAAAOwAAAFJIWdOleJxjYGRgYOBiMGCwY2BycfMJYeDLSSzJY5BiYGGAAJA8MpsxJzM9kYEDxgPKsYBpDiBWAdNMDGwMQkAWK1CGlYEZyGMCstiBMpxAUUYGZgDbGgXDeJxjYGTQYJzAwMrAwFDH0AMkZaB0AgMngzEDAxMDKzMDVhCQ5prCcIAh+SMTwwkgVwhMMjAwgggAY84IrgAAAHicvZFLCsMwDERHzsdJ6aL0HD1VQiDQRbIN9Axd9aI+QTpjq5Bdd5F4Bo1lybIBNAAq8iA1YB8YZG+qlvUKl6zXGBjf6MofMWHGEyu2FPb9oCxULCtHs3yy+J2urg1rtojo0HM/MKnFGabOGlbdYvdT+1N6/7drXl8e6Vajo3efHP3b7HAUvntBMy1OJKujMTeHNZMV9McpFBC+tLgY4QB4nGNgZACBEwzrGdgZGOwZxdnVDdXNPfKEGlhchO0KhZtZ3IQYmMFq1jCsZpBi0GLQY2AwNzGzZjQSk2UUYdNmVFID8UyVRUXYlNRMlVGlTM1FjU3tmZkTmVhYmFRBhHwoCyuzKgtTIjMzWJg3ZClIGMRlZQmVB7GhMixM0aGhQIsB52sTqgAAeJxjYGRgYADi2JNxkvH8Nl8ZuBlOAAWiOB/va0DQQHCCYT2Q5GBgAnEANJ0KnQAAeJxjYGRgYDjBwIBEMjKgAi4AOvoCZQAAeJxjYACCE1CMBwAAM7gBkXicY2AAAiGGIFQIABXIAqN4nGNgZGBg4GLQZ2BmAAEmMI8LSP4H8xkADjQBUwAAAHicZZA9bsJAFITHYEgCUoIUKSmzVQoimZ+SA0BPQZfCmLUxsr3WekGiywlyhBwhp4hyghwoY/NoYC0/fzNv3u7KAAb4hYd6ebhtar1auKE6cZv0IOyTn4U76ONFuEt/KNzDG6bCfTzinTt4/h2dAUrhFu7xIdym/ynsk7+EO3jCt3CX/o9wDyv8Cffx6g3TyBSxKdxSJ/sstGd5/q60rVJTqEkwPlsLXWgbOr1R66OqDsnUuVjF1uRqzq7OMqNKa3Y6csHWuXI2GsXiB5HJkSKCQYG4qQ5LaCTYI0MIe9W91CumLSr6tVaYIMD4KrVgqmiSIZXGhsk1jqwVDjxtStcxrfhazuSkucxq3iQjK/7vurejE9EPsG2mSsww4hNf5IPmDvk/PRFeqAAAAHicXcU7CsAgFEXBe4x/l/kQBAtt3X0KSZNpRk7X91/F8eAJRBKZQqUp2Og2va19MAadyWJzpBd4kgcWAA==') format('woff')}[class*=' luna-text-viewer-icon-'],[class^=luna-text-viewer-icon-]{display:inline-block;font-family:luna-text-viewer-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.luna-text-viewer-icon-check:before{content:'\f101'}.luna-text-viewer-icon-copy:before{content:'\f102'}.luna-text-viewer{color:#333;background-color:#fff;font-family:Arial,Helvetica,sans-serif;box-sizing:border-box;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;font-size:14px;padding:0;unicode-bidi:embed;position:relative;overflow:auto;border:1px solid #ccc}.luna-text-viewer.luna-text-viewer-platform-windows{font-family:'Segoe UI',Tahoma,sans-serif}.luna-text-viewer.luna-text-viewer-platform-linux{font-family:Roboto,Ubuntu,Arial,sans-serif}.luna-text-viewer .luna-text-viewer-hidden,.luna-text-viewer.luna-text-viewer-hidden{display:none}.luna-text-viewer .luna-text-viewer-invisible,.luna-text-viewer.luna-text-viewer-invisible{visibility:hidden}.luna-text-viewer *{box-sizing:border-box}.luna-text-viewer.luna-text-viewer-theme-dark{color:#d9d9d9;border-color:#3d3d3d;background:#242424}.luna-text-viewer:hover .luna-text-viewer-copy{opacity:1}.luna-text-viewer-table{display:table}.luna-text-viewer-table .luna-text-viewer-line-number,.luna-text-viewer-table .luna-text-viewer-line-text{padding:0}.luna-text-viewer-table-row{display:table-row}.luna-text-viewer-line-number{display:table-cell;padding:0 3px 0 8px!important;text-align:right;vertical-align:top;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;border-right:1px solid #ccc}.luna-text-viewer-line-text{display:table-cell;padding-left:4px!important;-webkit-user-select:text;-moz-user-select:text;-ms-user-select:text;user-select:text}.luna-text-viewer-copy{background:#fff;opacity:0;position:absolute;right:5px;top:5px;border:1px solid #ccc;border-radius:4px;width:25px;height:25px;text-align:center;line-height:25px;cursor:pointer;transition:opacity .3s,top .3s}.luna-text-viewer-copy .luna-text-viewer-icon-check{color:#188037}.luna-text-viewer-text{padding:4px;font-size:12px;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;box-sizing:border-box;white-space:pre;display:block}.luna-text-viewer-text.luna-text-viewer-line-numbers{padding:0}.luna-text-viewer-text.luna-text-viewer-wrap-long-lines{white-space:pre-wrap}.luna-text-viewer-text.luna-text-viewer-wrap-long-lines .luna-text-viewer-line-text{word-break:break-all}.luna-text-viewer-theme-dark{color-scheme:dark}.luna-text-viewer-theme-dark .luna-text-viewer-copy,.luna-text-viewer-theme-dark .luna-text-viewer-line-number{border-color:#3d3d3d}.luna-text-viewer-theme-dark .luna-text-viewer-copy .luna-text-viewer-icon-check{color:#81c995}.luna-text-viewer-theme-dark .luna-text-viewer-copy{background-color:#242424}@font-face{font-family:luna-notification-icon;src:url('data:application/x-font-woff;charset=utf-8;base64,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') format('woff')}[class*=' luna-notification-icon-'],[class^=luna-notification-icon-]{display:inline-block;font-family:luna-notification-icon!important;font-size:16px;font-style:normal;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.luna-notification-icon-info:before{content:'\f101'}.luna-notification-icon-check:before{content:'\f102'}.luna-notification-icon-warn:before{content:'\f103'}.luna-notification-icon-error:before{content:'\f104'}.luna-notification{position:relative;padding:20px;pointer-events:none;display:flex;flex-direction:column;overflow:hidden;color:rgba(0,0,0,.88);color:var(--luna-color-text,rgba(0,0,0,.88));background-color:rgba(0,0,0,0);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";font-family:var(--luna-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji");box-sizing:border-box;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;font-size:14px}.luna-notification .luna-notification-hidden,.luna-notification.luna-notification-hidden{display:none}.luna-notification .luna-notification-invisible,.luna-notification.luna-notification-invisible{visibility:hidden}.luna-notification *{box-sizing:border-box}.luna-notification.luna-notification-theme-dark{color-scheme:dark;color:hsla(0,0%,100%,.85);color:var(--luna-color-text-dark,rgba(255,255,255,.85));background-color:rgba(0,0,0,0)}.luna-notification.luna-notification-full{position:fixed;top:0;left:0;width:100%;height:100%}.luna-notification-item{display:flex;border:1px solid;padding:10px 16px;align-items:center}.luna-notification-lower{margin-top:16px}.luna-notification-upper{margin-bottom:16px}.luna-notification-icon-container{margin-right:8px;color:#fff;border-radius:50%;width:16px;height:16px;text-align:center;line-height:16px}.luna-notification-icon-container.luna-notification-info .luna-notification-icon{position:relative;top:-2px;font-size:12px}.luna-notification-icon-container.luna-notification-success .luna-notification-icon{position:relative;top:-1px;font-size:12px}.luna-notification-icon-container.luna-notification-warning{position:relative;top:-2px}.luna-notification-icon-container.luna-notification-warning .luna-notification-icon{font-size:14px}.luna-notification-icon-container.luna-notification-error{position:relative;top:-1px}.luna-notification-icon-container.luna-notification-error .luna-notification-icon{font-size:14px}.luna-notification-theme-light .luna-notification-item{border-color:#d9d9d9;border-color:var(--luna-color-border,#d9d9d9);box-shadow:0 6px 16px 0 rgba(0,0,0,.08),0 3px 6px -4px rgba(0,0,0,.12),0 9px 28px 8px rgba(0,0,0,.05);box-shadow:var(--luna-box-shadow,0 6px 16px 0 rgba(0,0,0,.08),0 3px 6px -4px rgba(0,0,0,.12),0 9px 28px 8px rgba(0,0,0,.05));color:rgba(0,0,0,.88);color:var(--luna-color-text,rgba(0,0,0,.88));background-color:#fff;background-color:var(--luna-color-bg-container,#fff)}.luna-notification-theme-light .luna-notification-icon-container.luna-notification-info{background-color:#1677ff;background-color:var(--luna-color-info,#1677ff)}.luna-notification-theme-light .luna-notification-icon-container.luna-notification-success{background-color:#52c41a;background-color:var(--luna-color-success,#52c41a)}.luna-notification-theme-light .luna-notification-icon-container.luna-notification-warning{color:#faad14;color:var(--luna-color-warning,#faad14)}.luna-notification-theme-light .luna-notification-icon-container.luna-notification-error{color:#ff4d4f;color:var(--luna-color-error,#ff4d4f)}.luna-notification-theme-dark .luna-notification-item{border-color:#424242;border-color:var(--luna-color-border,#424242);box-shadow:0 6px 16px 0 rgba(0,0,0,.08),0 3px 6px -4px rgba(0,0,0,.12),0 9px 28px 8px rgba(0,0,0,.05);box-shadow:var(--luna-box-shadow,0 6px 16px 0 rgba(0,0,0,.08),0 3px 6px -4px rgba(0,0,0,.12),0 9px 28px 8px rgba(0,0,0,.05));color:hsla(0,0%,100%,.85);color:var(--luna-color-text,rgba(255,255,255,.85));background-color:#141414;background-color:var(--luna-color-bg-container,#141414)}.luna-notification-theme-dark .luna-notification-icon-container.luna-notification-info{background-color:#1668dc;background-color:var(--luna-color-info,#1668dc)}.luna-notification-theme-dark .luna-notification-icon-container.luna-notification-success{background-color:#49aa19;background-color:var(--luna-color-success,#49aa19)}.luna-notification-theme-dark .luna-notification-icon-container.luna-notification-warning{color:#d89614;color:var(--luna-color-warning,#d89614)}.luna-notification-theme-dark .luna-notification-icon-container.luna-notification-error{color:#dc4446;color:var(--luna-color-error,#dc4446)}</style></head>
<body>
<div id="video-container" class="relative">
    <video id="video" class="w-full h-full object-cover" autoplay="" playsinline="" style="--cue-bottom:80px" disableremoteplayback=""></video>
    <div id="skip-hint" class="text-white"></div>
    <div id="loading-indicator" class="absolute inset-0 flex items-center justify-center bg-black/50 z-30 hidden">
        <img src="https://assets.nflxext.com/en_us/pages/wiplayer/site-spinner.png" class="w-20 h-20 rounded-full shadow-lg" alt="Loading">
    </div>
    <div id="top-overlay" class="absolute inset-0 cursor-pointer z-10"></div>
    <div id="center-play-pause-overlay" class="flex-col absolute left-1/2 right-1/2 inset-0 flex items-center justify-center z-10 transition-opacity duration-500 opacity-100 pointer-events-auto">
        <div id="center-controls-mobile-only" class="flex justify-center items-center">
            <button id="mobile-skip-backward-button" class="xl:hidden text-white hover:opacity-80 transition-opacity duration-200 focus:outline-none">
                <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-10 h-10 md:w-14 md:h-14" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M11.02 2.05A10 10 0 1 1 2 12H0a12 12 0 1 0 5-9.75V1H3v4a1 1 0 0 0 1 1h4V4H6a10 10 0 0 1 5.02-1.95M2 4v3h3v2H1a1 1 0 0 1-1-1V4zm12.13 12q-.88 0-1.53-.42-.64-.44-1-1.22a5 5 0 0 1-.35-1.86q0-1.05.35-1.85.36-.79 1-1.22A2.7 2.7 0 0 1 14.13 9a2.65 2.65 0 0 1 2.52 1.65q.35.79.35 1.85 0 1.07-.35 1.86a3 3 0 0 1-1.01 1.22 2.7 2.7 0 0 1-1.52.42m0-1.35q.59 0 .91-.56.34-.56.34-1.59 0-1.01-.34-1.58-.33-.57-.91-.57-.6 0-.92.57-.34.56-.34 1.58t.34 1.6q.33.54.91.55m-5.53 1.2v-5.13l-1.6.42V9.82l3.2-.8v6.84z" clip-rule="evenodd"></path></svg>
            </button>
            <button id="center-play-pause-button" class="text-white md:p-4 hover:opacity-80 transition-opacity duration-200 focus:outline-none">
                <svg id="center-play-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-12 h-12 md:w-16 md:h-16" viewBox="0 0 24 24"><path fill="currentColor" d="M5 2.7a1 1 0 0 1 1.48-.88l16.93 9.3a1 1 0 0 1 0 1.76l-16.93 9.3A1 1 0 0 1 5 21.31z"></path></svg>
                <svg id="center-pause-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="hidden w-12 h-12 md:w-16 md:h-16" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M4.5 3a.5.5 0 0 0-.5.5v17c0 .28.22.5.5.5h5a.5.5 0 0 0 .5-.5v-17a.5.5 0 0 0-.5-.5zm10 0a.5.5 0 0 0-.5.5v17c0 .28.22.5.5.5h5a.5.5 0 0 0 .5-.5v-17a.5.5 0 0 0-.5-.5z" clip-rule="evenodd"></path></svg>
            </button>
            <button id="mobile-skip-forward-button" class="xl:hidden text-white hover:opacity-80 transition-opacity duration-200 focus:outline-none space-x-6">
                <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-10 h-10 md:w-14 md:h-14" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M6.44 3.69A10 10 0 0 1 18 4h-2v2h4a1 1 0 0 0 1-1V1h-2v1.25A12 12 0 1 0 24 12h-2A10 10 0 1 1 6.44 3.69M22 4v3h-3v2h4a1 1 0 0 0 1-1V4zm-9.4 11.58q.66.42 1.53.42a2.7 2.7 0 0 0 1.5-.42q.67-.44 1.02-1.22.35-.8.35-1.86 0-1.05-.35-1.85A2.65 2.65 0 0 0 14.13 9a2.7 2.7 0 0 0-1.53.43q-.64.44-1 1.22a4.5 4.5 0 0 0-.35 1.85q0 1.07.35 1.86.36.78 1 1.22m2.44-1.49q-.33.56-.91.56-.6 0-.92-.56-.34-.56-.34-1.59 0-1.01.34-1.58.33-.57.91-.57.6 0 .92.57.34.56.34 1.58t-.34 1.6zM8.6 10.72v5.14h1.6V9.02l-3.2.8v1.32z" clip-rule="evenodd"></path></svg>
            </button>
        </div>
    </div>
    <div id="bottom-overlay" class="absolute inset-0 flex flex-col justify-end transition-opacity duration-500 controls-visible z-20 pointer-events-none">
        <div id="controls-bar" class="w-full bg-gradient-to-t from-black/70 to-transparent flex flex-col space-y-2 md:space-y-3 pointer-events-auto">
            <div id="top-bar" class="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-6 transition-opacity duration-500 controls-visible" style="height:4.5rem">
                <button id="back-button" class="text-white hover:opacity-80 transition-opacity duration-500 focus:outline-none flex-shrink-0 flex items-center justify-center" style="width:2.2rem;height:2.2rem" onclick="(function(){if(document.fullscreenElement&amp;&amp;window.innerWidth&lt;1000){document.exitFullscreen();}else{window.history.back();}})()">
                    <svg viewBox="0 0 24 24" width="2.2rem" height="2.2rem" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M6.414 11H21v2H6.414l5.293 5.293-1.414 1.414-7-7a1 1 0 0 1 0-1.414l7-7 1.414 1.414z" clip-rule="evenodd"></path></svg>
                </button>
                <div id="mobile-title" class="flex flex-col items-center pointer-events-none" style="max-width:55vw">
                    <span id="mobile-title-main" class="text-white font-medium text-sm leading-tight text-center" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%"></span>
                </div>
                <button id="report-button" class="text-white hover:opacity-80 transition-opacity duration-500 focus:outline-none flex-shrink-0 flex items-center justify-center" style="width:2.2rem;height:2.2rem">
                    <svg viewBox="0 0 24 24" width="2.2rem" height="2.2rem" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M3 2a1 1 0 0 0-1 1v19h2V10.579c1.85.029 3.241.142 5 .334v2.658a1 1 0 0 0 .726.962C13.026 15.473 15.873 16 21 16a1 1 0 0 0 1-1V8.429a1 1 0 0 0-1-1c-2.383 0-3.939-.117-6-.342V4.43a1 1 0 0 0-.726-.962C10.974 2.528 8.127 2 3 2m1 6.579c2.257.034 3.859.188 6.113.446l.887.101v3.685c2.616.706 5.052 1.123 9 1.182V9.42c-2.257-.034-3.859-.188-6.113-.446l-.887-.1V5.189c-2.616-.706-5.051-1.123-9-1.182z" clip-rule="evenodd"></path></svg>
                </button>
            </div>
            <div id="timeline-row" class="flex items-center space-x-2 md:space-x-4 w-full">
                <div id="seek-bar" class="relative flex-grow bg-white/30 group">
                    <div id="buffer-indicator" class="absolute inset-y-0 left-0 bg-white/50 transition-all duration-100" style="width:0%"></div>
                    <div id="progress-indicator" class="absolute inset-y-0 left-0 transition-all duration-100" style="width:0%"></div>
                    <div id="seek-thumb" class="absolute top-1/2 -translate-y-1/2 rounded-full transition-transform duration-150" style="left:0%"></div>
                </div>
                <div class="flex items-center space-x-1 flex-shrink-0">
                    <span id="remaining-time" class="text-white text-xs md:text-sm font-medium select-none w-10 md:w-12 text-center">0:00</span>
                </div>
            </div>
            <div id="bottom-controls-row" class="flex items-center justify-between" style="position:relative">
                <div id="title-display"><span class="title-main" id="title-main-text"></span></div>
                <div id="left-controlbuttons" class="flex items-center space-x-1 md:space-x-2">
                    <button id="custom-play-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 focus:outline-none">
                        <svg id="play-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" d="M5 2.7a1 1 0 0 1 1.48-.88l16.93 9.3a1 1 0 0 1 0 1.76l-16.93 9.3A1 1 0 0 1 5 21.31z"></path></svg>
                        <svg id="pause-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white hidden w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M4.5 3a.5.5 0 0 0-.5.5v17c0 .28.22.5.5.5h5a.5.5 0 0 0 .5-.5v-17a.5.5 0 0 0-.5-.5zm10 0a.5.5 0 0 0-.5.5v17c0 .28.22.5.5.5h5a.5.5 0 0 0 .5-.5v-17a.5.5 0 0 0-.5-.5z" clip-rule="evenodd"></path></svg>
                    </button>
                    <button id="skip-backward-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 focus:outline-none">
                        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M11.02 2.05A10 10 0 1 1 2 12H0a12 12 0 1 0 5-9.75V1H3v4a1 1 0 0 0 1 1h4V4H6a10 10 0 0 1 5.02-1.95M2 4v3h3v2H1a1 1 0 0 1-1-1V4zm12.13 12q-.88 0-1.53-.42-.64-.44-1-1.22a5 5 0 0 1-.35-1.86q0-1.05.35-1.85.36-.79 1-1.22A2.7 2.7 0 0 1 14.13 9a2.65 2.65 0 0 1 2.52 1.65q.35.79.35 1.85 0 1.07-.35 1.86a3 3 0 0 1-1.01 1.22 2.7 2.7 0 0 1-1.52.42m0-1.35q.59 0 .91-.56.34-.56.34-1.59 0-1.01-.34-1.58-.33-.57-.91-.57-.6 0-.92.57-.34.56-.34 1.58t.34 1.6q.33.54.91.55m-5.53 1.2v-5.13l-1.6.42V9.82l3.2-.8v6.84z" clip-rule="evenodd"></path></svg>
                    </button>
                    <button id="skip-forward-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 focus:outline-none">
                        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M6.44 3.69A10 10 0 0 1 18 4h-2v2h4a1 1 0 0 0 1-1V1h-2v1.25A12 12 0 1 0 24 12h-2A10 10 0 1 1 6.44 3.69M22 4v3h-3v2h4a1 1 0 0 0 1-1V4zm-9.4 11.58q.66.42 1.53.42a2.7 2.7 0 0 0 1.5-.42q.67-.44 1.02-1.22.35-.8.35-1.86 0-1.05-.35-1.85A2.65 2.65 0 0 0 14.13 9a2.7 2.7 0 0 0-1.53.43q-.64.44-1 1.22a4.5 4.5 0 0 0-.35 1.85q0 1.07.35 1.86.36.78 1 1.22m2.44-1.49q-.33.56-.91.56-.6 0-.92-.56-.34-.56-.34-1.59 0-1.01.34-1.58.33-.57.91-.57.6 0 .92.57.34.56.34 1.58t-.34 1.6zM8.6 10.72v5.14h1.6V9.02l-3.2.8v1.32z" clip-rule="evenodd"></path></svg>
                    </button>
                    <div id="volume-control-wrapper" class="relative flex items-center h-10 md:h-9">
                        <div id="volume-slider-container" class="absolute bottom-12 left-1/2 -translate-x-1/2 p-3 bg-black/80 rounded-lg shadow-2xl hidden transition-all duration-200">
                            <div id="volume-slider-track" class="relative w-2 h-24 rounded-full cursor-pointer">
                                <div id="volume-level" class="absolute bottom-0 left-0 right-0 rounded-full" style="background: rgb(225, 0, 0); height: 100%;"></div>
                                <div id="volume-thumb-control" class="absolute left-1/2 -translate-x-1/2 w-4 h-4 rounded-full" style="bottom: calc(100% - 8px); background: rgb(225, 0, 0);"></div>
                            </div>
                        </div>
                        <button id="mute-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 cursor-pointer focus:outline-none z-30">
                            <svg id="volume-low-icon" viewBox="0 0 24 24" width="100%" height="100%" class="text-white hidden w-6 h-6 md:w-full md:h-full" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M11 4a1 1 0 0 0-1.7-.7L4.58 8H1a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h3.59l4.7 4.7A1 1 0 0 0 11 20zM5.7 9.7 9 6.42V17.6l-3.3-3.3-.29-.29H2v-4h3.41zM16 12a6 6 0 0 0-1.76-4.24l-1.41 1.41a4 4 0 0 1 0 5.66l1.41 1.41A6 6 0 0 0 16 12" clip-rule="evenodd"></path></svg>
                            <svg id="volume-medium-icon" viewBox="0 0 24 24" width="100%" height="100%" class="text-white hidden w-6 h-6 md:w-full md:h-full" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M11 4a1 1 0 0 0-1.7-.7L4.58 8H1a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h3.59l4.7 4.7A1 1 0 0 0 11 20zM5.7 9.7 9 6.42V17.6l-3.3-3.3-.29-.29H2v-4h3.41zm11.37-4.77a10 10 0 0 1 0 14.14l-1.41-1.41a8 8 0 0 0 0-11.32zm-2.83 2.83a6 6 0 0 1 0 8.48l-1.41-1.41a4 4 0 0 0 0-5.66z" clip-rule="evenodd"></path></svg>
                            <svg id="volume-high-icon" viewBox="0 0 24 24" width="100%" height="100%" class="text-white w-6 h-6 md:w-full md:h-full" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M24 12a14 14 0 0 0-4.1-9.9l-1.415 1.415a12 12 0 0 1 0 16.97L19.9 21.9A14 14 0 0 0 24 12M11 4a1 1 0 0 0-1.707-.707L4.586 8H1a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h3.586l4.707 4.707A1 1 0 0 0 11 20zM5.707 9.707 9 6.414v11.172l-3.293-3.293L5.414 14H2v-4h3.414zM16 12a6 6 0 0 0-1.757-4.243l-1.415 1.415a4 4 0 0 1 0 5.656l1.415 1.415A6 6 0 0 0 16 12m1.07-7.071a10 10 0 0 1 0 14.142l-1.413-1.414a8 8 0 0 0 0-11.314z" clip-rule="evenodd"></path></svg>
                            <svg id="volume-off-icon" viewBox="0 0 24 24" width="100%" height="100%" class="text-white w-6 h-6 md:w-full md:h-full hidden" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#FFFFFF" fill-rule="evenodd" d="M11 4a1 1 0 0 0-1.7-.7L4.58 8H1a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h3.59l4.7 4.7A1 1 0 0 0 11 20zM5.7 9.7 9 6.42V17.6l-3.3-3.3-.29-.29H2v-4h3.41zm9.6 0 2.29 2.3-2.3 2.3 1.42 1.4L19 13.42l2.3 2.3 1.4-1.42-2.28-2.3 2.3-2.3-1.42-1.4-2.3 2.28-2.3-2.3z" clip-rule="evenodd"></path></svg>
                        </button>
                    </div>
                </div>
                <div id="right-controlbuttons" class="flex items-center space-x-1 md:space-x-2 relative">
                    <button id="next-episode-button" style="display:none">
                        <span>Next Ep</span>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"></path></svg>
                    </button>
                    <div class="relative" id="audio-subtitle-wrapper">
                        <button id="audio-subtitle-toggle" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 cursor-pointer focus:outline-none mobile-labeled-btn" title="Audio &amp; Subtitles">
                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-6 h-6 md:w-full md:h-full flex-shrink-0" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M1 3a1 1 0 0 1 1-1h20a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-3v3a1 1 0 0 1-1.55.83L11.7 18H2a1 1 0 0 1-1-1zm2 1v12h9.3l.25.17L17 19.13V16h4V4zm7 5H5V7h5zm9 2h-5v2h5zm-7 2H5v-2h7zm7-6h-7v2h7z" clip-rule="evenodd"></path></svg>
                            <span class="mobile-btn-label">Audio &amp; Subtitles</span>
                        </button>
                        <div id="audio-subtitle-menu" class="absolute bottom-12 right-0 w-72 max-w-[85vw] md:w-[450px] rounded-[0.4rem] shadow-2xl p-4 hidden text-white" style="background-color:#262626">
                            <div id="audio-subtitle-menu-inner">
                                <div class="flex gap-4">
                                    <div id="audio-tracks-container" class="flex-1 flex flex-col min-h-0 pr-2">
                                        <h4 class="mb-2 text-gray-200 pb-1 flex-shrink-0" style="font-size:16px;font-weight:700">Audio</h4>
                                        <ul id="audio-list" class="space-y-1 text-sm overflow-y-auto max-h-56"><li class="text-gray-400">Loading...</li></ul>
                                    </div>
                                    <div id="subtitle-tracks-container" class="flex-1 flex flex-col min-h-0 pl-2 border-l border-gray-700">
                                        <h4 class="mb-2 text-gray-200 pb-1 flex-shrink-0" style="font-size:16px;font-weight:700">Subtitles</h4>
                                        <ul id="subtitle-list" class="space-y-1 text-sm overflow-y-auto max-h-56"><li class="text-gray-400">Loading...</li></ul>
                                    </div>
                                </div>
                            </div>
                            <div id="audio-subtitle-menu-footer" style="display:none;position:absolute;width:100%;bottom:0;right:0;background:transparent;justify-content:flex-end;gap:8px;padding:12px 16px;flex-shrink:0">
                                <button onclick="toggleAudioSubtitleMenu()" style="background:#242424;color:#fff;padding:8px 20px;font-size:14px;font-weight:700;cursor:pointer;border-radius:2px">Cancel</button>
                                <button onclick="toggleAudioSubtitleMenu()" style="background:white;border:none;color:#000;padding:8px 20px;font-size:14px;font-weight:700;cursor:pointer;border-radius:2px">Apply</button>
                            </div>
                        </div>
                    </div>
                    <button id="speed-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 cursor-pointer focus:outline-none mobile-labeled-btn" title="Playback speed">
                        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-6 h-6 md:w-full md:h-full flex-shrink-0" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M19.06 6.27a9.7 9.7 0 0 0-14.12 0 10.8 10.8 0 0 0 0 14.82L3.5 22.47a12.8 12.8 0 0 1 0-17.59 11.7 11.7 0 0 1 17 0 12.8 12.8 0 0 1 0 17.59l-1.44-1.38a10.8 10.8 0 0 0 0-14.82M15 14a3 3 0 1 1-1.7-2.7l3-3 1.4 1.4-3 3q.3.6.3 1.3" clip-rule="evenodd"></path></svg>
                        <span class="mobile-btn-label">Speed</span>
                    </button>
                    <div id="speed-menu" class="absolute bottom-12 right-0 w-48 rounded-[0.4rem] shadow-2xl p-3 hidden text-white" style="background-color:#262626"><ul id="speed-list" class="space-y-1 text-sm"></ul></div>
                    <div style="position:relative">
                        <button id="quality-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 cursor-pointer focus:outline-none mobile-labeled-btn" title="Video Quality">
                            <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="w-6 h-6 md:w-full md:h-full flex-shrink-0" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-14h2v6h-2zm0 8h2v2h-2z"></path></svg>
                            <span class="mobile-btn-label">Quality</span>
                        </button>
                        <div id="quality-menu" class="hidden"><ul id="quality-list"></ul></div>
                    </div>
                    <button id="fullscreen-button" class="bottom-control-button text-white flex items-center justify-center md:h-9 md:w-9 flex-shrink-0 cursor-pointer focus:outline-none">
                        <svg id="fullscreen-enter-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M0 5c0-1.1.9-2 2-2h7v2H2v4H0zm22 0h-7V3h7a2 2 0 0 1 2 2v4h-2zM2 15v4h7v2H2a2 2 0 0 1-2-2v-4zm20 4v-4h2v4a2 2 0 0 1-2 2h-7v-2z" clip-rule="evenodd"></path></svg>
                        <svg id="fullscreen-exit-icon" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" class="text-white hidden w-6 h-6 md:w-full md:h-full" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="M24 8h-5V3h-2v7h7zM0 16h5v5h2v-7H0zm7-6H0V8h5V3h2zm12 11v-5h5v-2h-7v7z" clip-rule="evenodd"></path></svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
    <div id="error-message" class="absolute top-0 left-1/2 -translate-x-1/2 mt-4 p-3 bg-red-800 text-white text-sm rounded-lg shadow-xl z-30">Fatal HLS error</div>
    <div class="report-modal" id="reportModal">
        <div class="report-modal-box">
            <div class="report-modal-header"><h2 class="report-modal-title">Report an Issue</h2><button class="report-close-btn" onclick="closeReportModal()">×</button></div>
            <div class="report-modal-body">
                <label for="issueType">Issue Type</label>
                <select id="issueType" __gcruniqueid="1"><option value="">Select an issue</option><option value="video">Video not playing</option><option value="audio">Audio issue</option><option value="subtitle">Subtitle issue</option><option value="buffer">Buffering or slow playback</option><option value="other">Other</option></select>
                <label for="issueDesc">Description (optional)</label>
                <textarea id="issueDesc" placeholder="Describe the problem" __gcruniqueid="2"></textarea>
            </div>
            <div class="report-modal-footer"><button class="report-submit-btn" id="submitBtn" onclick="submitIssue()" disabled="">Submit</button></div>
        </div>
    </div>
</div>
<script>
/* =====================================================================
   DOM REFS
   ===================================================================== */
const video=document.getElementById('video'),videoContainer=document.getElementById('video-container'),errorMessageDiv=document.getElementById('error-message'),topOverlay=document.getElementById('top-overlay'),bottomOverlay=document.getElementById('bottom-overlay'),customPlayButton=document.getElementById('custom-play-button'),playIcon=document.getElementById('play-icon'),pauseIcon=document.getElementById('pause-icon'),volumeControlWrapper=document.getElementById('volume-control-wrapper'),muteButton=document.getElementById('mute-button'),volumeLowIcon=document.getElementById('volume-low-icon'),volumeMediumIcon=document.getElementById('volume-medium-icon'),volumeHighIcon=document.getElementById('volume-high-icon'),volumeOffIcon=document.getElementById('volume-off-icon'),volumeSliderContainer=document.getElementById('volume-slider-container'),volumeSliderTrack=document.getElementById('volume-slider-track'),volumeLevel=document.getElementById('volume-level'),volumeThumbControl=document.getElementById('volume-thumb-control'),seekBar=document.getElementById('seek-bar'),bufferIndicator=document.getElementById('buffer-indicator'),progressIndicator=document.getElementById('progress-indicator'),seekThumb=document.getElementById('seek-thumb'),remainingTimeDisplay=document.getElementById('remaining-time'),fullscreenButton=document.getElementById('fullscreen-button'),fullscreenEnterIcon=document.getElementById('fullscreen-enter-icon'),fullscreenExitIcon=document.getElementById('fullscreen-exit-icon'),skipBackwardButton=document.getElementById('skip-backward-button'),skipForwardButton=document.getElementById('skip-forward-button'),loadingIndicator=document.getElementById('loading-indicator'),audioSubtitleToggle=document.getElementById('audio-subtitle-toggle'),audioSubtitleMenu=document.getElementById('audio-subtitle-menu'),audioList=document.getElementById('audio-list'),subtitleList=document.getElementById('subtitle-list'),centerPlayPauseOverlay=document.getElementById('center-play-pause-overlay'),centerPlayPauseButton=document.getElementById('center-play-pause-button'),centerPlayIcon=document.getElementById('center-play-icon'),centerPauseIcon=document.getElementById('center-pause-icon'),mobileSkipBackwardButton=document.getElementById('mobile-skip-backward-button'),mobileSkipForwardButton=document.getElementById('mobile-skip-forward-button'),nextEpisodeButton=document.getElementById('next-episode-button');

/* =====================================================================
   STATE
   ===================================================================== */
let currentSeriesId=null,currentSeason=null,currentEpisode=null,totalEpisodes=null;
let isHlsJsMode=false,hlsInstance=null;
let inactivityTimer;
const INACTIVITY_TIMEOUT=3000;
let isSeeking=false,isVolumeAdjusting=false,lastKnownVolume=0.5;
let currentMouseMoveHandler=null,currentTouchMoveHandler=null;
let videoStorageKey=null,hasRestoredPosition=false,saveProgressInterval=null;
let resolvedUrl=null,_subtitleBlobUrls=[];
let _pendingSubtitleArgs=null,_subtitlesLoaded=false,_subtitlesLoading=false;
let _proxySubtitles={}; // { langCode: fullVttUrl } from hls-proxy
let _loaderWatchdog=null;
let bufferMonitorInterval=null;
// iOS: track if we are in the initial load (suppress spurious waiting events)
let _initialLoad=true;

const speedQualityMenu=document.createElement('div');
speedQualityMenu.id='speed-quality-menu';
speedQualityMenu.className='hidden';
document.body.appendChild(speedQualityMenu);

/* =====================================================================
   STORAGE KEY
   ===================================================================== */
function extractStableStreamId(url){
    if(!url)return null;
    try{const m=url.match(/\/([a-z0-9]{4,12})\/(?:master\.m3u8|cf-master)/i);if(m)return m[1];}catch(e){}
    return null;
}
function generateStorageKey(url){
    const pp=window.location.pathname,sid=extractStableStreamId(url);
    return sid?`vp:${pp}:${sid}`:`vp:${pp}`;
}

/* =====================================================================
   HELPERS
   ===================================================================== */
function revokeAllSubtitleBlobs(){while(_subtitleBlobUrls.length)URL.revokeObjectURL(_subtitleBlobUrls.pop());}
function getMediaInfoFromUrl(){
    const p=window.location.pathname;
    const tv=p.match(/\/tv\/(\d+)\/S(\d+)\/E(\d+)/i);
    if(tv)return{mediaType:'tv',contentId:tv[1],seasonNumber:Number(tv[2]),episodeNumber:Number(tv[3])};
    const mv=p.match(/\/movie\/(\d+)/i);
    if(mv)return{mediaType:'movie',contentId:mv[1]};
    return null;
}
function formatTime(s){
    if(isNaN(s)||s<0)return'0:00';
    const sec=Math.floor(s%60),min=Math.floor(s/60)%60,hrs=Math.floor(s/3600);
    const p=n=>n.toString().padStart(2,'0');
    return hrs?`${hrs}:${p(min)}:${p(sec)}`:`${min}:${p(sec)}`;
}
function displayError(msg){console.error(msg);errorMessageDiv.textContent=msg;errorMessageDiv.classList.remove('hidden');}

/* =====================================================================
   BUFFER MONITOR — only used during initial load
   ===================================================================== */
function startBufferMonitor(){
    if(bufferMonitorInterval)clearInterval(bufferMonitorInterval);
    bufferMonitorInterval=setInterval(()=>{
        if(video.readyState>=3&&!loadingIndicator.classList.contains('hidden')){
            hideLoader();
            stopBufferMonitor();
            if(video.paused&&!video.ended)video.play().catch(()=>{});
        }
    },500);
}
function stopBufferMonitor(){
    if(bufferMonitorInterval){clearInterval(bufferMonitorInterval);bufferMonitorInterval=null;}
}

/* =====================================================================
   LOADER — iOS fix: only show on real buffering, not every fragment load
   ===================================================================== */
function showLoader(){
    loadingIndicator.classList.remove('hidden');
    centerPlayPauseOverlay.classList.remove('opacity-100','pointer-events-auto');
    centerPlayPauseOverlay.classList.add('opacity-0','pointer-events-none');
    clearTimeout(_loaderWatchdog);
    startBufferMonitor();
    _loaderWatchdog=setTimeout(()=>{
        if(!loadingIndicator.classList.contains('hidden')&&video.currentTime>0&&!video.paused){
            hideLoader();stopBufferMonitor();
        }
    },8000);
}
function hideLoader(){
    clearTimeout(_loaderWatchdog);_loaderWatchdog=null;
    stopBufferMonitor();
    loadingIndicator.classList.add('hidden');
    resetInactivityTimer();
}

/* =====================================================================
   CONTROLS VISIBILITY
   ===================================================================== */
function showControls(){
    bottomOverlay.classList.remove('controls-hidden');bottomOverlay.classList.add('controls-visible');
    if(loadingIndicator.classList.contains('hidden')){
        centerPlayPauseOverlay.classList.remove('opacity-0','pointer-events-none');
        centerPlayPauseOverlay.classList.add('opacity-100','pointer-events-auto');
    }
}
function hideControls(){
    if(!isAnyMenuOpen()){
        bottomOverlay.classList.remove('controls-visible');bottomOverlay.classList.add('controls-hidden');
        centerPlayPauseOverlay.classList.remove('opacity-100','pointer-events-auto');
        centerPlayPauseOverlay.classList.add('opacity-0','pointer-events-none');
    }
}
function isAnyMenuOpen(){
    return!audioSubtitleMenu.classList.contains('hidden')||
           !document.getElementById('speed-menu').classList.contains('hidden')||
           !document.getElementById('quality-menu').classList.contains('hidden');
}
function resetInactivityTimer(){
    clearTimeout(inactivityTimer);showControls();
    if(!video.paused&&!isSeeking&&!isAnyMenuOpen()&&loadingIndicator.classList.contains('hidden'))
        inactivityTimer=setTimeout(hideControls,INACTIVITY_TIMEOUT);
}

/* =====================================================================
   PROGRESS SAVE / RESTORE
   ===================================================================== */
function saveVideoProgress(){
    if(!video.duration||isNaN(video.duration)||video.duration===Infinity)return;
    if(video.currentTime<1||video.currentTime>video.duration-5)return;
    if(!videoStorageKey)return;
    try{localStorage.setItem(videoStorageKey,JSON.stringify({currentTime:video.currentTime,duration:video.duration,timestamp:Date.now()}));}
    catch(e){}
}
function restoreVideoProgress(){
    if(hasRestoredPosition)return;
    if(!video.duration||isNaN(video.duration)||video.duration===Infinity)return;
    if(!videoStorageKey)return;
    try{
        const raw=localStorage.getItem(videoStorageKey);if(!raw)return;
        const d=JSON.parse(raw);
        if(!d.currentTime||d.currentTime<=5||d.currentTime>=(d.duration||Infinity)-10)return;
        hasRestoredPosition=true;
        const doSeek=()=>{video.currentTime=d.currentTime;};
        if(video.readyState>=2)doSeek();else video.addEventListener('canplay',doSeek,{once:true});
    }catch(e){hasRestoredPosition=true;}
}
function clearVideoProgress(){if(videoStorageKey)try{localStorage.removeItem(videoStorageKey);}catch(e){}}
function startProgressSaving(){
    saveProgressInterval=setInterval(saveVideoProgress,5000);
    video.addEventListener('pause',saveVideoProgress);
    video.addEventListener('seeking',saveVideoProgress);
    video.addEventListener('ended',clearVideoProgress);
    window.addEventListener('beforeunload',saveVideoProgress);
}
function stopProgressSaving(){
    clearInterval(saveProgressInterval);saveProgressInterval=null;
    video.removeEventListener('pause',saveVideoProgress);
    video.removeEventListener('seeking',saveVideoProgress);
    video.removeEventListener('ended',clearVideoProgress);
    window.removeEventListener('beforeunload',saveVideoProgress);
}
function postTimeUpdateToParent(){
    if(window.parent!==window)window.parent.postMessage({event:'videoTimeUpdate',currentTime:video.currentTime,duration:video.duration,paused:video.paused,...getMediaInfoFromUrl()},'*');
}

/* =====================================================================
   PROGRESS BAR UI
   ===================================================================== */
function updateBufferProgress(){
    if(!video.duration||video.duration===Infinity)return;
    const b=video.buffered;if(!b.length){bufferIndicator.style.width='0%';return;}
    let f=0;for(let i=0;i<b.length;i++)f=Math.max(f,b.end(i));
    bufferIndicator.style.width=`${Math.min(100,(f/video.duration)*100)}%`;
}
function updateProgress(){
    if(!video.duration||isSeeking)return;
    const pct=(video.currentTime/video.duration)*100;
    progressIndicator.style.width=`${pct}%`;
    seekThumb.style.left=`calc(${pct}% - 3px)`;
    remainingTimeDisplay.textContent=formatTime(video.duration-video.currentTime);
}
function updateBottomPlayPauseIcon(p){if(p){playIcon.classList.remove('hidden');pauseIcon.classList.add('hidden');}else{playIcon.classList.add('hidden');pauseIcon.classList.remove('hidden');}}
function updateCenterPlayPauseIcon(p){if(p){centerPlayIcon.classList.remove('hidden');centerPauseIcon.classList.add('hidden');}else{centerPlayIcon.classList.add('hidden');centerPauseIcon.classList.remove('hidden');}}
function updateMuteIcon(){
    const muted=video.muted||video.volume===0,vol=video.muted?0:video.volume;
    volumeOffIcon.classList.toggle('hidden',!muted);
    volumeLowIcon.classList.toggle('hidden',muted||vol>0.33);
    volumeMediumIcon.classList.toggle('hidden',muted||vol<=0.33||vol>0.66);
    volumeHighIcon.classList.toggle('hidden',muted||vol<=0.66);
}
function updateVolumeSlider(){
    const vol=video.muted?0:video.volume;
    volumeLevel.style.height=`${vol*100}%`;
    volumeThumbControl.style.bottom=`calc(${vol*100}% - 8px)`;
    updateMuteIcon();
}
function toggleMute(){
    if(video.muted){video.volume=lastKnownVolume>0?lastKnownVolume:0.5;video.muted=false;}
    else{lastKnownVolume=video.volume;video.muted=true;}
    updateVolumeSlider();resetInactivityTimer();
}
function toggleVideoPlayPause(){
    if(!isAnyMenuOpen()&&loadingIndicator.classList.contains('hidden')){
        if(video.paused||video.ended)video.play().catch(e=>displayError('Play failed: '+e.message));
        else video.pause();
    }
}

/* =====================================================================
   SEEKBAR
   ===================================================================== */
let _lastSeekClientX=0;
function calculateNewTime(clientX){
    const rect=seekBar.getBoundingClientRect();
    return video.duration*Math.max(0,Math.min(clientX-rect.left,rect.width))/rect.width;
}
function handleSeek(clientX){
    if(!video.duration||video.duration===Infinity)return;
    _lastSeekClientX=clientX;
    const pct=(calculateNewTime(clientX)/video.duration)*100;
    progressIndicator.style.width=`${pct}%`;
    seekThumb.style.left=`calc(${pct}% - 3px)`;
    remainingTimeDisplay.textContent=`-${formatTime(video.duration-calculateNewTime(clientX))}`;
}
function startSeeking(e){
    if(!video.duration||video.duration===Infinity)return;
    e.preventDefault();
    isSeeking=true;showControls();seekThumb.classList.add('scale-100');
    _lastSeekClientX=e.touches?e.touches[0].clientX:e.clientX;
    currentMouseMoveHandler=ev=>handleSeek(ev.clientX);
    currentTouchMoveHandler=ev=>{ev.preventDefault();handleSeek(ev.touches[0].clientX);};
    window.addEventListener('mousemove',currentMouseMoveHandler);
    window.addEventListener('mouseup',endSeeking);
    window.addEventListener('touchmove',currentTouchMoveHandler,{passive:false});
    window.addEventListener('touchend',endSeeking);
    handleSeek(_lastSeekClientX);
}
function endSeeking(){
    if(!isSeeking)return;
    const t=calculateNewTime(_lastSeekClientX);
    isSeeking=false;seekThumb.classList.remove('scale-100');
    if(currentMouseMoveHandler){window.removeEventListener('mousemove',currentMouseMoveHandler);currentMouseMoveHandler=null;}
    if(currentTouchMoveHandler){window.removeEventListener('touchmove',currentTouchMoveHandler);currentTouchMoveHandler=null;}
    window.removeEventListener('mouseup',endSeeking);
    window.removeEventListener('touchend',endSeeking);
    video.currentTime=t;
    resetInactivityTimer();
}

/* =====================================================================
   VOLUME SLIDER
   ===================================================================== */
function calculateNewVolume(clientY){const rect=volumeSliderTrack.getBoundingClientRect();return Math.max(0,Math.min(rect.bottom-clientY,rect.height))/rect.height;}
function handleVolumeAdjust(e){
    e.preventDefault();
    const vol=calculateNewVolume(e.touches?e.touches[0].clientY:e.clientY);
    video.volume=vol;
    if(vol>0){video.muted=false;lastKnownVolume=vol;}else video.muted=true;
    updateVolumeSlider();
}
function startVolumeAdjusting(e){
    isVolumeAdjusting=true;e.preventDefault();
    window.addEventListener('mousemove',handleVolumeAdjust);window.addEventListener('mouseup',endVolumeAdjusting);
    window.addEventListener('touchmove',handleVolumeAdjust);window.addEventListener('touchend',endVolumeAdjusting);
    handleVolumeAdjust(e);
}
function endVolumeAdjusting(){
    if(!isVolumeAdjusting)return;isVolumeAdjusting=false;
    window.removeEventListener('mousemove',handleVolumeAdjust);window.removeEventListener('mouseup',endVolumeAdjusting);
    window.removeEventListener('touchmove',handleVolumeAdjust);window.removeEventListener('touchend',endVolumeAdjusting);
    resetInactivityTimer();
}
volumeSliderTrack.addEventListener('mousedown',startVolumeAdjusting);
volumeSliderTrack.addEventListener('touchstart',startVolumeAdjusting,{passive:true});

/* =====================================================================
   FULLSCREEN
   ===================================================================== */
function isMobileDevice(){return/Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent)||(navigator.maxTouchPoints>1&&window.innerWidth<=1024);}
function lockLandscape(){try{if(screen.orientation?.lock)screen.orientation.lock('landscape').catch(()=>{});}catch(e){}}
function unlockOrientation(){try{if(screen.orientation?.unlock)screen.orientation.unlock();}catch(e){}}
function isInFullscreen(){return!!(document.fullscreenElement||document.webkitFullscreenElement||video.webkitDisplayingFullscreen);}
function toggleFullscreen(){
    if(video.webkitEnterFullscreen&&!document.fullscreenElement&&!document.webkitFullscreenElement){video.webkitEnterFullscreen();return;}
    if(document.fullscreenElement||document.webkitFullscreenElement){
        (document.exitFullscreen||document.webkitExitFullscreen).call(document);
        if(isMobileDevice())unlockOrientation();
    }else{
        const req=videoContainer.requestFullscreen||videoContainer.webkitRequestFullscreen;
        if(req)req.call(videoContainer,{navigationUI:'hide'}).then(()=>{if(isMobileDevice())lockLandscape();}).catch(err=>displayError('Fullscreen: '+err.message));
    }
}
function updateFullscreenIcon(){
    const fs=isInFullscreen();
    fullscreenEnterIcon.classList.toggle('hidden',fs);fullscreenExitIcon.classList.toggle('hidden',!fs);
    if(!fs&&isMobileDevice())unlockOrientation();
}

/* =====================================================================
   LANGUAGE MAP
   ===================================================================== */
const LM={'eng':'English','en':'English','und':'Undefined','hin':'Hindi','hi':'Hindi','tel':'Telugu','te':'Telugu','tam':'Tamil','ta':'Tamil','kan':'Kannada','kn':'Kannada','spa':'Spanish','es':'Spanish','fre':'French','fr':'French','ger':'German','de':'German','ita':'Italian','it':'Italian','jpn':'Japanese','ja':'Japanese','por':'Portuguese','pt':'Portuguese','rus':'Russian','ru':'Russian','zho':'Chinese','zh':'Chinese','ara':'Arabic','ar':'Arabic','kor':'Korean','ko':'Korean','tl':'Filipino','mal':'Malayalam','ml':'Malayalam','ben':'Bengali','bn':'Bengali','mar':'Marathi','mr':'Marathi'};
function getLang(code){if(!code)return'';const lc=code.toLowerCase();return LM[lc]||code.charAt(0).toUpperCase()+code.slice(1);}

/* =====================================================================
   AUDIO / SUBTITLE MENU
   ===================================================================== */
function toggleAudioSubtitleMenu(){
    const hidden=audioSubtitleMenu.classList.contains('hidden');
    if(hidden){
        // Render audio immediately, load subtitles on first open
        if(!_subtitlesLoaded&&!_subtitlesLoading&&_pendingSubtitleArgs){
            _subtitlesLoading=true;
            const{type,tmdbId,season,episode}=_pendingSubtitleArgs;
            subtitleList.innerHTML='<li class="text-gray-400" style="padding:8px 10px">Loading subtitles…</li>';
            // Inject proxy subtitles immediately (already fetched), then load stremio
            injectProxySubtitles().then(()=>{
                return loadStremioSubtitles(type,tmdbId,season,episode);
            }).then(()=>{
                _subtitlesLoaded=true;_subtitlesLoading=false;renderTracksMenu();
            }).catch(()=>{
                _subtitlesLoaded=true;_subtitlesLoading=false;renderTracksMenu();
            });
            renderTracksMenuAudioOnly();
        }else if(_subtitlesLoading){
            renderTracksMenuAudioOnly();
        }else{
            renderTracksMenu();
        }
        audioSubtitleMenu.classList.remove('hidden');clearTimeout(inactivityTimer);showControls();
    }else{
        audioSubtitleMenu.classList.add('hidden');resetInactivityTimer();
    }
}

function _checkmark(visible){
    const s=document.createElement('span');
    s.style.cssText=`visibility:${visible?'visible':'hidden'};flex-shrink:0;display:inline-flex;align-items:center`;
    s.innerHTML='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14"><path fill-rule="evenodd" clip-rule="evenodd" d="M21.2928 4.29285L22.7071 5.70706L8.70706 19.7071C8.51952 19.8946 8.26517 20 7.99995 20C7.73474 20 7.48038 19.8946 7.29285 19.7071L0.292847 12.7071L1.70706 11.2928L7.99995 17.5857L21.2928 4.29285Z" fill="white"/></svg>';
    return s;
}
function _trackDisplayName(track,isHls){
    const raw=isHls?track.lang:track.language,primary=isHls?track.name:track.label;
    let name=raw?getLang(raw):'';
    if(primary){const l=primary.toLowerCase();if(LM[l])name=LM[l];else if(!name||name.toLowerCase()==='undefined')name=primary;}
    return name||`Track ${track.id??track.groupId??''}`;
}

function renderTracksMenuAudioOnly(){
    audioList.innerHTML='';
    const tracks=isHlsJsMode?hlsInstance.audioTracks:(video.audioTracks?Array.from(video.audioTracks):[]);
    const cur=isHlsJsMode?hlsInstance.audioTrack:(video.audioTracks?Array.from(video.audioTracks).findIndex(t=>t.enabled):-1);
    if(!tracks.length){audioList.innerHTML='<li class="text-gray-400">No alternate audio</li>';return;}
    tracks.forEach((t,i)=>{
        const sel=isHlsJsMode?(i===cur):t.enabled;
        const li=document.createElement('li');li.className=`track-selector cursor-pointer flex items-center gap-2 ${sel?'font-bold text-white':'text-gray-400'}`;
        li.appendChild(_checkmark(sel));const lb=document.createElement('span');lb.textContent=_trackDisplayName(t,isHlsJsMode);li.appendChild(lb);
        li.addEventListener('click',()=>handleTrackSelection('audio',i));audioList.appendChild(li);
    });
}

function renderTracksMenu(){
    audioList.innerHTML='';subtitleList.innerHTML='';
    // Audio
    const aTracks=isHlsJsMode?hlsInstance.audioTracks:(video.audioTracks?Array.from(video.audioTracks):[]);
    const aCur=isHlsJsMode?hlsInstance.audioTrack:(video.audioTracks?Array.from(video.audioTracks).findIndex(t=>t.enabled):-1);
    if(!aTracks.length){audioList.innerHTML='<li class="text-gray-400">No alternate audio</li>';}
    else{aTracks.forEach((t,i)=>{const sel=isHlsJsMode?(i===aCur):t.enabled;const li=document.createElement('li');li.className=`track-selector cursor-pointer flex items-center gap-2 ${sel?'font-bold text-white':'text-gray-400'}`;li.appendChild(_checkmark(sel));const lb=document.createElement('span');lb.textContent=_trackDisplayName(t,isHlsJsMode);li.appendChild(lb);li.addEventListener('click',()=>handleTrackSelection('audio',i));audioList.appendChild(li);});}
    // Subtitles
    const subs=video.textTracks?Array.from(video.textTracks).filter(t=>t.kind==='subtitles'||t.kind==='captions'):[];
    const sCur=subs.findIndex(t=>t.mode==='showing');
    // Off
    const offLi=document.createElement('li');offLi.className=`track-selector cursor-pointer flex items-center gap-2 ${sCur===-1?'font-bold text-white':'text-gray-400'}`;offLi.appendChild(_checkmark(sCur===-1));const offLb=document.createElement('span');offLb.textContent='Off';offLi.appendChild(offLb);offLi.addEventListener('click',()=>handleTrackSelection('subtitle',-1));subtitleList.appendChild(offLi);
    if(!subs.length){subtitleList.innerHTML+='<li class="text-gray-400">No subtitles found</li>';}
    else{
        subs.forEach((t,idx)=>{
            const sel=t.mode==='showing';
            const isProxy=t.label&&t.label.includes('[CC]');
            const li=document.createElement('li');
            li.className=`track-selector cursor-pointer flex items-center gap-2 ${sel?'font-bold text-white':'text-gray-400'}`;
            li.appendChild(_checkmark(sel));
            const lb=document.createElement('span');
            // Proxy CC tracks already have [CC] in label; stremio tracks get plain name
            lb.textContent=t.label||getLang(t.language);
            // Highlight proxy [CC] tracks
            if(isProxy){lb.style.color=sel?'#fff':'#e2b84b';}
            li.appendChild(lb);
            li.addEventListener('click',()=>handleTrackSelection('subtitle',idx));
            subtitleList.appendChild(li);
        });
    }
}

function handleTrackSelection(type,idx){
    if(type==='audio'){
        if(isHlsJsMode&&hlsInstance)hlsInstance.audioTrack=idx;
        else if(video.audioTracks)for(let i=0;i<video.audioTracks.length;i++)video.audioTracks[i].enabled=(i===idx);
        audioSubtitleMenu.classList.add('hidden');renderTracksMenu();resetInactivityTimer();return;
    }
    const subs=video.textTracks?Array.from(video.textTracks).filter(t=>t.kind==='subtitles'||t.kind==='captions'):[];
    if(idx===-1){if(isHlsJsMode&&hlsInstance)hlsInstance.subtitleTrack=-1;subs.forEach(t=>t.mode='disabled');}
    else{if(isHlsJsMode&&hlsInstance)hlsInstance.subtitleTrack=-1;subs.forEach((t,i)=>t.mode=(i===idx)?'showing':'disabled');}
    audioSubtitleMenu.classList.add('hidden');renderTracksMenu();resetInactivityTimer();
}

/* =====================================================================
   SPEED MENU
   ===================================================================== */
const SPEED_OPTIONS=[{label:'0.25x',value:.25},{label:'0.5x',value:.5},{label:'0.75x',value:.75},{label:'Normal',value:1},{label:'1.25x',value:1.25},{label:'1.5x',value:1.5},{label:'1.75x',value:1.75},{label:'2x',value:2}];
const speedButton=document.getElementById('speed-button'),speedMenu=document.getElementById('speed-menu'),speedList=document.getElementById('speed-list');
function renderSpeedMenu(){
    speedList.innerHTML='';
    SPEED_OPTIONS.forEach(o=>{const li=document.createElement('li');li.className=`cursor-pointer hover:opacity-80 p-1 rounded transition text-sm ${video.playbackRate===o.value?'font-bold text-white':'text-gray-400'}`;li.textContent=o.label;li.addEventListener('click',()=>{video.playbackRate=o.value;renderSpeedMenu();speedMenu.classList.add('hidden');resetInactivityTimer();});speedList.appendChild(li);});
}
function toggleSpeedMenu(){const h=speedMenu.classList.contains('hidden');if(h){renderSpeedMenu();speedMenu.classList.remove('hidden');clearTimeout(inactivityTimer);showControls();}else{speedMenu.classList.add('hidden');resetInactivityTimer();}}
speedButton.addEventListener('click',e=>{e.stopPropagation();toggleSpeedMenu();});

/* =====================================================================
   QUALITY MENU
   ===================================================================== */
const qualityButton=document.getElementById('quality-button'),qualityMenu=document.getElementById('quality-menu'),qualityList=document.getElementById('quality-list');
function renderQualityMenu(){
    qualityList.innerHTML='';
    if(!hlsInstance||!isHlsJsMode){const li=document.createElement('li');li.textContent='Auto';li.style.color='#9ca3af';li.style.justifyContent='center';qualityList.appendChild(li);return;}
    const levels=hlsInstance.levels,current=hlsInstance.currentLevel;
    const add=(text,value,isAuto)=>{const li=document.createElement('li');li.style.cssText='display:flex;justify-content:space-between;align-items:center';const sp=document.createElement('span');sp.textContent=text;li.appendChild(sp);if(value===current&&!isAuto){const b=document.createElement('span');b.className='quality-badge';b.textContent='Active';li.appendChild(b);li.style.color='#fff';li.style.fontWeight='700';}else li.style.color='#9ca3af';li.addEventListener('click',()=>{if(isAuto)hlsInstance.currentLevel=-1;else hlsInstance.currentLevel=value;renderQualityMenu();qualityMenu.classList.add('hidden');resetInactivityTimer();});qualityList.appendChild(li);};
    add('Auto',-1,true);levels.forEach((l,i)=>add(`${l.height?l.height+'p':'Level '+i}${l.bitrate?' ('+Math.round(l.bitrate/1000)+'kbps)':''}`,i,false));
}
function toggleQualityMenu(){const h=qualityMenu.classList.contains('hidden');if(h){renderQualityMenu();qualityMenu.classList.remove('hidden');clearTimeout(inactivityTimer);showControls();}else{qualityMenu.classList.add('hidden');resetInactivityTimer();}}
qualityButton.addEventListener('click',e=>{e.stopPropagation();toggleQualityMenu();});

/* =====================================================================
   NEXT EPISODE
   ===================================================================== */
function extractEpisodeInfoFromUrl(){const m=window.location.pathname.match(/\/tv\/(\d+)\/S(\d+)\/E(\d+)/i);return m?{seriesId:m[1],season:parseInt(m[2]),episode:parseInt(m[3])}:null;}
async function updateNextEpisodeButton(){
    const info=extractEpisodeInfoFromUrl();
    if(!info){nextEpisodeButton.style.display='none';return;}
    currentSeriesId=info.seriesId;currentSeason=info.season;currentEpisode=info.episode;
    if(totalEpisodes===null){
        try{
            const r=await fetch(`https://search-proxy.bingeoutofficial.workers.dev/tv/${currentSeriesId}/season/${currentSeason}`);
            if(r.ok){const d=await r.json();totalEpisodes=(d.episodes||[]).length||null;}
        }catch(e){totalEpisodes=null;}
    }
    if(totalEpisodes!==null&&currentEpisode<totalEpisodes){
        nextEpisodeButton.style.display='flex';
        nextEpisodeButton.onclick=()=>{window.location.href=`/tv/${currentSeriesId}/S${currentSeason}/E${currentEpisode+1}`;};
    }else{nextEpisodeButton.style.display='none';}
}

/* =====================================================================
   HLS PLAYER INIT
   ===================================================================== */
function isDirectVideoUrl(url){
    try{const path=new URL(url).pathname.toLowerCase();return/\.(mp4|webm|ogg|ogv|mov|mkv|avi|flv|m4v)(\?|$)/.test(path);}
    catch(e){return/\.(mp4|webm|ogg|ogv|mov|mkv|avi|flv|m4v)(\?|$)/.test(url.toLowerCase());}
}

function cleanupSubtitles(){
    Array.from(video.querySelectorAll('track[data-stremio],track[data-proxy]')).forEach(t=>t.remove());
}

function initHlsPlayer(url){
    saveVideoProgress();
    if(saveProgressInterval){clearInterval(saveProgressInterval);saveProgressInterval=null;}
    stopProgressSaving();
    hasRestoredPosition=false;
    _initialLoad=true;
    if(hlsInstance){hlsInstance.destroy();hlsInstance=null;}
    cleanupSubtitles();
    errorMessageDiv.classList.add('hidden');
    resolvedUrl=url;
    videoStorageKey=generateStorageKey(url);
    _subtitlesLoaded=false;
    _subtitlesLoading=false;

    if(isDirectVideoUrl(url)){
        isHlsJsMode=false;
        showLoader();
        video.src=url;
        video.addEventListener('loadedmetadata',()=>{
            renderTracksMenu();hideLoader();
            restoreVideoProgress();startProgressSaving();
            video.play().catch(()=>{});
            updateNextEpisodeButton();
            _initialLoad=false;
        },{once:true});
        video.addEventListener('error',()=>{
            if(video.currentTime>0||video.readyState>=2)return;
            displayError('Failed to load video: '+(video.error?video.error.message:'unknown error'));
            hideLoader();
        },{once:true});
        return;
    }

    if(Hls.isSupported()){
        isHlsJsMode=true;
        showLoader();
        const h=new Hls({
            autoStartLoad:true,
            startLevel:2,
            maxBufferLength:30,
            maxMaxBufferLength:60,
            maxBufferSize:80*1024*1024,
            maxBufferHole:0.1,
            enableWorker:true,
            renderTextTracksNatively:true,
            subtitleDisplay:true,
        });
        hlsInstance=h;
        h.on(Hls.Events.MEDIA_ATTACHED,()=>h.loadSource(url));
        h.on(Hls.Events.MANIFEST_PARSED,()=>{renderTracksMenu();renderQualityMenu();updateNextEpisodeButton();});
        h.on(Hls.Events.AUDIO_TRACK_SWITCHED,renderTracksMenu);
        h.on(Hls.Events.SUBTITLE_TRACK_SWITCHED,renderTracksMenu);
        h.on(Hls.Events.LEVEL_SWITCHED,renderQualityMenu);
        h.on(Hls.Events.ERROR,(ev,data)=>{
            if(data.fatal){displayError('Fatal HLS error');h.destroy();hideLoader();}
        });
        h.attachMedia(video);
        video.addEventListener('loadedmetadata',()=>restoreVideoProgress(),{once:true});
        video.addEventListener('canplay',()=>{hideLoader();startProgressSaving();video.play().catch(()=>{});_initialLoad=false;},{once:true});
    }
    else if(video.canPlayType('application/vnd.apple.mpegurl')){
        // iOS Safari native HLS
        isHlsJsMode=false;
        showLoader();
        video.src=url;
        video.addEventListener('loadedmetadata',()=>{
            renderTracksMenu();hideLoader();
            restoreVideoProgress();startProgressSaving();
            video.play().catch(()=>{});
            updateNextEpisodeButton();
            _initialLoad=false;
        },{once:true});
        video.addEventListener('error',()=>{
            if(video.currentTime>0&&!video.paused)return;
            displayError('Failed to load stream: '+(video.error?video.error.message:'unknown error'));
            hideLoader();
        },{once:true});
    }
    else{
        displayError('Browser does not support HLS');hideLoader();
    }
}

/* =====================================================================
   PROXY SUBTITLES — injected immediately from hls-proxy response
   Format: { "en": "/path/en.vtt#en", "hi": "/path/hi.vtt#hi" }
   Base: https://multimovies.rpmhub.site
   ===================================================================== */
const PROXY_SUBTITLE_BASE='https://multimovies.rpmhub.site';

async function injectProxySubtitles(){
    // Remove old proxy tracks
    Array.from(video.querySelectorAll('track[data-proxy]')).forEach(t=>t.remove());
    if(!_proxySubtitles||!Object.keys(_proxySubtitles).length)return;

    const inject=()=>{
        Object.entries(_proxySubtitles).forEach(([lang,path])=>{
            // path looks like "/JFBSnoH84A0s3egE2WqAQA/q3o/.../en.vtt#en"
            // strip fragment, prepend base
            const cleanPath=path.split('#')[0];
            const fullUrl=`${PROXY_SUBTITLE_BASE}${cleanPath}`;
            const track=document.createElement('track');
            track.kind='subtitles';
            track.label=`${getLang(lang)} [CC]`;
            track.srclang=lang;
            track.src=fullUrl;
            track.default=false;
            track.setAttribute('data-proxy','1');
            video.appendChild(track);
            console.log(`[ProxySub] Added ${lang}: ${fullUrl}`);
        });
        renderTracksMenu();
    };

    if(video.readyState>=1)inject();
    else video.addEventListener('loadedmetadata',inject,{once:true});
}

/* =====================================================================
   STREMIO / OPENSUBTITLES — only fetched when menu is opened
   Only the main JSON endpoint is requested upfront; SRT files fetched per track
   ===================================================================== */
const TMDB_PROXY='https://search-proxy.bingeoutofficial.workers.dev';

async function loadStremioSubtitles(type,tmdbId,season,episode){
    Array.from(video.querySelectorAll('track[data-stremio]')).forEach(t=>t.remove());
    let imdbId=null;
    try{
        const r=await fetch(`${TMDB_PROXY}/${type}/${tmdbId}/external_ids`);
        if(r.ok){const d=await r.json();imdbId=d.imdb_id;}
    }catch(e){console.warn('[Stremio] IMDb fetch failed:',e.message);return;}
    if(!imdbId){console.warn('[Stremio] No IMDb ID');return;}

    // Only request the main subtitle list URL — individual SRTs fetched below
    const listUrl=(type==='tv'&&season&&episode)
        ?`https://opensubtitles-v3.strem.io/subtitles/series/${imdbId}:${season}:${episode}.json`
        :`https://opensubtitles-v3.strem.io/subtitles/movie/${imdbId}.json`;

    console.log('[Stremio] Fetching list:',listUrl);
    try{
        const r=await fetch(listUrl);
        if(!r.ok)return;
        const data=await r.json();
        let subs=data.subtitles||[];
        if(!subs.length)return;

        // 5 per lang, 15 total
        const LIMIT_PER_LANG=5,LIMIT_TOTAL=15;
        const langCount=new Map(),filtered=[];
        for(const s of subs){
            if(filtered.length>=LIMIT_TOTAL)break;
            const lang=(s.lang||'und').toLowerCase();
            const cnt=langCount.get(lang)||0;
            if(cnt<LIMIT_PER_LANG){langCount.set(lang,cnt+1);filtered.push(s);}
        }

        const inject=async()=>{
            for(const sub of filtered){
                try{
                    const srtRes=await fetch(sub.url);
                    if(!srtRes.ok)continue;
                    const srtText=await srtRes.text();
                    const vttText=srtToVtt(srtText);
                    const base64=btoa(unescape(encodeURIComponent(vttText)));
                    const dataUrl=`data:text/vtt;charset=utf-8;base64,${base64}`;
                    const track=document.createElement('track');
                    track.kind='subtitles';
                    track.label=sub.langName||getLang(sub.lang);
                    track.srclang=sub.lang;
                    track.src=dataUrl;
                    track.default=false;
                    track.setAttribute('data-stremio','1');
                    video.appendChild(track);
                    console.log(`[Stremio] Added: ${track.label}`);
                }catch(err){console.warn(`[Stremio] Failed ${sub.lang}:`,err.message);}
            }
            setTimeout(renderTracksMenu,300);
        };

        if(video.readyState>=1)await inject();
        else video.addEventListener('loadedmetadata',async()=>await inject(),{once:true});
    }catch(e){console.warn('[Stremio] Error:',e.message);}
}

function srtToVtt(srt){
    let vtt='WEBVTT\n\n';
    const body=srt.replace(/\r\n/g,'\n').replace(/\r/g,'\n').replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g,'$1.$2').trim();
    vtt+=body.replace(/(\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3})/g,'$1 line:85% position:50% align:center');
    return vtt;
}


/* =====================================================================
   CONFIG
   ===================================================================== */
const PROXY_API = 'https://script.google.com/macros/s/AKfycbw8pW6LI6nNDxqn1wXaPOzHN5QBaeqB12qv-J5NaNcu7IWqbsX9KJkruY_8y8wW12hv/exec';
const CATALOG_API = 'https://script.google.com/macros/s/AKfycbw8pW6LI6nNDxqn1wXaPOzHN5QBaeqB12qv-J5NaNcu7IWqbsX9KJkruY_8y8wW12hv/exec';
const CATALOG_KEY = 'e11a7debaaa4f5d25b671706ffe4d2acb56efbd4';

/* =====================================================================
   STEP 1 — Get IMDb ID from TMDB (movies only)
   ===================================================================== */
async function getImdbId(tmdbId) {
    try {
        const r = await fetch(`${TMDB_PROXY}/movie/${tmdbId}/external_ids`);
        if (!r.ok) return null;
        const d = await r.json();
        return d.imdb_id || null;
    } catch(e) {
        console.warn('[IMDb] fetch failed:', e.message);
        return null;
    }
}

/* =====================================================================
   STEP 2 — Fetch fileslugs from catalog API
   ===================================================================== */
async function fetchCatalogFiles(type, imdbId, tmdbId, season, episode) {
    try {
        const params = type === 'movie'
            ? { type: 'movie', imdbid: imdbId, key: CATALOG_KEY }
            : { type: 'tv', tmdbid: tmdbId, season, epname: episode, key: CATALOG_KEY };

        const url = CATALOG_API + '?' + new URLSearchParams(params);
        const r = await fetch(url, { cache: 'no-store' });
        if (!r.ok) return null;
        const data = await r.json();
        if (!data.success || !data.data?.length) return null;
        console.log('[Catalog] Files:', data.data);
        return data.data; // [{ filename, fileslug, fsize }, ...]
    } catch(e) {
        console.warn('[Catalog] Error:', e.message);
        return null;
    }
}

/* =====================================================================
   STEP 3 — Resolve fileslug via Django API → m3u8
   ===================================================================== */
/* =====================================================================
   STEP 3 — Resolve fileslug via embedhelper proxy
   ==================================================================== */
from app.api.sites.gdmirrorbot import _fetch_embed_data

def process_fileslug(fileslug):

    Fetches embed data for a given fileslug and returns it.

    # 1. Fetch the data
    data = _fetch_embed_data(fileslug)

    # 2. Handle potential failure
    if data is None:
        # Return an empty dict or raise an error, depending on your needs
        return {"error": "Failed to fetch embed data"}

    # 3. Optional: debug print
    print(data)

    # 4. Extract specific fields if needed (they are used later)
    sources = data.get("sources", {})
    mresult = data.get("mresult")

    # 5. Return the full data
    return data
           
/*========== 2. Build iframe URLs from embed data (JS version of your Python function) ==========*/
function buildIframeUrls(embedData) {
  const { mresult, sources } = embedData;

  if (!mresult) {
    throw new Error('mresult missing in embed data');
  }

  // Decode base64 mresult and parse JSON
  const decoded = atob(mresult); // atob works in browser; for Node use Buffer.from(mresult, 'base64').toString()
  let streamIds;
  try {
    streamIds = JSON.parse(decoded);
  } catch {
    throw new Error('Invalid JSON in decoded mresult');
  }

  if (!streamIds || typeof streamIds !== 'object') {
    throw new Error('Decoded mresult is empty or invalid');
  }

  // ---------- Define provider mappings ----------
  // Option A: Hardcode base URLs and friendly names (if static)
  const siteUrls = {
    upnshr: 'https://upnshr.example.com/embed/',
    rpmshre: 'https://rpmshre.example.com/embed/',
    strmp2: 'https://strmp2.example.com/embed/',
    smwh: 'https://smwh.example.com/embed/',
    flls: 'https://flls.example.com/embed/'
  };

  const friendlyNames = {
    upnshr: 'UPNSHR',
    rpmshre: 'RPMSHRE',
    strmp2: 'STRMP2',
    smwh: 'SMWH',
    flls: 'FLLS'
  };

  // Option B: Fetch mappings from your Python endpoints (uncomment if needed)
  /*
  const [streamp2pMap, streamwishMap] = await Promise.all([
    fetch('/app/api/sites/streamp2p.py').then(r => r.json()),
    fetch('/app/api/sites/streamwish.py').then(r => r.json())
  ]);
  // merge mappings...
  */

  const iframeUrls = {};

  for (const [providerKey, streamId] of Object.entries(streamIds)) {
    if (!streamId) continue;

    const baseUrl = siteUrls[providerKey];
    if (!baseUrl) continue;

    const providerName = friendlyNames[providerKey] || providerKey;
    iframeUrls[providerName] = `${baseUrl}${streamId}`;
  }

  return iframeUrls;
}

// ========== 3. Usage example ==========
(async () => {
  const fileslug = 'your_fileslug_here'; // e.g., "abc123"
  const embedData = await resolveFileslug(fileslug);

  if (!embedData) {
    console.error('Failed to fetch embed data');
    return;
  }

  try {
    const iframeUrls = buildIframeUrls(embedData);
    console.log('Generated iframe URLs:', iframeUrls);

    // Extract specific ones if needed:
    const { UPNSHR, RPMSHRE, STRMP2, SMWH, FLLS } = iframeUrls;
    console.log('UPNSHR:', UPNSHR);
    console.log('RPMSHRE:', RPMSHRE);
    console.log('STRMP2:', STRMP2);
    console.log('SMWH:', SMWH);
    console.log('FLLS:', FLLS);
  } catch (err) {
    console.error('Error building iframe URLs:', err.message);
  }
})();

/* =====================================================================
   STEP 4 — Full catalog source
   ===================================================================== */
async function source_catalog(type, tmdbId, season, episode) {
    let imdbId = null;

    if (type === 'movie') {
        imdbId = await getImdbId(tmdbId);
        if (!imdbId) {
            console.warn('[Catalog] Could not get IMDb ID');
            return null;
        }
    }

    const files = await fetchCatalogFiles(type, imdbId, tmdbId, season, episode);
    if (!files) return null;

    // Try each fileslug until one resolves
    for (const file of files) {
        if (!file.fileslug) continue;
        console.log('[Catalog] Trying fileslug:', file.fileslug, file.filename);
        const url = await resolveFileslug(file.fileslug);
        if (url) return url;
    }

    return null;
}

/* =====================================================================
   STREAM FETCHER — catalog first, GitHub fallback
   ===================================================================== */
async function fetchStream(type, id, season, episode) {
    // Priority 1: Catalog → GDMirror → StreamWish/StreamP2P
    console.log('[fetchStream] Trying catalog...');
    let url = await source_catalog(type, id, season, episode);
    if (url) return url;

    // Priority 2: GitHub fallback
    console.warn('[fetchStream] Catalog failed, trying GitHub...');
    _proxySubtitles = {};
    try {
        const ghUrl = type === 'movie'
            ? `https://raw.githubusercontent.com/Watchout2025/api/refs/heads/main/hls/movie/${id}`
            : `https://raw.githubusercontent.com/Watchout2025/api/refs/heads/main/hls/tv/${id}/S${season}.json`;
        const ghRes = await fetch(ghUrl, { cache: 'no-store' });
        if (ghRes.ok) {
            if (type === 'movie') return (await ghRes.text()).trim();
            else { const d = await ghRes.json(); return d[Number(episode)] || null; }
        }
    } catch(e) { console.warn('[GitHub fallback] failed:', e.message); }

    return null;
}

/* =====================================================================
   TITLE FETCH
   ===================================================================== */
async function fetchAndSetTitle(type,id,season,episode){
    try{
        let title='',mobileTitle='';
        if(type==='movie'){
            const r=await fetch(`${TMDB_PROXY}/movie/${id}`);
            if(r.ok){const d=await r.json();title=d.title||'';mobileTitle=title;}
        }else{
            const[sr,er]=await Promise.all([fetch(`${TMDB_PROXY}/tv/${id}`),fetch(`${TMDB_PROXY}/tv/${id}/season/${season}/episode/${episode}`)]);
            const series=sr.ok?await sr.json():{},ep=er.ok?await er.json():{};
            title=[series.name,`S${season}:E${episode}`,ep.name].filter(Boolean).join(' ');
            mobileTitle=`S${season}:E${episode} "${ep.name||series.name}"`;
        }
        document.getElementById('title-main-text').textContent=title;
        document.getElementById('mobile-title-main').textContent=mobileTitle;
        document.title=title||document.title;
    }catch(e){}
}

/* =====================================================================
   ROUTER
   ===================================================================== */
async function resolveAndPlay(){
    const path=window.location.pathname;
    const urlParams=new URLSearchParams(window.location.search);
    const urlParam=urlParams.get('url');

    // ?url= direct stream (e.g. .txt served as HLS manifest)
    if(urlParam){
        showLoader();
        revokeAllSubtitleBlobs();
        _proxySubtitles={};
        initHlsPlayer(urlParam);
        return;
    }

    const mv=path.match(/\/movie\/(\d+)/i);
    if(mv){
        const id=mv[1];showLoader();
        const streamUrl=await fetchStream('movie',id,null,null);
        if(streamUrl){
            revokeAllSubtitleBlobs();
            initHlsPlayer(streamUrl);
            fetchAndSetTitle('movie',id);
            _pendingSubtitleArgs={type:'movie',tmdbId:id,season:null,episode:null};
        }else{hideLoader();displayError('Could not load movie. Please try again later.');}
        return;
    }

    const tv=path.match(/\/tv\/(\d+)\/S(\d+)\/E(\d+)/i);
    if(tv){
        const[,id,season,episode]=tv;showLoader();
        const streamUrl=await fetchStream('tv',id,season,episode);
        if(streamUrl){
            revokeAllSubtitleBlobs();
            initHlsPlayer(streamUrl);
            fetchAndSetTitle('tv',id,season,episode);
            _pendingSubtitleArgs={type:'tv',tmdbId:id,season,episode};
        }else{hideLoader();displayError('Could not load episode. Please try again later.');}
        return;
    }

    // Default fallback
    initHlsPlayer('https://vidmmo.com/hls/ZDBtrL1WMPQipj3EubEdG6tAKeYJ0Nt3/master.m3u8');
}

/* =====================================================================
   UI BINDINGS
   ===================================================================== */
function setupInactivityDetection(){
    if(!isHlsJsMode&&video.audioTracks)video.audioTracks.addEventListener('change',renderTracksMenu);
    lastKnownVolume=video.volume>0?video.volume:0.5;
    updateProgress();updateBufferProgress();updateVolumeSlider();updateFullscreenIcon();
    updateNextEpisodeButton();
    if(video.paused||video.ended){showControls();updateBottomPlayPauseIcon(true);updateCenterPlayPauseIcon(true);}
    else{updateBottomPlayPauseIcon(false);updateCenterPlayPauseIcon(false);resetInactivityTimer();}
}

function setupUIControls(){
    let waitingTimeout=null,stalledTimeout=null;

    ['mousemove','mousedown','touchstart','touchend'].forEach(ev=>
        videoContainer.addEventListener(ev,resetInactivityTimer,ev.startsWith('touch')?{passive:true}:false)
    );

    topOverlay.addEventListener('click',()=>{
        if(window.innerWidth<=1000){
            const els=[document.getElementById('center-controls-mobile-only'),document.getElementById('controls-bar')];
            const anyHidden=els.some(el=>el.style.display==='none');
            els.forEach(el=>el.style.display=anyHidden?'flex':'none');
        }else{toggleVideoPlayPause();}
    });

    customPlayButton.addEventListener('click',toggleVideoPlayPause);
    centerPlayPauseButton.addEventListener('click',toggleVideoPlayPause);
    fullscreenButton.addEventListener('click',toggleFullscreen);
    skipBackwardButton.addEventListener('click',()=>{video.currentTime=Math.max(0,video.currentTime-10);resetInactivityTimer();});
    skipForwardButton.addEventListener('click',()=>{video.currentTime=Math.min(video.duration,video.currentTime+10);resetInactivityTimer();});
    mobileSkipBackwardButton.addEventListener('click',()=>{video.currentTime=Math.max(0,video.currentTime-10);resetInactivityTimer();});
    mobileSkipForwardButton.addEventListener('click',()=>{video.currentTime=Math.min(video.duration,video.currentTime+10);resetInactivityTimer();});
    muteButton.addEventListener('click',toggleMute);
    audioSubtitleToggle.addEventListener('click',e=>{e.stopPropagation();toggleAudioSubtitleMenu();});
    seekBar.addEventListener('mousedown',startSeeking);
    seekBar.addEventListener('touchstart',startSeeking,{passive:false});
    volumeControlWrapper.addEventListener('mouseenter',()=>volumeSliderContainer.classList.remove('hidden'));
    volumeControlWrapper.addEventListener('mouseleave',()=>setTimeout(()=>{if(!isVolumeAdjusting)volumeSliderContainer.classList.add('hidden');},300));

    document.addEventListener('fullscreenchange',updateFullscreenIcon);
    document.addEventListener('webkitfullscreenchange',updateFullscreenIcon);
    video.addEventListener('webkitbeginfullscreen',updateFullscreenIcon);
    video.addEventListener('webkitendfullscreen',updateFullscreenIcon);

    video.addEventListener('timeupdate',()=>{updateProgress();postTimeUpdateToParent();});
    video.addEventListener('progress',updateBufferProgress);
    video.addEventListener('loadedmetadata',()=>{
        updateProgress();updateBufferProgress();
        remainingTimeDisplay.textContent=`-${formatTime(video.duration)}`;
    });
    video.addEventListener('volumechange',updateVolumeSlider);

    // iOS fix: suppress loader during normal fragment loading
    // Only show loader if video is genuinely stalled (not just fetching next segment)
    video.addEventListener('waiting',()=>{
        if(_initialLoad)return; // suppress during initial load — canplay handles it
        if(waitingTimeout)clearTimeout(waitingTimeout);
        waitingTimeout=setTimeout(()=>{
            // Only show if video is not making progress
            if(!isSeeking&&!video.paused&&video.currentTime>0&&video.readyState<3){
                showLoader();
            }
        },600); // 600ms threshold — normal fragment loads are faster
    });

    video.addEventListener('stalled',()=>{
        if(_initialLoad)return;
        if(stalledTimeout)clearTimeout(stalledTimeout);
        stalledTimeout=setTimeout(()=>{
            if(!isSeeking&&!video.paused&&video.currentTime>0&&video.readyState<3){
                showLoader();
            }
        },1000);
    });

    video.addEventListener('canplay',()=>{
        if(waitingTimeout){clearTimeout(waitingTimeout);waitingTimeout=null;}
        if(stalledTimeout){clearTimeout(stalledTimeout);stalledTimeout=null;}
        hideLoader();stopBufferMonitor();
    });

    video.addEventListener('playing',()=>{
        if(waitingTimeout){clearTimeout(waitingTimeout);waitingTimeout=null;}
        if(stalledTimeout){clearTimeout(stalledTimeout);stalledTimeout=null;}
        // Only hide if not in initial load (canplay handles that)
        if(!_initialLoad)hideLoader();
        stopBufferMonitor();
    });

    video.addEventListener('seeked',()=>{if(!video.paused)hideLoader();});

    video.addEventListener('pause',()=>{
        showControls();updateBottomPlayPauseIcon(true);updateCenterPlayPauseIcon(true);
        clearTimeout(inactivityTimer);
    });
    video.addEventListener('play',()=>{
        updateBottomPlayPauseIcon(false);updateCenterPlayPauseIcon(false);resetInactivityTimer();
    });
    video.addEventListener('ended',()=>{
        showControls();updateBottomPlayPauseIcon(true);updateCenterPlayPauseIcon(true);hideLoader();
    });

    lastKnownVolume=video.volume>0?video.volume:0.5;
    updateProgress();updateBufferProgress();updateVolumeSlider();updateFullscreenIcon();
    if(video.paused||video.ended){showControls();updateBottomPlayPauseIcon(true);updateCenterPlayPauseIcon(true);}
    else{updateBottomPlayPauseIcon(false);updateCenterPlayPauseIcon(false);resetInactivityTimer();}
}

/* =====================================================================
   KEYBOARD
   ===================================================================== */
document.addEventListener('keydown',e=>{
    if(['INPUT','TEXTAREA'].includes(e.target.tagName))return;
    if(['Space','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.code))e.preventDefault();
    switch(e.code){
        case'Space':case'KeyK':toggleVideoPlayPause();break;
        case'ArrowLeft':video.currentTime=Math.max(0,video.currentTime-5);resetInactivityTimer();break;
        case'ArrowRight':video.currentTime=Math.min(video.duration,video.currentTime+5);resetInactivityTimer();break;
        case'KeyJ':video.currentTime=Math.max(0,video.currentTime-10);resetInactivityTimer();break;
        case'KeyL':video.currentTime=Math.min(video.duration,video.currentTime+10);resetInactivityTimer();break;
        case'ArrowUp':video.volume=Math.min(1,video.volume+0.05);video.muted=false;lastKnownVolume=video.volume;updateVolumeSlider();resetInactivityTimer();break;
        case'ArrowDown':video.volume=Math.max(0,video.volume-0.05);if(video.volume===0)video.muted=true;updateVolumeSlider();resetInactivityTimer();break;
        case'KeyM':toggleMute();break;
        case'KeyF':toggleFullscreen();break;
        case'KeyC':{const subs=Array.from(video.textTracks).filter(t=>t.kind==='subtitles'||t.kind==='captions');const showing=subs.some(t=>t.mode==='showing');subs.forEach((t,i)=>t.mode=showing?'disabled':(i===0?'showing':'disabled'));renderTracksMenu();resetInactivityTimer();break;}
        default:
            if(e.code.startsWith('Digit')){video.currentTime=(video.duration*parseInt(e.code.replace('Digit','')))/10;resetInactivityTimer();}
            else if(e.code==='Home'){video.currentTime=0;resetInactivityTimer();}
            else if(e.code==='End'){video.currentTime=video.duration;resetInactivityTimer();}
    }
});

/* =====================================================================
   REPORT MODAL
   ===================================================================== */
const reportModal=document.getElementById('reportModal'),issueTypeSelect=document.getElementById('issueType'),submitBtn=document.getElementById('submitBtn');
document.getElementById('report-button').addEventListener('click',()=>reportModal.classList.add('active'));
issueTypeSelect.addEventListener('change',()=>{submitBtn.disabled=issueTypeSelect.value==='';});
function closeReportModal(){reportModal.classList.remove('active');}
reportModal.addEventListener('click',e=>{if(e.target===reportModal)closeReportModal();});
async function submitIssue(){
    submitBtn.disabled=true;
    try{
        const r=await fetch('https://report.bingeoutofficial.workers.dev',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({issueType:issueTypeSelect.value,description:document.getElementById('issueDesc').value,pageUrl:location.href})});
        if(!r.ok)throw new Error('Failed');
        alert('Issue reported successfully');closeReportModal();
        issueTypeSelect.value='';document.getElementById('issueDesc').value='';submitBtn.disabled=true;
    }catch(e){alert('Failed to report. Try again.');}
    finally{submitBtn.disabled=issueTypeSelect.value==='';}
}

/* =====================================================================
   CLOSE MENUS ON OUTSIDE CLICK
   ===================================================================== */
document.addEventListener('click',e=>{
    if(!audioSubtitleMenu.classList.contains('hidden')&&!audioSubtitleMenu.contains(e.target)&&!audioSubtitleToggle.contains(e.target)&&window.innerWidth>=1000){audioSubtitleMenu.classList.add('hidden');resetInactivityTimer();}
    if(!speedMenu.classList.contains('hidden')&&!speedMenu.contains(e.target)&&!speedButton.contains(e.target)){speedMenu.classList.add('hidden');resetInactivityTimer();}
    if(!qualityMenu.classList.contains('hidden')&&!qualityMenu.contains(e.target)&&!qualityButton.contains(e.target)){qualityMenu.classList.add('hidden');resetInactivityTimer();}
});

window.onload=()=>{setupUIControls();resolveAndPlay();};
</script><div id="speed-quality-menu" class="hidden"></div>


<script src="https://cdn.jsdelivr.net/npm/eruda"></script></body><div id="eruda" style="all: initial;"></div><div class="__chobitsu-hide__" style="all: initial;"></div></html>
    """

    return HttpResponse(html_content, content_type="text/html", status=200)



def site_paused(request):
    return HttpResponse("<h1>Site is under maintenance</h1>", status=503)

