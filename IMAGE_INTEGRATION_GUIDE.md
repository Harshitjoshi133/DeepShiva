# 🖼️ Image Integration Guide

## 📍 Where to Add Images in Code

### 1. **Update Product Images**

**File:** `server/app/routers/culture.py`

**Current (lines 25-65):**
```python
"image": "https://placehold.co/400x400/FF9933/FFFFFF?text=Aipan+Art"
```

**Replace with:**
```python
"image": "/images/products/aipan-art.jpg"
```

**All 5 products need real image URLs:**
- Aipan Art → `/images/products/aipan-art.jpg`
- Woolen Shawl → `/images/products/woolen-shawl.jpg`
- Ringal Basket → `/images/products/ringal-basket.jpg`
- Copper Bottle → `/images/products/copper-bottle.jpg`
- Himalayan Honey → `/images/products/himalayan-honey.jpg`

### 2. **Add Logo to Header**

**File:** `client/src/components/Layout.jsx`

**Current (line 45):**
```jsx
<h1 className="text-2xl font-bold gradient-text">Deep-Shiva</h1>
```

**Replace with:**
```jsx
<div className="flex items-center gap-2">
  <img src="/images/branding/logo.svg" alt="Deep-Shiva" className="h-8 w-8" />
  <h1 className="text-2xl font-bold gradient-text">Deep-Shiva</h1>
</div>
```

### 3. **Add Hero Background**

**File:** `client/src/pages/Home.jsx`

**Add after opening div:**
```jsx
<div className="max-w-6xl mx-auto relative">
  {/* Hero Background */}
  <div className="absolute inset-0 -z-10">
    <img 
      src="/images/hero/hero-bg.jpg" 
      alt="Uttarakhand Mountains" 
      className="w-full h-full object-cover opacity-20 rounded-2xl"
    />
  </div>
  
  {/* Existing content */}
```

### 4. **Add Shrine Images to Dashboard**

**File:** `client/src/pages/Dashboard.jsx`

**Add shrine images in the status cards section:**
```jsx
{crowdData.map((shrine) => (
  <div key={shrine.shrine} className="text-center p-3 bg-gray-50 rounded-lg relative overflow-hidden">
    <img 
      src={`/images/shrines/${shrine.shrine.toLowerCase()}.jpg`}
      alt={shrine.shrine}
      className="absolute inset-0 w-full h-full object-cover opacity-30"
    />
    <div className="relative z-10">
      <p className="font-semibold text-gray-800">{shrine.shrine}</p>
      <p className={`text-sm font-bold ${
        shrine.status === 'Light' ? 'text-green-600' :
        shrine.status === 'Moderate' ? 'text-orange-600' :
        'text-red-600'
      }`}>
        {shrine.status}
      </p>
    </div>
  </div>
))}
```

### 5. **Add Yoga Pose Overlays**

**File:** `client/src/pages/YogaSentinel.jsx`

**Replace the SVG skeleton overlay (lines 65-72) with:**
```jsx
{/* Pose Guide Overlay */}
<div className="absolute inset-0 flex items-center justify-center pointer-events-none">
  <img 
    src="/images/yoga/warrior-pose.svg" 
    alt="Warrior Pose Guide" 
    className="h-4/5 opacity-30"
  />
</div>
```

### 6. **Add Favicon**

**File:** `client/index.html`

**Replace (line 4):**
```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
```

**With:**
```html
<link rel="icon" type="image/x-icon" href="/images/branding/favicon.ico" />
<link rel="icon" type="image/svg+xml" href="/images/branding/logo.svg" />
```

### 7. **Add Cultural Decorations**

**File:** `client/src/pages/Home.jsx`

**Add decorative elements:**
```jsx
{/* Decorative Om Symbol */}
<div className="absolute top-10 right-10 opacity-10">
  <img src="/images/cultural/om-symbol.svg" alt="" className="h-20 w-20" />
</div>

{/* Decorative Lotus */}
<div className="absolute bottom-10 left-10 opacity-10">
  <img src="/images/cultural/lotus.svg" alt="" className="h-16 w-16" />
</div>
```

## 🔧 Quick Implementation Script

Create this file to quickly update all image paths:

**File:** `update-images.js`
```javascript
// Run this after adding images to public/images/
const fs = require('fs');

// Update culture.py
const cultureFile = 'server/app/routers/culture.py';
let cultureContent = fs.readFileSync(cultureFile, 'utf8');

const imageMap = {
  'Aipan+Art': 'aipan-art.jpg',
  'Woolen+Shawl': 'woolen-shawl.jpg', 
  'Ringal+Basket': 'ringal-basket.jpg',
  'Copper+Bottle': 'copper-bottle.jpg',
  'Honey': 'himalayan-honey.jpg'
};

Object.entries(imageMap).forEach(([placeholder, filename]) => {
  cultureContent = cultureContent.replace(
    new RegExp(`https://placehold\\.co/400x400/[^"]*${placeholder}[^"]*`, 'g'),
    `/images/products/${filename}`
  );
});

fs.writeFileSync(cultureFile, cultureContent);
console.log('✅ Updated product images');
```

## 📂 File Placement

**Place images in:** `client/public/images/`

The `public` folder is served directly by Vite, so:
- `client/public/images/logo.svg` → accessible as `/images/logo.svg`
- `client/public/images/products/aipan-art.jpg` → accessible as `/images/products/aipan-art.jpg`

## 🎯 Priority Implementation Order

### Phase 1: Essential (Do First)
1. **Logo** - Replace text logo with image
2. **Product Images** - Replace placeholder URLs
3. **Favicon** - Professional browser tab icon

### Phase 2: Visual Impact
4. **Hero Background** - Stunning mountain backdrop
5. **Shrine Images** - Dashboard visual enhancement

### Phase 3: Polish
6. **Yoga Guides** - Functional pose overlays
7. **Cultural Decorations** - Subtle spiritual elements
8. **Patterns** - Background textures

## 🔍 Testing Checklist

After adding images:
- [ ] All images load without 404 errors
- [ ] Images are properly sized and optimized
- [ ] Alt text is descriptive and helpful
- [ ] Images work on mobile devices
- [ ] Loading performance is acceptable
- [ ] Images respect cultural sensitivity

## 📱 Responsive Image Implementation

For better performance, consider responsive images:

```jsx
<img 
  src="/images/hero/hero-bg.jpg"
  srcSet="/images/hero/hero-bg-480.jpg 480w,
          /images/hero/hero-bg-800.jpg 800w,
          /images/hero/hero-bg-1200.jpg 1200w"
  sizes="(max-width: 480px) 480px,
         (max-width: 800px) 800px,
         1200px"
  alt="Uttarakhand Mountains"
  className="w-full h-full object-cover"
/>
```

---

**Once you have the images, follow this guide to integrate them systematically into the application!**