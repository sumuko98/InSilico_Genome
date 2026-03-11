# CV Editor

A React-based CV / résumé editor with a live preview, built with Vite.

## Features

- **Tabbed editor** – edit Personal Info, Work Experience, Education, and Skills in separate tabs
- **Live preview** – see a formatted CV document update in real time as you type
- **Add / remove entries** – dynamically manage multiple experience, education, and skill entries

## Tech Stack

| Tool | Purpose |
|------|---------|
| [React 19](https://react.dev) | UI framework |
| [Vite 7](https://vite.dev) | Dev server & build tool |
| ESLint | Code quality |

## Getting Started

```bash
# 1. Enter the project directory
cd cv-editor

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

Then open http://localhost:5173 in your browser.

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint |

## Project Structure

```
cv-editor/
├── public/
├── src/
│   ├── components/
│   │   ├── PersonalInfo.jsx   # Personal info form section
│   │   ├── Experience.jsx     # Work experience entries
│   │   ├── Education.jsx      # Education entries
│   │   ├── Skills.jsx         # Skills list
│   │   └── CVPreview.jsx      # Live CV document preview
│   ├── App.jsx                # Root component with state & layout
│   ├── App.css                # Application styles
│   ├── index.css              # Global resets
│   └── main.jsx               # Entry point
├── index.html
├── vite.config.js
└── package.json
```

