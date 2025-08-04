const trackedResources = new Set();
const resourceList = [];

function toAbsolute(url) {
    const a = document.createElement('a');
    a.href = url;
    return a.href;
}

function isValid(src) {
    return src && !src.startsWith('data:') && (src.startsWith('http') || src.startsWith('//') || src.startsWith('/') || src.includes('/'));
}

function addResource(src) {
    if (!isValid(src)) return;
    const absUrl = toAbsolute(src);
    if (!trackedResources.has(absUrl)) {
        trackedResources.add(absUrl);
        resourceList.push(absUrl);
        console.log('Added:', absUrl);
    }
}

function checkResources() {
    const elements = [
        ...document.querySelectorAll('script[src]'),
        ...document.querySelectorAll('link[rel="stylesheet"][href]'),
        ...document.querySelectorAll('img[src]'),
        ...document.querySelectorAll('audio[src]')
    ];
    for (const el of elements) {
        const src = el.src || el.href;
        addResource(src);
    }
}

function addInitialResources() {
    addResource(location.href);
    // addResource(location.origin + '/addons.html');
    checkResources();
}

const observer = new MutationObserver(() => checkResources());
observer.observe(document, { childList: true, subtree: true });

addInitialResources();
setInterval(checkResources, 1000);

document.addEventListener('keydown', e => {
    if (e.key === 'h') {
        console.log(JSON.stringify(resourceList, null, 2));
    }
});
