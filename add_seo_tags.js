const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname);
const blogDir = path.join(__dirname, 'blog');
const baseUrl = 'https://paradise-hero.com';

function processHtmlFile(filePath, relativeUrl) {
    let content = fs.readFileSync(filePath, 'utf8');

    // Skip if already has SEO tags (rudimentary check)
    if (content.includes('rel="canonical"') && content.includes('og:title')) {
        console.log(`Skipping (already processed): ${relativeUrl}`);
        return;
    }

    // Extract title
    const titleMatch = content.match(/<title>(.*?)<\/title>\s*/i);
    const title = titleMatch ? titleMatch[1] : '김쌤과 함께하는 파라다이스 매일 응원방';

    // Description
    const defaultDesc = '황영웅 가수님을 위한 파라다이스 매일 응원방 및 시니어 꿀팁 블로그입니다. 시니어를 위한 유용한 정보와 건강 꿀팁을 확인하세요.';
    let description = defaultDesc;

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
    <meta property="og:image" content="${baseUrl}/assets/og-image.jpg"> <!-- Ensure an image exists or adjust -->

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="${canonicalUrl}">
    <meta property="twitter:title" content="${title}">
    <meta property="twitter:description" content="${description}">
    <meta property="twitter:image" content="${baseUrl}/assets/og-image.jpg">
`;

    // Inject before closing </head> or after <meta name="viewport" ...>
    if (content.includes('</head>')) {
        content = content.replace('</head>', seoTags + '</head>');
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`Processed: ${relativeUrl}`);
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
