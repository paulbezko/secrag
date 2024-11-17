const { createWriteStream } = require('fs');
const { SitemapStream } = require('sitemap');
const routes = [
  '/', 
  '/home', 
  '/preview', 
  '/terms-and-conditions', 
  '/login', 
  '/signup', 
  '/handle-supabase', 
  '/reset-password', 
  '/subscribe', 
  '/dashboard', 
  '/change-email'
];

const dynamicRoutes = [
  // Add any dynamic routes here if needed, e.g., `/blog/:id`
];

const hostname = 'https://secrag.com'; // Replace with your website's URL

const generateSitemap = () => {
  const sitemap = new SitemapStream({ hostname });
  const writeStream = createWriteStream('./public/sitemap.xml');
  sitemap.pipe(writeStream);

  // Add static routes
  routes.forEach((route) => {
    sitemap.write({ url: route, changefreq: 'daily', priority: 0.8 });
  });

  // Add dynamic routes if any
  dynamicRoutes.forEach((route) => {
    sitemap.write({ url: route, changefreq: 'weekly', priority: 0.7 });
  });

  sitemap.end();
  console.log('Sitemap successfully created!');
};

generateSitemap();