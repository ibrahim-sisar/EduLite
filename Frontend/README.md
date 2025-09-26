
# 🎨 EduLite Frontend


The EduLite frontend is a responsive interface that focuses on speed, clarity, and simplicity to make essential features easily accessible — such as courses , classes .It also supports multiple languages for ease and supports dark mode. The design avoids distractions to support a clear and smooth learning experience.


## 🛠️ Tech Stack

- **TypeScript** - Type-safe JavaScript with enhanced IDE support
- **React 19** - Latest React with improved performance
- **Tailwind CSS v4** - Utility-first CSS framework
- **Vite** - Lightning-fast build tool and dev server
- **React Router v7** - Client-side routing
- **i18next** - Internationalization support

## 🗂️ Project Structure

```
Frontend/
├── EduLiteFrontend/
│   ├── node_modules/
│   ├── public/
│   │   └── vite.svg    # EduLite logo
│   ├── src/
│   │   ├── assets/     # Images, logos, etc.
│   │   │   ├── heroimg.png
│   │   │   └── EduTech_Logo.webp
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx  ✅ (TypeScript)
│   │   │   │   └── Input.tsx   ✅ (TypeScript)
│   │   │   ├── DarkModeToggle.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── LanguageSwitcher.jsx
│   │   │   └── Sidebar.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Notifications.jsx
│   │   │   ├── LogInandLogOut.jsx
│   │   │   └── Chats.jsx
│   │   │
│   │   ├── i18n/
│   │   │   ├── locals/
│   │   │   │   ├── ar.json
│   │   │   │   └── en.json
│   │   │   └── index.js
│   │   │
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json      # TypeScript config
│   ├── tsconfig.node.json  # TypeScript Node config
│   └── vite.config.js
└── README.md
```
## 🚀 Getting Started

```bash
cd Frontend/EduLiteFrontend
npm install
npm run dev
```

## 📦 Available Scripts

| Script | Command | Description |
| ------ | ------- | ----------- |
| `dev` | `npm run dev` | Start development server |
| `build` | `npm run build` | Build for production |
| `preview` | `npm run preview` | Preview production build |
| `lint` | `npm run lint` | Run ESLint |
| `type-check` | `npm run type-check` | Check TypeScript types |

## ⚙️ TypeScript Configuration

- **Strict Mode**: Full type safety enabled
- **Path Aliases**: `@/*` maps to `src/*`
- **Target**: ES2020 with modern browser support
- **JSX**: React 19 automatic runtime

## 🗺️ Available Pages & Routing

these routs are defined in `src/App.jsx` using `react-router-dom` library.

| Path      | Component    | Description                                                |
| --------- | ------------ | ---------------------------------------------------------- |
| `/`       | `Home`       | The main landing page.                                     |
| `/login`  | `LoginPage`  | Allows users to sign in.                                   |
| `/signup` | `SignUpPage` | Allows new users to register.                              |
| `/about`  | `AboutPage`  | This page provides an overview of the project, it's goals. |

## ✨ Component Showcase

### TypeScript Components (Migrated)

| Component | Type | Description | Props |
| --------- | ---- | ----------- | ----- |
| `Button` | `.tsx` | Versatile button with multiple styles | `type`, `size`, `width`, `disabled` |
| `Input` | `.tsx` | Apple-style glass-morphism input | `label`, `error`, `compact`, `required` |

### JavaScript Components (To be migrated)

| Component | Status | Description |
| --------- | ------ | ----------- |
| `Navbar` | `.jsx` | Navigation bar component |
| `Sidebar` | `.jsx` | Collapsible sidebar |
| `DarkModeToggle` | `.jsx` | Theme switcher |
| `LanguageSwitcher` | `.jsx` | i18n language selector |
