import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import SearchPipeline from './pages/SearchPipeline';
import ForensicChatbot from './pages/ForensicChatbot';
import CCTVPlayer from './pages/CCTVPlayer';
import CaseLogs from './pages/CaseLogs';
import About from './pages/About';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        {/* Scan line effect */}
        <div className="scan-line" />

        <Sidebar />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pipeline" element={<SearchPipeline />} />
            <Route path="/chatbot" element={<ForensicChatbot />} />
            <Route path="/player" element={<CCTVPlayer />} />
            <Route path="/cases" element={<CaseLogs />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
