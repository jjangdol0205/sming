const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname);
const blogDir = path.join(__dirname, 'blog');
const baseUrl = 'https://paradise-hero.com';

function processHtmlFile(filePath, relativeUrl) {
    let content = fs.readFileSync(filePath, 'utf8');

    // Remove existing SEO block if present
    const seoStart = '<!-- SEO Meta Tags -->';
    let seoStartIdx = content.indexOf(seoStart);
    
    // Some older files might simply have `<meta name="description"` directly inside. We will just use the comment marker.
    // Loop in case of multiple blocks
    while (seoStartIdx !== -1) {
        const twitterImage = '<meta property="twitter:image" content="https://paradise-hero.com/assets/og-image.jpg">';
        const seoEndIdx = content.indexOf(twitterImage, seoStartIdx);
        if (seoEndIdx !== -1) {
            content = content.slice(0, seoStartIdx) + content.slice(seoEndIdx + twitterImage.length).replace(/^\s+/, '\n');
        } else {
            // fallback, cut until just before </head>
            const headEnd = content.indexOf('</head>', seoStartIdx);
            if (headEnd !== -1) {
                content = content.slice(0, seoStartIdx) + content.slice(headEnd).replace(/^\s+/, '\n');
            } else {
                break;
            }
        }
        seoStartIdx = content.indexOf(seoStart);
    }

    // Extract title
    const titleMatch = content.match(/<title>(.*?)<\/title>\s*/i);
    const title = titleMatch ? titleMatch[1] : '김쌤과 함께하는 파라다이스 매일 응원방';

    // Description
    let description = '황영웅 가수님을 위한 파라다이스 매일 응원방 및 시니어 꿀팁 블로그입니다. 시니어를 위한 유용한 정보와 건강 꿀팁을 확인하세요.';
    
    // For blog posts, extract the first paragraph text
    if (relativeUrl.startsWith('/blog/')) {
        const pMatch = content.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
        if (pMatch && pMatch[1]) {
            let text = pMatch[1].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
            if (text.length > 0) {
                if (text.length > 150) {
                    text = text.substring(0, 150) + '...';
                }
                // Escape quotes
                text = text.replace(/"/g, '&quot;');
                description = text;
            }
        }
    }

    // Construct Canonical URL
    const canonicalUrl = relativeUrl === '/index.html' ? baseUrl + '/' : baseUrl + relativeUrl;

    const seoTags = `
    <!-- SEO Meta Tags -->
    <meta name="description" content="${description}">
    <link rel="canonical" href="${canonicalUrl}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="${canonicalUrl}">
    <meta property="og:title" content="${title}">
    <meta property="og:description" content="${description}">
    <meta property="og:image" content="${baseUrl}/assets/og-image.jpg">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="${canonicalUrl}">
    <meta property="twitter:title" content="${title}">
    <meta property="twitter:description" content="${description}">
    <meta property="twitter:image" content="${baseUrl}/assets/og-image.jpg">
`;

    if (content.includes('</head>')) {
        content = content.replace('</head>', seoTags.trimEnd() + '\n</head>');
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`Processed: ${relativeUrl} (${description.slice(0, 30)}...)`);
    } else {
        console.error(`Could not find </head> in ${relativeUrl}`);
    }
}

// 1. Process base files
const baseFiles = fs.readdirSync(baseDir);
baseFiles.forEach(file => {
    if (file.endsWith('.html')) {
        const filePath = path.join(baseDir, file);
        processHtmlFile(filePath, `/${file}`);
    }
});

// 2. Process blog files
if (fs.existsSync(blogDir)) {
    const blogFiles = fs.readdirSync(blogDir);
    blogFiles.forEach(file => {
        if (file.endsWith('.html')) {
            const filePath = path.join(blogDir, file);
            processHtmlFile(filePath, `/blog/${file}`);
        }
    });
}

console.log('SEO tags generation complete.');
