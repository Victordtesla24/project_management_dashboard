# Network Filters
||ads.*^$third-party,important
||analytics.*^$third-party,important
||tracker.*^$third-party,important
||metrics.*^$third-party,important
||cdn4ads.*^$third-party,important
||telemetry.*^$third-party,important
||*/advert.$third-party,important
||*/stats.$third-party,important
||*/pixel.$third-party,important
||*/beacon.$third-party,important
||*/collect.$third-party,important

# Advanced Anti-Detection (2024)
*##+js(set-constant, Object.prototype.hasAdblock, undefined)
*##+js(nano-stb, .offsetHeight)
*##+js(set-constant, adblockDetector, null)
*##+js(no-fetch-if, /adblock|ad-check|ad-detect/)
*##+js(abort-current-script, document.createElement, /ads|analytics/)
*##+js(trusted-set-local-storage-item, adblock_detected, false)
*##+js(abort-on-property-read, /^[a-zA-Z]{1,20}Detector$/)
*##+js(no-setTimeout-if, /check|detect/)
*##+js(remove-attr, data-adblockkey)
*##+js(set-constant, canRunAds, true)
*##+js(set-constant, adBlockDisabled, true)
*##+js(no-setInterval-if, /blockAdBlock|AdBlock|adsBlocked/)
*##+js(abort-current-script, /wpadgu-frontend|vyECXakRudwr/)
*##+js(set-constant, Object.prototype.checkAdStatus, undefined)
*##+js(trusted-set-cookie, ad_blocker_status, disabled)
*##+js(prevent-addEventListener, load, /adBlock|checkAds/)
*##+js(prevent-setTimeout, /detectAdBlock|checkForAds/, 1)

# Enhanced Popup Prevention (2024)
||*.com^$popup,domain=~allowlist.example.com|~trusted-site.com
||*.net^$popup,domain=~allowlist.example.com|~trusted-site.com
||*.org^$popup,domain=~allowlist.example.com|~trusted-site.com
*##+js(window.open-defuser)
*##+js(no-window-open-if, /popup|modal|overlay|lightbox/)
*##+js(remove-attr, onclick|target, [onclick*="window.open"])
##[class*="popup"]:has(iframe)
##[id*="modal"]:has([class*="ad"])
##[id*="popup-overlay"]
##div[class*="lightbox"]:has(iframe)
*##+js(no-setInterval-if, /pop|modal|overlay/)
*##+js(prevent-window-open)
*##+js(no-setTimeout-if, /showModal|displayPopup/)
##div[class*="modal-backdrop"]
##div[role="dialog"][class*="popup"]
*##+js(remove-class, modal-open, body)

# Intelligent Resource Protection
@@||example.com^$image
@@||example.com^$media
@@||example.com^$font
@@||*/ads.js$script,1p
@@||*/advertisement.js$script,1p
@@||*/advertisement-loader.js$script,1p
@@||cdn.*.com^$image
@@||cdn.*.com^$media
@@||cdn.*.com^$font
@@||api.*.com^$xmlhttprequest
@@||*.cloudfront.net^$image
@@||*.cloudfront.net^$media
@@||*.akamai.net^$image
@@||*.akamai.net^$media
@@||*.fastly.net^$image
@@||*.fastly.net^$media
@@||player.*.com^$media
@@||player.*.com^$xmlhttprequest

# Advanced Network Security
||*^$websocket,domain=example.com,important
||*^$xmlhttprequest,domain=example.com,important
||*^$ping,domain=example.com,important
*##+js(no-xhr-if, /analytics|tracking|telemetry/)
*##+js(abort-on-property-read, navigator.sendBeacon)
*##+js(prevent-fetch, /collect|track|analyze/)
*##+js(no-websocket-if, /analytics|tracking/)
*##+js(prevent-beacon)

# Performance Optimization
*##+js(nano-setInterval-booster)
*##+js(nano-setTimeout-booster)
*##+js(no-fetch-if, /analytics|tracking/)
*##+js(abort-on-stack-trace, /adblock/)
*##+js(set-constant, performance.timing, undefined)
*##+js(no-requestIdleCallback-if, /detect|check/)
*##+js(prevent-requestAnimationFrame, /check|detect/)
*##+js(set-constant, performance.memory, undefined)
*##+js(abort-current-script, /GoogleAnalytics|gtag|fbq/)

# Enhanced DOM Protection
##[src*="analytics"]
##[src*="tracker"]
##[src*="metrics"]
##[data-ad-client]
##[data-ad-slot]
##.adsbygoogle
##div[id^="div-gpt-ad"]
##div[class*="ad-container"]
##[class*="sponsored-content"]
##[id*="banner-ad"]
##iframe[src*="doubleclick"]
##div[data-google-query-id]

# Advanced Injection Prevention
*##+js(abort-current-script, /ad|analytics/)
*##+js(abort-on-property-read, detectAdBlock)
*##+js(set, Object.defineProperty, noopFunc)
*##+js(prevent-addEventListener, /scroll|mousemove/, /detect|check/)
*##+js(prevent-setInterval, /check|detect/, 100)
*##+js(trusted-set-constant, document.hasFocus, () => true)
*##+js(set-constant, document.hidden, false)
*##+js(prevent-mutation-observer, /ad|banner|popup/)

# Anti-Detection Message Prevention
##div[class*="adblock-notice"]
##div[id*="adblock-notification"]
##div[class*="ad-block-message"]
##.adblock-warning
##.adblock-stop
##div[class*="detectadblock"]
##div[id*="detect-adblock"]
##.anti-adblock-notice
##div[class*="adb-warning"]
##div[id*="check-adblock"]
##.adblock-overlay
##div[class*="whitelist-notice"]
##div[id*="whitelist-message"]
*##+js(remove-class, has-adblock, body)
*##+js(remove-class, adblock-detected, html)
*##+js(trusted-set-cookie, whitelisted, true)

# Advanced Message Bypass (2024)
*##+js(set-constant, showAdblockMessage, noopFunc)
*##+js(abort-current-script, /checkAdblockStatus|detectAdBlock/)
*##+js(prevent-setTimeout, /showMessage|displayWarning/, 1)
*##+js(remove-attr, style, body[style*="overflow: hidden"])
*##+js(no-setInterval-if, /checkWhitelist|verifyAdblock/)
*##+js(trusted-set-local-storage-item, whitelisted, true)
*##+js(set-constant, Object.prototype.showBlockerMessage, undefined)
##div[style*="z-index: 999999"]
##div[class*="overlay"][style*="position: fixed"]
##.modal-backdrop
##div[class*="dimmer"]

# DOM Cleanup Rules
*##+js(remove-element, div[id*="adblock"])
*##+js(remove-element, div[class*="adblock-detected"])
*##+js(remove-element, div[class*="whitelist"])
*##+js(prevent-append, div[class*="message"])
##div[style*="position: fixed"][class*="message"]
##div[style*="position: absolute"][id*="notice"]
##div[role="dialog"][class*="adblock"]
##div[role="alertdialog"]

# Enhanced Overlay Prevention
*##+js(set-constant, document.body.style.overflow, '')
*##+js(set-constant, document.documentElement.style.overflow, '')
*##+js(prevent-addEventListener, scroll, /checkScroll|preventScroll/)
*##+js(no-setTimeout-if, /enableScroll|disableScroll/)
##div[style*="backdrop-filter"]
##div[style*="pointer-events: all"]
##.modal-open
##body[style*="overflow: hidden"] .overlay

# Safari-Specific Optimizations (M3)
*##+js(safari-defuser)
*##+js(prevent-safari-popup)
##safari-web-extension[style*="display: block"]
##.safari-popup-warning
*##+js(set-constant, safari.pushNotification, noopFunc)

# Enhanced Safari Popup Prevention
||*^$popup,domain=~allowlist.example.com|~trusted-site.com,important
*##+js(window.open-defuser, safari)
*##+js(no-window-open-if, /notification|subscribe|alert/)
*##+js(prevent-window-open, /popup|modal|overlay/, true)
##div[class*="notification-prompt"]
##div[id*="push-prompt"]
##.push-notification-box

# Advanced Network Security (Safari-Compatible)
||*^$websocket,domain=example.com,important
||*^$xmlhttprequest,domain=example.com,important
||*^$ping,domain=example.com,important
*##+js(no-xhr-if, /analytics|tracking|telemetry/)
*##+js(prevent-fetch, /collect|track|analyze/)
*##+js(no-websocket-if, /analytics|tracking/)

# Safari-Specific Resource Protection
@@||example.com^$image
@@||example.com^$media
@@||example.com^$font
@@||cdn.*.com^$image
@@||cdn.*.com^$media
@@||cdn.*.com^$font
@@||api.*.com^$xmlhttprequest
@@||*.cloudfront.net^$image
@@||*.cloudfront.net^$media
@@||*.akamai.net^$image
@@||*.akamai.net^$media
@@||*.fastly.net^$image
@@||*.fastly.net^$media
@@||player.*.com^$media
@@||player.*.com^$xmlhttprequest

# Additional Safari Optimizations
*##+js(set-constant, safari.pushNotification.permission, "denied")
*##+js(prevent-notification-api)
*##+js(no-setInterval-if, /checkPermission|requestNotification/)
##div[class*="browser-notification"]
##.notification-request
##div[id*="notification-prompt"]

# Safari Developer Settings:
# 1. Enable in Safari > Develop:
#    - Disable Cross-Origin Restrictions
#    - Enable JavaScript from Smart Search field
#    - Enable Intelligent Tracking Prevention debug mode
#    - Enable Private Click Measurement debug mode
# 2. Additional Settings:
#    - Block all third-party cookies
#    - Prevent cross-site tracking
#    - Hide IP address from trackers
#    - Block all pop-ups
#    - Disable auto-play
#    - Block all notifications

# M3-Optimized Rules
*##+js(set-constant, navigator.hardwareConcurrency, 8)
*##+js(set-constant, navigator.deviceMemory, 8)
*##+js(prevent-addEventListener, devicemotion)
*##+js(prevent-addEventListener, deviceorientation)
*##+js(set-constant, window.safari.private, undefined)
##div[class*="hardware-acceleration"]
##div[id*="performance-notice"]

# Resource Type Definitions
# image - Images and icons
# media - Audio and video content
# font - Font files
# xmlhttprequest - Ajax requests
# websocket - WebSocket connections
# ping - Navigator beacon
