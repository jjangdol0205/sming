const fs = require('fs');
const path = require('path');

const baseUrl = 'https://paradise-hero.com';
const blogDir = path.join(__dirname, 'blog');
const sitemapPath = path.join(__dirname, 'sitemap.xml');
const rssPath = path.join(__dirname, 'rss.xml');

// 1. Base files
const urls = [
    { url: '/', priority: '1.00' },
    { url: '/index.html', priority: '0.80' },
    { url: '/blog_list.html', priority: '0.80' },
    { url: '/privacy.html', priority: '0.50' },
    { url: '/privacy-policy.html', priority: '0.50' },
    { url: '/terms-of-service.html', priority: '0.50' },
    { url: '/battery.html', priority: '0.80' },
    { url: '/lutein.html', priority: '0.80' },
    { url: '/kakaotalk.html', priority: '0.80' },
    { url: '/smishing.html', priority: '0.80' }
];

// 2. Read all blog posts
const files = fs.readdirSync(blogDir);
files.forEach(file => {
    if (file.endsWith('.html')) {
        urls.push({
            url: `/blog/${file}`,
            priority: '0.90' // High priority for content
        });
    }
});

const today = new Date().toISOString().split('T')[0] + 'T00:00:00+00:00';

// 3. Generate Sitemap XML
let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

urls.forEach(u => {
    sitemapXml += `  <url>
    <loc>${baseUrl}${u.url}</loc>
    <lastmod>${today}</lastmod>
    <priority>${u.priority}</priority>
  </url>\n`;
});
sitemapXml += `</urlset>`;

fs.writeFileSync(sitemapPath, sitemapXml);

// 4. Generate RSS XML (basic implementation)
let rssXml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>김쌤과 함께하는 파라다이스 매일 응원방</title>
    <link>${baseUrl}/</link>
    <description>황영웅 가수님을 위한 파라다이스 매일 응원방 및 시니어 꿀팁 블로그</description>
    <atom:link href="${baseUrl}/rss.xml" rel="self" type="application/rss+xml" />
    <language>ko</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>\n\n`;

urls.forEach(u => {
    rssXml += `    <item>
      <title>${u.url.replace('/', '').replace('.html', '') || '홈'}</title>
      <link>${baseUrl}${u.url}</link>
      <guid>${baseUrl}${u.url}</guid>
    </item>\n`;
});
rssXml += `  </channel>\n</rss>`;

fs.writeFileSync(rssPath, rssXml);

console.log(`Generated sitemap.xml with ${urls.length} URLs.`);
console.log(`Generated rss.xml with ${urls.length} items.`);
