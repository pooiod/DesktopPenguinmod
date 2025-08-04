// Makes all links for penguinmod stay on the main browser window
if (window.location.host == "studio.penguinmod.com" || window.location.host == "penguinmod.com") {
    function updateLinks() {
        const links = document.querySelectorAll('a[href]');
        links.forEach(link => {
            try {
                const url = new URL(link.href);
                if (!['penguinmod.com', 'studio.penguinmod.com'].includes(url.host)) {
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                } else {
                    link.target = '_self';
                    link.removeAttribute('rel');
                }
            } catch {}
        });
    }

    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    if (node.tagName === 'A') updateLinks();
                    else if (node.querySelectorAll) {
                        if (node.querySelector('a')) updateLinks();
                    }
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    updateLinks();
}

function editorExtras() {
    // makes addons open in an iframe (greasyfork.org/en/scripts/524781)
    (function() {
        'use strict';
    
        setInterval(() => {
            const AddonsButton = Array.from(document.querySelectorAll('div')).find(btn => {
                const div = btn.querySelector('div');
                const span = div?.querySelector('span');
                if (span?.textContent.trim() === 'Addons') {
                    return btn;
                }
            });
            const existingButton = document.getElementById("StylishAddonsButton");
    
            if (AddonsButton && !existingButton) {
                const newAddonsButton = AddonsButton.cloneNode(true);
                newAddonsButton.id = "StylishAddonsButton";
                AddonsButton.parentNode.replaceChild(newAddonsButton, AddonsButton);
    
                newAddonsButton.addEventListener("click", function(event) {
                    event.preventDefault();
                    event.stopImmediatePropagation();
    
                    if (document.getElementById("widgetoverlay")) return;
    
                    const overlay = document.createElement('div');
                    overlay.style.position = 'fixed';
                    overlay.style.top = '0';
                    overlay.style.left = '0';
                    overlay.style.width = '100%';
                    overlay.style.height = '100%';
                    overlay.style.backgroundColor = 'rgba(0, 195, 255, 0.7)';
                    overlay.style.zIndex = '9999';
                    overlay.id = "widgetoverlay";
    
                    const wrapper = document.createElement('div');
                    wrapper.style.position = 'absolute';
                    wrapper.style.top = "50%";
                    wrapper.style.left = "50%";
                    wrapper.style.transform = 'translate(-50%, -50%)';
                    wrapper.style.border = '4px solid rgba(255, 255, 255, 0.25)';
                    wrapper.style.borderRadius = '13px';
                    wrapper.style.padding = '0px';
                    wrapper.style.width = '70vw';
                    wrapper.style.height = '80vh';
    
                    const modal = document.createElement('div');
                    modal.style.backgroundColor = 'var(--ui-primary, white)';
                    modal.style.padding = '0px';
                    modal.style.borderRadius = '10px';
                    modal.style.width = '100%';
                    modal.style.height = '100%';
                    modal.style.textAlign = 'center';
    
                    wrapper.appendChild(modal);
    
                    const title = document.createElement('div');
                    title.style.position = 'absolute';
                    title.style.top = '0';
                    title.style.left = '0';
                    title.style.width = '100%';
                    title.style.height = '50px';
                    title.style.backgroundColor = 'rgb(0, 195, 255)';
                    title.style.display = 'flex';
                    title.style.justifyContent = 'center';
                    title.style.alignItems = 'center';
                    title.style.color = 'white';
                    title.style.fontSize = '24px';
                    title.style.borderTopLeftRadius = '10px';
                    title.style.borderTopRightRadius = '10px';
                    title.innerHTML = "Addons";
    
                    const iframe = document.createElement('iframe');
                    iframe.src = '/addons.html';
                    iframe.style.width = '100%';
                    iframe.style.height = `calc(100% - 50px)`;
                    iframe.style.marginTop = '50px';
                    iframe.style.border = 'none';
                    iframe.style.borderBottomLeftRadius = '10px';
                    iframe.style.borderBottomRightRadius = '10px';
                    modal.appendChild(iframe);
    
                    const closeButton = document.createElement('div');
                    closeButton.setAttribute('aria-label', 'Close');
                    closeButton.classList.add('close-button_close-button_lOp2G', 'close-button_large_2oadS');
                    closeButton.setAttribute('role', 'button');
                    closeButton.setAttribute('tabindex', '0');
                    closeButton.innerHTML = '<img class="close-button_close-icon_HBCuO" src="data:image/svg+xml,%3Csvg%20data-name%3D%22Layer%201%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%207.48%207.48%22%3E%3Cpath%20d%3D%22M3.74%206.48V1M1%203.74h5.48%22%20style%3D%22fill%3Anone%3Bstroke%3A%23fff%3Bstroke-linecap%3Around%3Bstroke-linejoin%3Around%3Bstroke-width%3A2px%22%2F%3E%3C%2Fsvg%3E">';
                    closeButton.style.position = 'absolute';
                    closeButton.style.top = '50%';
                    closeButton.style.right = '10px';
                    closeButton.style.transform = 'translateY(-50%)';
                    closeButton.style.zIndex = '1000';
                    closeButton.addEventListener('click', () => {
                        document.body.removeChild(overlay);
                    });
                    title.appendChild(closeButton);
    
                    modal.appendChild(title);
                    overlay.appendChild(wrapper);
                    document.body.appendChild(overlay);
    
                    overlay.addEventListener('click', (e) => {
                        if (e.target === overlay) {
                            document.body.removeChild(overlay);
                        }
                    });
                });
            }
        }, 1000);
    })();

    // adds my extension gallary to the list (p7scratchextensions.pages.dev/extras/js/pmgallary.js)
    (function() {
        'use strict';

        function checkAndInsertExtensionGallery() {
        const targetSpan = Array.from(document.querySelectorAll('span'))
        .find(span => span.textContent.trim() === 'PenguinMod Extra Extensions');

        if (document.querySelector('#p7extensionslist')) {
            document.querySelector('#p7extensionslist').remove();
        }

        if (targetSpan && Array.from(document.querySelectorAll('span'))
            .find(span => span.textContent.trim() === 'TurboWarp Extension Gallery')) {
            const parentElement = targetSpan.closest('span').parentElement.parentElement;

            const newHTML = `
                <div id="p7extensionslist" class="library-item_library-item_1DcMO library-item_featured-item_3V2-t library-item_library-item-extension_3xus9" onclick="window.open('https://p7scratchextensions.pages.dev')">
                <div class="library-item_featured-image-container_1KIHG">
                    <img class="library-item_featured-image_2gwZ6" loading="lazy" draggable="false" src="https://p7scratchextensions.pages.dev/extras/images/P7ExtGalleryCover.png">
                </div>
                <div class="library-item_featured-extension-text_22A1k library-item_featured-text_2KFel">
                    <span class="library-item_library-item-name_2qMXu"><span>Pooiod7's extensions</span></span><br>
                    <span class="library-item_featured-description_MjIJw"><span>Explore a large collection of Scratch extensions made by Pooiod7.</span></span>
                </div>
                </div>
            `;
            parentElement.insertAdjacentHTML('afterend', newHTML);
        }
        }

        setInterval(checkAndInsertExtensionGallery, 1000);
    })();
}

if (window.location.host == "studio.penguinmod.com") {
    // BlockLink replaces the home button remover addon
    if (window.location.href.includes("addons.html")) {
        function doReplacement() {
            document.querySelectorAll('.settings_addon-title-text_3QjlP').forEach(el => {
                if (el.textContent.trim() === 'Remove Back to Home button') el.textContent = 'BlockLink';
            });
            document.querySelectorAll('.settings_description_2MbZo, .settings_inline-description_SovV9').forEach(el => {
                if (el.textContent.trim() === 'Removes the Back to Home button from the menu bar.') {
                    el.textContent = 'Adds the ability to edit a project at the same time as another user';
                }
            });
        }

        const observer = new MutationObserver(() => {
            doReplacement();
        });

        observer.observe(document.body, { childList: true, subtree: true });
        doReplacement();
    } else {
        editorExtras();

        // Always remove the default home button because AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        const style = document.createElement('style');
        style.textContent = `a[class^="menu-bar_feedback-link_"] { display: none; }`;
        document.head.appendChild(style);

        setTimeout(() => {
            // BlockLink replaces the home button remover addon
            const scripts = document.querySelectorAll('script[src*="addon-entry-tw-remove-feedback.cafc2661378f8a4f0070.js"]');
            scripts.forEach(script => {
                const replacement = document.createElement('script');
                replacement.src = 'https://p7scratchextensions.pages.dev/ext/BlockLink/inject.js';
                script.parentNode.replaceChild(replacement, script);
            });

            // Super cool and epic user card thingy
            setInterval(function() {
                var parent = document.querySelector('.menu-bar_account-info-group_MeJZP');
                if (!parent || parent.querySelector('.account-nav_user-info_dUiXV')) return;

                var ud = window.vm && vm.runtime && vm.runtime.ioDevices && vm.runtime.ioDevices.userData;
                var loggedIn = ud && ud._loggedIn;
                var username = loggedIn ? ud._username : null;

                var wrapper = document.createElement('div');
                wrapper.className = 'account-nav_user-info_dUiXV menu-bar_menu-bar-item_NKeCD menu-bar_menu-bar-item_oLDa- menu-bar_hoverable_c6WFB';
                wrapper.style.cssText = 'display:flex;align-items:center;padding:0 10px;';

                var a = document.createElement('a');
                a.style.cssText = 'display:flex;align-items:center;text-decoration:none;color:inherit;';
                a.href = loggedIn ? 'https://penguinmod.com/profile?user=' + username : 'https://penguinmod.com';

                if (loggedIn) {
                    var img = document.createElement('img');
                    img.className = 'account-nav_avatar_Drhc7 user-avatar_user-thumbnail_G9XFP';
                    img.src = 'https://projects.penguinmod.com/api/v1/users/getpfp?username=' + username;
                    img.referrerPolicy = 'no-referrer';
                    img.style.cssText = 'width:30px;height:30px;border-radius:5px;border:1px solid rgba(0,0,0,0.1);';
                    a.appendChild(img);
                }

                var span = document.createElement('span');
                span.className = 'account-nav_profile-name_COfZL';

                if (loggedIn) {
                    span.style.marginLeft = '8px';
                    span.innerText = username;
                } else {
                    span.innerText = 'Home';
                }

                a.appendChild(span);
                wrapper.appendChild(a);
                parent.appendChild(wrapper);
            }, 1000);
        }, 2000);
    }
} else if (window.location.host == "penguinmod.com") {
    // PyQt5 does not play nicely with the Cloudflare challenges or google logins
    if (window.location.href.includes("signin")) {
        const GoogleLoginInterval = setInterval(() => {
            const buttons = document.querySelectorAll('.gsi-material-button');
            if (buttons.length > 0) {
                buttons.forEach(el => {
                    if (el.textContent.includes('Google')) {
                        el.style.opacity = '0.5';
                        el.style.pointerEvents = 'none';

                        const loginelunsuported = document.querySelector('.or-line.svelte-yl8gw9');
                        if (loginelunsuported) {
                            let next = loginelunsuported.nextSibling;
                            while (next) {
                                const toRemove = next;
                                next = next.nextSibling;
                                toRemove.remove();
                            }
                            loginelunsuported.remove();
                        }

                        if ([...document.scripts].some(s => s.src.includes('challenges.cloudflare.com'))) {
                            const paragraphs = document.querySelectorAll('p.svelte-yl8gw9');

                            document.querySelector(".old-accounts-warning")?.remove()
                            paragraphs.forEach(paragraph => {
                                const warningHTML = `
                                    <div class="old-accounts-warning svelte-yl8gw9">
                                        <p>
                                            Due to browser based authentication issues, some login methods are currently unavailable. If you don't have any of these accounts linked you can log in with your browser and link them.
                                            <br> This is not an issue with PenguinMod
                                        </p>
                                    </div>
                                `;
                                paragraph.insertAdjacentHTML('afterend', warningHTML);
                            });
                        }
                    }
                });
                clearInterval(GoogleLoginInterval);
            }
        }, 100);
    }
} else {
    if (window.location.host == "scratch.mit.edu") {
        (function() {
            // Add a loader for scratch so it is not just a blank page of purple
            const loader5676 = document.createElement('div');
            loader5676.style.position = 'fixed';
            loader5676.style.top = '50%';
            loader5676.style.left = '50%';
            loader5676.style.transform = 'translate(-50%, -50%)';
            loader5676.style.zIndex = '9999999999999999999999';
            loader5676.style.width = '100px';
            loader5676.style.height = '100px';
            loader5676.innerHTML = `
                <svg viewBox="0 0 100 100" style="width:100%;height:100%;animation:spin 1s linear infinite">
                <circle cx="50" cy="50" r="40" stroke="#fff" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="188.4" stroke-dashoffset="141.3"/>
                </svg>
                <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
            `;
            document.body.appendChild(loader5676);

            const checkText453 = setInterval(() => {
                if (document.body.innerText.trim().length > 0) {
                    clearInterval(checkText453);
                    loader5676.remove();
                }
            }, 1000);

            // A script to make f=a=>a*a functions work because PyQt5 does not like minification
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/@babel/standalone@7.21.0/babel.min.js';
            script.onload = function() {
                console.log("Compiling scripts...");
                var scripts = document.querySelectorAll('script[type="text/babel"]');
                scripts.forEach(function(script) {
                    var code = script.textContent;
                    var transpiledCode = Babel.transform(code, {
                        presets: ['env']
                    }).code;
                    var newScript = document.createElement('script');
                    newScript.textContent = transpiledCode;
                    document.body.appendChild(newScript);
                });

                var externalScripts = document.querySelectorAll('script[src]');
                externalScripts.forEach(function(script) {
                    var url = script.src;
                    fetch(url)
                        .then(response => response.text())
                        .then(code => {
                            var transpiledCode = Babel.transform(code, {
                                presets: ['env']
                            }).code;
                            var newScript = document.createElement('script');
                            newScript.textContent = transpiledCode;
                            document.body.appendChild(newScript);
                        })
                        .catch(error => console.error('Error loading external script:', error));
                });

                console.log("Scripts compiled.");
            };
            document.head.appendChild(script);
        })();
    }
}
