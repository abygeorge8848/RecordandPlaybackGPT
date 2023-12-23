if (!window.hasInjected) {
    window.hasInjected = true;
        
    document.addEventListener('contextmenu', function(e) {
          e.preventDefault(); // Prevents the browser's context menu from showing up
          var xpath = computeXPath(e.target);
          console.log(`You have right clicked on : \n ${xpath}`);
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
                let uniqueXPath = getUniqueXPathForElement(currentElement);
                if (uniqueXPath) {
                    paths.unshift(uniqueXPath);
                    break; // Break the loop if a unique identifier is found
                }
    
                let parentTextXPath = getParentTextXPath(currentElement);
                if (parentTextXPath) {
                    paths.unshift(parentTextXPath);
                    break; // Use parent text content for XPath if it provides uniqueness
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
        

        function getParentTextXPath(element) {
            let parent = element.parentNode;
            if (!parent || parent.nodeType !== 1) {
                return null;
            }
    
            let parentText = parent.textContent.trim();
            let childText = Array.from(parent.childNodes).filter(n => n.nodeType === Node.TEXT_NODE).map(n => n.textContent.trim()).join('').trim();
    
            // Check if parent's own text (excluding children's text) is unique and significant
            if (parentText !== childText && parentText.includes(childText) && isUniqueByText(parent, parentText.replace(childText, '').trim())) {
                return `${parent.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(parentText.replace(childText, '').trim())})]`;
            }
    
            return null;
        }

        function isUniqueByCombinedAttributes(element, attributes) {
            let xpath = `//${element.tagName.toLowerCase()}`;
            let attributeConditions = [];
        
            for (let attr of attributes) {
                let attrValue = element.getAttribute(attr);
                if (attrValue) {
                    attributeConditions.push(`@${attr}=${escapeXPathString(attrValue)}`);
                }
            }
        
            if (attributeConditions.length === 0) return false;
        
            xpath += '[' + attributeConditions.join(' and ') + ']';
            return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
        }
        
    
        function getUniqueXPathForElement(element) {
            // First, try to find a unique XPath using a single attribute
            let uniqueAttributeXPath = getUniqueAttributeXPath(element);
            if (uniqueAttributeXPath) {
                return uniqueAttributeXPath;
            }
        
            // If single attribute is not unique, try a combination of attributes
            const combinedAttributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind']; // Customize this list as needed
            if (isUniqueByCombinedAttributes(element, combinedAttributes)) {
                let conditions = combinedAttributes
                    .filter(attr => element.getAttribute(attr))
                    .map(attr => `@${attr}=${escapeXPathString(element.getAttribute(attr))}`)
                    .join(' and ');
                return `${element.tagName.toLowerCase()}[${conditions}]`;
            }
        
            // If no unique identification is found, return null or proceed to other identification methods
            return null;
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

        const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind', 'ng-click', 'placeholder'];
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

        if (element.tagName.toLowerCase() !== 'i' && element.childNodes.length > 0) {
            for (let child of element.childNodes) {
                if (child.nodeType === Node.TEXT_NODE) {
                    let text = child.textContent.trim();
                    if (text) {
                        let xpath = `//${element.tagName.toLowerCase()}[text()[contains(., ${escapeXPathString(text)})]]`;
                        if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                            return xpath;
                        }
                    }
                }
            }
        }

        return generateRelativeXPath(element);
        }

}