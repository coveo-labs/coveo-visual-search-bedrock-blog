# Luxury Image Search UI

Modern, luxury-themed React application for reverse image search.

## Features

- Drag & drop image upload
- Real-time search with loading states
- Luxury design with gold accents
- OpenSearch debug log viewer
- Responsive design
- Smooth animations with Framer Motion

## Tech Stack

- React 18
- Vite
- TailwindCSS
- Framer Motion
- Axios

## Development

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your API endpoint

# Start development server
npm run dev
```

## Build

```bash
npm run build
```

## Deploy to Netlify

### Option 1: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod
```

### Option 2: Netlify UI

1. Push code to GitHub
2. Go to Netlify dashboard
3. Click "New site from Git"
4. Select your repository
5. Build settings are auto-detected from netlify.toml
6. Add environment variables in Netlify UI:
   - VITE_API_URL
   - VITE_ENABLE_ANALYTICS
7. Deploy!

### Option 3: Drag & Drop

1. Run `npm run build`
2. Go to Netlify dashboard
3. Drag the `dist` folder to deploy

## Environment Variables

### Local Development

Create a `.env` file in the `ui/` directory:

```env
VITE_API_URL=https://your-api-gateway-url.com/prod
VITE_ENABLE_ANALYTICS=true
```

**Quick setup:**
```bash
# Windows
setup-env.bat

# Or manually
cp .env.example .env
# Then edit .env with your API Gateway URL
```

### Netlify Deployment

Environment variables for Netlify are configured in **two places**:

#### 1. Local .env (for building)

Create `ui/.env` before deploying:
```env
VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
VITE_ENABLE_ANALYTICS=true
```

#### 2. Netlify Dashboard (recommended for production)

After deploying, add variables in Netlify:
1. Go to your site in [Netlify Dashboard](https://app.netlify.com/)
2. Navigate to **Site settings** → **Environment variables**
3. Add these variables:
   - `VITE_API_URL` = Your API Gateway URL
   - `VITE_ENABLE_ANALYTICS` = `true`
4. Trigger a new deployment

**Note:** Variables in Netlify dashboard override local `.env` file.

## Customization

### Colors

Edit `tailwind.config.js` to customize the luxury color palette:

```js
colors: {
  luxury: {
    gold: '#D4AF37',
    darkGold: '#B8941F',
    cream: '#F5F5DC',
    charcoal: '#2C2C2C',
    black: '#0A0A0A',
    white: '#FAFAFA'
  }
}
```

### Fonts

The app uses:
- Playfair Display (serif, headings)
- Inter (sans-serif, body)

Change in `index.html` and `tailwind.config.js`.
