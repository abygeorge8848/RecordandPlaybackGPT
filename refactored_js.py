listeners = """
if (!window.hasInjected) {
    window.recordedEvents = [];
    window.hasInjected = true;
    window.isPaused = false;

    console.log("Listeners have been set up");
    function sendEventsToServerSync() {
        console.log("Sending the respective event to the server");
        if (window.isSending || window.recordedEvents.length === 0) {
            return; // Do not send if a send operation is in progress or if there are no events to send
        }
        window.isSending = true;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", 'http://localhost:9005/save', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    console.log('Event data sent successfully');
                }
                window.isSending = false;
                window.recordedEvents = []; // Clear the recorded events after sending
            }
        };

        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(window.recordedEvents));
    }

    var clickTimer;
    var doubleClickFlag = false;

    function getFrameInfo() {
        if (window !== window.top) {
            // Inside a frame
            return {
                isInFrame: true,
                frameId: window.frameElement ? window.frameElement.id : 'unknownFrame'
            };
        } else {
            // Not inside a frame
            return {
                isInFrame: false,
                frameId: null
            };
        }
    }

    function isInIframe() {
        return window !== window.top;
    }

    // Function to update frameDetected in localStorage
    function setFrameDetected(value) {
        localStorage.setItem('frameDetected', value.toString());
    }

    // Function to get frameDetected from localStorage
    function getFrameDetected() {
        return localStorage.getItem('frameDetected') === 'true';
    }

    window.frameDetected = getFrameDetected();


    document.addEventListener('dblclick', function(e) {
        console.log("Double Click ...");
        if (window.isPaused) return;
        doubleClickFlag = true;
        clearTimeout(clickTimer);
        var xpath = computeXPath(e.target);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['dblClick', Date.now(), xpath]);
        sendEventsToServerSync();
        doubleClickFlag = false;
    });

    document.addEventListener('click', function(e) {
        if (window.isPaused) return;
        if (!doubleClickFlag) {
            clearTimeout(clickTimer);
            clickTimer = setTimeout(function() {
                if (!doubleClickFlag) {
                    console.log("You clicked right now ...");
                    var xpath = computeXPath(e.target);
                    var frameInfo = getFrameInfo(e.target);
                    console.log(frameInfo);
                    var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
                    console.log(currentFrameDetected);
                    if (frameInfo.frameId !== null && !currentFrameDetected){
                        window.frameDetected = true;
                        console.log('Detected a frame for clicked element');
                        console.log(frameInfo.frameId);
                        setFrameDetected(true);
                        window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
                    } else if (frameInfo.frameId === null && currentFrameDetected){
                        window.frameDetected = false;
                        console.log('You have now left the frame to the parent body');
                        setFrameDetected(false);
                        window.recordedEvents.push(['frame', Date.now(), 'parent']);
                    }
                    window.recordedEvents.push(['click', Date.now(), xpath]);
                    sendEventsToServerSync();
                }
                doubleClickFlag = false;
            }, 300); // Adjust the timeout duration (300ms) as needed
        }
    });


    document.addEventListener('keypress', function(e) {
        if (window.isPaused) return;
        var xpath = computeXPath(e.target);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['input', Date.now(), xpath, e.key]);
        sendEventsToServerSync();  
    });

    function recordPageLoadEvent() {
        if (window.recordedEvents.length === 0 || window.recordedEvents[window.recordedEvents.length - 1][0] !== 'WaitForPageLoad') {
            window.recordedEvents.push(['WaitForPageLoad', Date.now()]);
            sendEventsToServerSync();  
        }
    }

    document.addEventListener('scroll', function(e) {
        if (window.isPaused) return;
        var xpath = computeXPathOfElementAt20Percent()
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['scroll', Date.now(), xpath]);
        sendEventsToServerSync();  
    });

    function computeXPathOfElementAt20Percent() {
        var yPosition = window.innerHeight * 0.25; 
        var elements = document.elementsFromPoint(window.innerWidth / 2, yPosition);
        for (var i = 0; i < elements.length; i++) {
            var xpath = computeXPath(elements[i]);
            if (xpath) {
                return xpath;
            }
        }
        return null;
    }

    recordPageLoadEvent();

    function computeXPath(element) {
        if (!element) return null;

        function escapeXPathString(str) {
            if (!str.includes("'")) return `'${str}'`;
            if (!str.includes('"')) return `"${str}"`;
            let parts = str.split("'");
            let xpathString = "concat(";
            for (let i = 0; i < parts.length; i++) {
                xpathString += `'${parts[i]}'`;
                if (i < parts.length - 1) {
                    xpathString += `, "'", `;
                }
            }
            xpathString += ")";

            return xpathString;
        }

        function isUniqueByAttribute(element, attrName) {
            let attrValue = element.getAttribute(attrName);
            if (!attrValue) return false;
            let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
            return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
        }

        function isUniqueByText(element) {
            let text = element.textContent.trim();
            if (!text) return false;
            let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
            return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
        }

        function getChildRelativeXPath(child, parent) {
            var path = '';
            for (var current = child; current && current !== parent; current = current.parentNode) {
                let index = 1;
                for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                    if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                        index++;
                    }
                }
                let tagName = current.tagName.toLowerCase();
                let pathIndex = (index > 1 ? `[${index}]` : '');
                path = '/' + tagName + pathIndex + path;
            }
            return path;
        }

        // Function to generate a unique XPath using parent attributes
        function generateRelativeXPath(element) {
            var paths = [];
            var currentElement = element;

            while (currentElement && currentElement.nodeType === 1) {
                let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                if (uniqueAttributeXPath) {
                    paths.unshift(uniqueAttributeXPath);
                    break; // Break the loop if a unique attribute is found
                }

                let tagName = currentElement.tagName.toLowerCase();
                let index = 1;
                for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                    if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                        index++;
                    }
                }
                let pathIndex = (index > 1 ? `[${index}]` : '');
                paths.unshift(`${tagName}${pathIndex}`);

                currentElement = currentElement.parentNode;
            }

            return paths.length ? `//${paths.join('/')}` : null;
        }

        function getUniqueAttributeXPath(element) {
            const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
            for (let attr of attributes) {
                if (isUniqueByAttribute(element, attr)) {
                    return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                }
            }
            return null;
        }    

        // Special handling for svg elements
        if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
            let parentElement = element.parentElement;
            if (parentElement) {
                let parentXPath = computeXPath(parentElement);
                if (parentXPath) {
                    if (parentXPath.startsWith('//')){
                        return parentXPath;
                    } else if (parentXPath.startsWith('/')){
                        return '/' + parentXPath;
                    } else {
                        return '//' + parentXPath;
                    }	
                }
            }
            return null;
        }

        const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
        for (let attr of attributes) {
            if (isUniqueByAttribute(element, attr)) {
                return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
            }
        }

        if (element.className && typeof element.className === 'string') {	
            let classes = element.className.trim().split(/\s+/);
            let combinedClassSelector = classes.join('.');
            let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
            if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                return xpath;
            }
        }

        if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
            return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
        }

        return generateRelativeXPath(element);
        }          



}
"""

xpath_js = """
            var callback = arguments[arguments.length - 1];  // The callback function provided by Selenium

            function sendEventsToServerSync() {
                console.log("Sending the respective event to the server");
                if (window.isSending || window.recordedEvents.length === 0) {
                    return; // Do not send if a send operation is in progress or if there are no events to send
                }
                window.isSending = true;

                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'http://localhost:9005/save', true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            console.log('Event data sent successfully');
                        }
                        window.isSending = false;
                        window.recordedEvents = []; // Clear the recorded events after sending
                    }
                };

                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(window.recordedEvents));
            }

            function getFrameInfo() {
                if (window !== window.top) {
                    // Inside a frame
                    return {
                        isInFrame: true,
                        frameId: window.frameElement ? window.frameElement.id : 'unknownFrame'
                    };
                } else {
                    // Not inside a frame
                    return {
                        isInFrame: false,
                        frameId: null
                    };
                }
            }

            function isInIframe() {
                return window !== window.top;
            }

            // Function to update frameDetected in localStorage
            function setFrameDetected(value) {
                localStorage.setItem('frameDetected', value.toString());
            }

            // Function to get frameDetected from localStorage
            function getFrameDetected() {
                return localStorage.getItem('frameDetected') === 'true';
            }

            window.frameDetected = getFrameDetected();


            document.addEventListener('click', function getTextEvent(e) {
                e.preventDefault();
                e.stopPropagation();
                var xpath = computeXPath(e.target);
                var frameInfo = getFrameInfo(e.target);
                console.log(frameInfo);
                var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
                console.log(currentFrameDetected);
                if (frameInfo.frameId !== null && !currentFrameDetected){
                    window.frameDetected = true;
                    console.log('Detected a frame for clicked element');
                    console.log(frameInfo.frameId);
                    setFrameDetected(true);
                    window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
                    sendEventsToServerSync();
                } else if (frameInfo.frameId === null && currentFrameDetected){
                    window.frameDetected = false;
                    console.log('You have now left the frame to the parent body');
                    setFrameDetected(false);
                    window.recordedEvents.push(['frame', Date.now(), 'parent']);
                    sendEventsToServerSync();
                }
                console.log(xpath);
                callback(xpath);  // Call the callback with the XPath as the argument
            });

            function computeXPath(element) {
                if (!element) return null;

                function escapeXPathString(str) {
                    if (!str.includes("'")) return `'${str}'`;
                    if (!str.includes('"')) return `"${str}"`;
                    let parts = str.split("'");
                    let xpathString = "concat(";
                    for (let i = 0; i < parts.length; i++) {
                        xpathString += `'${parts[i]}'`;
                        if (i < parts.length - 1) {
                            xpathString += `, "'", `;
                        }
                    }
                    xpathString += ")";

                    return xpathString;
                }

                function isUniqueByAttribute(element, attrName) {
                    let attrValue = element.getAttribute(attrName);
                    if (!attrValue) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function isUniqueByText(element) {
                    let text = element.textContent.trim();
                    if (!text) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function getChildRelativeXPath(child, parent) {
                    var path = '';
                    for (var current = child; current && current !== parent; current = current.parentNode) {
                        let index = 1;
                        for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                                index++;
                            }
                        }
                        let tagName = current.tagName.toLowerCase();
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        path = '/' + tagName + pathIndex + path;
                    }
                    return path;
                }

                // Function to generate a unique XPath using parent attributes
                function generateRelativeXPath(element) {
                    var paths = [];
                    var currentElement = element;

                    while (currentElement && currentElement.nodeType === 1) {
                        let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                        if (uniqueAttributeXPath) {
                            paths.unshift(uniqueAttributeXPath);
                            break; // Break the loop if a unique attribute is found
                        }

                        let tagName = currentElement.tagName.toLowerCase();
                        let index = 1;
                        for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                                index++;
                            }
                        }
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        paths.unshift(`${tagName}${pathIndex}`);

                        currentElement = currentElement.parentNode;
                    }

                    return paths.length ? `//${paths.join('/')}` : null;
                }

                function getUniqueAttributeXPath(element) {
                    const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                    for (let attr of attributes) {
                        if (isUniqueByAttribute(element, attr)) {
                            return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                        }
                    }
                    return null;
                }    

                // Special handling for svg elements
                if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
                    let parentElement = element.parentElement;
                    if (parentElement) {
                        let parentXPath = computeXPath(parentElement);
                        if (parentXPath) {
                            if (parentXPath.startsWith('//')){
                                return parentXPath;
                            } else if (parentXPath.startsWith('/')){
                                return '/' + parentXPath;
                            } else {
                                return '//' + parentXPath;
                            }	
                        }
                    }
                    return null;
                }

                const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                for (let attr of attributes) {
                    if (isUniqueByAttribute(element, attr)) {
                        return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                    }
                }

                if (element.className && typeof element.className === 'string') {	
                    let classes = element.className.trim().split(/\s+/);
                    let combinedClassSelector = classes.join('.');
                    let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
                    if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                        return xpath;
                    }
                }

                if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
                    return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
                }

                return generateRelativeXPath(element);
                }
        """








