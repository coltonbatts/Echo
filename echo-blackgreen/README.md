# Echo Black-Green Terminal Chat

![version](https://img.shields.io/badge/version-0.1-green)

---

**Version 0.1 – June 18, 2025**
- 🟢 First working checkpoint: Docker + backend + React dev server + chat proxy integration
- ✅ All smoke tests passing (backend, frontend, chat API, OpenAI relay)
- See below for setup and usage steps.

---

This project includes a retro, green-on-black terminal-style chat interface built in React. The chat pane lives in the center of a Linux tiling window manager-inspired grid layout and communicates with a backend (via `/api/echo`) to provide ChatGPT-powered conversations.

## Features
- **Old-school terminal look:** Green monospaced text on black, minimal chrome, blinking cursor, and typewriter effect.
- **Self-contained React component:** All chat logic is in `src/ChatBox.jsx`.
- **API integration:** Connects to your backend, which should proxy requests to OpenAI's API.
- **Easy integration:** Just drop `<ChatBox />` into your layout (see `BlackGreenMockup.jsx`).

## Setup
1. **Install dependencies:**
   ```bash
   npm install
   ```
2. **Configure your backend:**
   - Ensure your backend exposes a POST `/api/echo` endpoint that relays messages to OpenAI's API.
   - The backend should read your OpenAI API key from an environment variable (see below).

3. **.env file:**
   Create a `.env` file in your backend directory (not this React app) and add:
   ```
   OPENAI_API_KEY=sk-...
   ```
   (Replace with your actual OpenAI API key.)

4. **Run the React app:**
   ```bash
   npm start
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the app.

---

## v0.1 Changelog
- Initial working integration of backend (FastAPI), frontend (Nginx), and React dev chat app.
- ChatBox now proxies `/api/echo` to backend via `src/setupProxy.js`.
- All containers and dev tools run via Docker Compose and `npm start`.
- All smoke tests pass: backend health, frontend loads, chat API connects, OpenAI relay works.

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
