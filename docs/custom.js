// Custom JavaScript for GitCord documentation

(function() {
    'use strict';

    // Add copy button to code blocks
    function addCopyButtons() {
        const codeBlocks = document.querySelectorAll('pre code');
        
        codeBlocks.forEach((block, index) => {
            const button = document.createElement('button');
            button.className = 'copy-btn';
            button.textContent = 'Copy';
            button.style.cssText = `
                position: absolute;
                top: 8px;
                right: 8px;
                background: #5865f2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                cursor: pointer;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            
            const pre = block.parentElement;
            pre.style.position = 'relative';
            
            pre.addEventListener('mouseenter', () => {
                button.style.opacity = '1';
            });
            
            pre.addEventListener('mouseleave', () => {
                button.style.opacity = '0';
            });
            
            button.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(block.textContent);
                    button.textContent = 'Copied!';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                    button.textContent = 'Failed';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000);
                }
            });
            
            pre.appendChild(button);
        });
    }

    // Add syntax highlighting for YAML
    function highlightYAML() {
        const yamlBlocks = document.querySelectorAll('pre code.language-yaml, pre code.language-yml');
        
        yamlBlocks.forEach(block => {
            const text = block.textContent;
            const highlighted = text
                .replace(/(\w+):/g, '<span class="hljs-keyword">$1</span>:')
                .replace(/(\d+)/g, '<span class="hljs-number">$1</span>')
                .replace(/"([^"]*)"/g, '<span class="hljs-string">"$1"</span>')
                .replace(/'([^']*)'/g, '<span class="hljs-string">\'$1\'</span>');
            
            block.innerHTML = highlighted;
        });
    }

    // Add search functionality
    function addSearch() {
        const searchBox = document.createElement('div');
        searchBox.innerHTML = `
            <div style="margin: 20px 0; padding: 16px; background: #f8f9fa; border-radius: 6px;">
                <input type="text" id="search-input" placeholder="Search documentation..." 
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                <div id="search-results" style="margin-top: 10px;"></div>
            </div>
        `;
        
        const content = document.querySelector('.markdown');
        if (content) {
            content.insertBefore(searchBox, content.firstChild);
            
            const searchInput = document.getElementById('search-input');
            const resultsDiv = document.getElementById('search-results');
            
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                if (query.length < 2) {
                    resultsDiv.innerHTML = '';
                    return;
                }
                
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                const results = [];
                
                headings.forEach(heading => {
                    const text = heading.textContent.toLowerCase();
                    if (text.includes(query)) {
                        results.push({
                            text: heading.textContent,
                            level: parseInt(heading.tagName.charAt(1)),
                            element: heading
                        });
                    }
                });
                
                if (results.length > 0) {
                    resultsDiv.innerHTML = `
                        <h4>Search Results:</h4>
                        <ul style="list-style: none; padding: 0;">
                            ${results.slice(0, 5).map(result => `
                                <li style="margin: 4px 0;">
                                    <a href="#${result.element.id}" style="color: #5865f2; text-decoration: none;">
                                        ${'&nbsp;'.repeat((result.level - 1) * 4)}${result.text}
                                    </a>
                                </li>
                            `).join('')}
                        </ul>
                    `;
                } else {
                    resultsDiv.innerHTML = '<p style="color: #666;">No results found.</p>';
                }
            });
        }
    }

    // Add table of contents
    function addTableOfContents() {
        const headings = document.querySelectorAll('h1, h2, h3');
        if (headings.length < 3) return;
        
        const toc = document.createElement('div');
        toc.innerHTML = `
            <div style="margin: 20px 0; padding: 16px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #5865f2;">
                <h3 style="margin-top: 0;">Table of Contents</h3>
                <ul id="toc-list" style="list-style: none; padding: 0;"></ul>
            </div>
        `;
        
        const content = document.querySelector('.markdown');
        if (content) {
            content.insertBefore(toc, content.firstChild);
            
            const tocList = document.getElementById('toc-list');
            
            headings.forEach((heading, index) => {
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }
                
                const li = document.createElement('li');
                const indent = (parseInt(heading.tagName.charAt(1)) - 1) * 20;
                li.style.marginLeft = `${indent}px`;
                li.style.marginBottom = '4px';
                
                const link = document.createElement('a');
                link.href = `#${heading.id}`;
                link.textContent = heading.textContent;
                link.style.color = '#5865f2';
                link.style.textDecoration = 'none';
                
                li.appendChild(link);
                tocList.appendChild(li);
            });
        }
    }

    // Add dark mode toggle
    function addDarkModeToggle() {
        const toggle = document.createElement('button');
        toggle.innerHTML = '🌙';
        toggle.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #5865f2;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            z-index: 1000;
            font-size: 16px;
        `;
        
        document.body.appendChild(toggle);
        
        let isDark = localStorage.getItem('darkMode') === 'true';
        if (isDark) {
            document.body.classList.add('dark-mode');
            toggle.innerHTML = '☀️';
        }
        
        toggle.addEventListener('click', () => {
            isDark = !isDark;
            document.body.classList.toggle('dark-mode', isDark);
            toggle.innerHTML = isDark ? '☀️' : '🌙';
            localStorage.setItem('darkMode', isDark);
        });
    }

    // Add dark mode styles
    function addDarkModeStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .dark-mode {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            .dark-mode .markdown {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            .dark-mode .book-summary {
                background-color: #2d2d2d !important;
                color: #ffffff !important;
            }
            
            .dark-mode pre {
                background-color: #2d2d2d !important;
                color: #ffffff !important;
            }
            
            .dark-mode code {
                background-color: #2d2d2d !important;
                color: #ff6b6b !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize all features
    function init() {
        console.log('GitCord documentation loaded');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        addCopyButtons();
        highlightYAML();
        addSearch();
        addTableOfContents();
        addDarkModeStyles();
        addDarkModeToggle();
        
        // Add smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Start initialization
    init();
})(); 