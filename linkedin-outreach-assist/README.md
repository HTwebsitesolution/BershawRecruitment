# LinkedIn Outreach Assist

Chrome extension that generates personalised connection notes and JD follow-ups, then inserts them into LinkedIn composers.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build for production:
```bash
npm run build
```

3. Load the extension in Chrome:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `linkedin-outreach-assist` folder

## Development

Run the development server:
```bash
npm run dev
```

Note: For Chrome extension development, you'll typically build and reload the extension after making changes.

## Project Structure

```
linkedin-outreach-assist/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── manifest.json
├── public/
│   └── icon128.png (add your icon here)
└── src/
    ├── contentScript.tsx
    ├── lib/
    │   └── linkedinComposer.ts
    └── ui/
        ├── DraftButton.tsx
        └── panel.css
```

## Features

- **Draft Suggestions**: Generates multiple personalised outreach note templates
- **LinkedIn Integration**: Automatically detects and inserts text into LinkedIn composers
- **Shadow DOM**: Uses Shadow DOM to avoid CSS conflicts with LinkedIn's styles
- **React UI**: Modern React-based interface with suggestion panel

## Customization

To integrate with your backend API for personalized drafts, update the `refresh()` function in `src/ui/DraftButton.tsx` to call your API endpoint.

