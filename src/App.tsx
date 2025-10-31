import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './components/Landing';
import RequestPage from './pages/RequestPage';
import ResponsePage from './pages/ResponsePage';
import SuccessPage from './pages/SuccessPage';
import Dashboard from './pages/Dashboard';
import { initializeAnalytics } from './analytics';

function App() {
  useEffect(() => {
    // Initialize analytics platforms (GA4, Mixpanel, Amplitude)
    initializeAnalytics();
    console.log('📊 Feedback360 - Ready');
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/request" element={<RequestPage />} />
        <Route path="/respond" element={<ResponsePage />} />
        <Route path="/success" element={<SuccessPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
